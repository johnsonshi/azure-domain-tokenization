"""Corpus construction: extract, normalize, segment, dedupe, and build
byte-matched training corpora (plan.md §10-12).

Operates on in-memory document lists so it is unit-testable without downloads.
Raw + intermediate text stays under data/ (git-ignored); only manifests and
hashes are publishable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import dedup as dd
from . import markdown_extract as mx
from . import normalize as nz
from .provenance import atomic_write_json, sha256_text


@dataclass
class RawDoc:
    source_repo: str
    source_commit: str
    source_path: str
    license_id: str
    raw_bytes: bytes


@dataclass
class ProcessedDoc:
    document_id: str
    source_repo: str
    source_commit: str
    source_path: str
    license_id: str
    semantic_full: str
    prose_only: str
    technical_syntax: str
    utf8_bytes: int
    unicode_chars: int
    whitespace_words: int
    sha256: str
    content_type_counts: dict[str, int] = field(default_factory=dict)


def document_id(repo: str, path: str) -> str:
    return "sha256:" + sha256_text(f"{repo}|{path}")


def process_documents(raw_docs: list[RawDoc], report: nz.NormalizationReport | None = None) -> list[ProcessedDoc]:
    report = report or nz.NormalizationReport()
    out: list[ProcessedDoc] = []
    for rd in raw_docs:
        text, ok = nz.decode_utf8_strict(rd.raw_bytes)
        if not ok or text is None:
            report.malformed += 1
            continue
        normed = nz.normalize_document(text, report)
        if normed is None or not normed.strip():
            continue
        segs = mx.extract_segments(normed)
        semantic = mx.to_representation(segs, "semantic_full")
        prose = mx.to_representation(segs, "prose_only")
        tech = mx.to_representation(segs, "technical_syntax")
        if not semantic.strip():
            continue
        b, c, w = nz.count_metrics(semantic)
        ctcounts: dict[str, int] = {}
        for s in segs:
            ctcounts[s.content_type] = ctcounts.get(s.content_type, 0) + 1
        out.append(ProcessedDoc(
            document_id=document_id(rd.source_repo, rd.source_path),
            source_repo=rd.source_repo,
            source_commit=rd.source_commit,
            source_path=rd.source_path,
            license_id=rd.license_id,
            semantic_full=semantic,
            prose_only=prose,
            technical_syntax=tech,
            utf8_bytes=b,
            unicode_chars=c,
            whitespace_words=w,
            sha256=dd.exact_hash(semantic),
            content_type_counts=ctcounts,
        ))
    return out


def segments_dataframe(raw_docs: list[RawDoc]) -> pd.DataFrame:
    """One row per segment with full provenance (schema in plan.md §10)."""
    rows = []
    for rd in raw_docs:
        text, ok = nz.decode_utf8_strict(rd.raw_bytes)
        if not ok or text is None:
            continue
        normed = nz.nfc(text)
        doc_id = document_id(rd.source_repo, rd.source_path)
        segs = mx.extract_segments(normed)
        for i, s in enumerate(segs):
            b, c, w = nz.count_metrics(s.text)
            rows.append({
                "source_repo": rd.source_repo,
                "source_commit": rd.source_commit,
                "source_path": rd.source_path,
                "document_id": doc_id,
                "segment_id": f"{doc_id}#{i}",
                "content_type": s.content_type,
                "language": "en",
                "utf8_bytes": b,
                "unicode_chars": c,
                "whitespace_words": w,
                "sha256": sha256_text(s.text),
                "split": "unassigned",
                "license_id": rd.license_id,
                "classifier_rule": s.classifier_rule,
                "classifier_confidence": s.confidence,
            })
    return pd.DataFrame(rows)


def exact_dedup(docs: list[ProcessedDoc]) -> tuple[list[ProcessedDoc], dict]:
    """Remove exact duplicates (by semantic-full hash), keeping the first."""
    seen: set[str] = set()
    kept: list[ProcessedDoc] = []
    removed = 0
    for d in docs:
        if d.sha256 in seen:
            removed += 1
            continue
        seen.add(d.sha256)
        kept.append(d)
    return kept, {"input": len(docs), "kept": len(kept), "removed_exact": removed}


def near_dedup_clusters(docs: list[ProcessedDoc], threshold: float = 0.8) -> dd.NearDupResult:
    items = [(d.document_id, d.semantic_full) for d in docs]
    return dd.find_near_duplicates(items, threshold=threshold)


def near_dedup(docs: list[ProcessedDoc], threshold: float = 0.8) -> tuple[list[ProcessedDoc], dd.NearDupResult, dict]:
    """Remove near-duplicates, keeping one representative per cluster (plan.md §11).

    Keeping a single representative both cleans the corpus and prevents genuine
    cross-service near-duplicates (e.g. Azure's auto-generated per-service policy
    pages) from bridging otherwise-independent services in the split.
    """
    near = near_dedup_clusters(docs, threshold)
    by_cluster: dict[int, list[ProcessedDoc]] = {}
    for d in docs:
        by_cluster.setdefault(near.clusters.get(d.document_id, -1), []).append(d)
    kept: list[ProcessedDoc] = []
    removed = 0
    for group in by_cluster.values():
        group_sorted = sorted(group, key=lambda d: d.document_id)
        kept.append(group_sorted[0])
        removed += len(group_sorted) - 1
    stats = {"input": len(docs), "kept": len(kept), "removed_near": removed, "threshold": threshold}
    return kept, near, stats


def build_corpus_file(texts: list[str], out_path: Path, separator: str = "\n\n") -> dict:
    """Write selected document texts to a single training corpus file."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content_bytes = sum(len(t.encode("utf-8")) for t in texts)
    blob = separator.join(texts) + "\n"
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(blob, encoding="utf-8")
    tmp.replace(out_path)
    return {
        "path": str(out_path),
        "n_documents": len(texts),
        "content_utf8_bytes": content_bytes,
        "file_utf8_bytes": out_path.stat().st_size,
        "sha256": sha256_text(blob),
    }


def write_corpus_manifest(name: str, info: dict, extra: dict, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    payload = {"corpus": name, **info, **extra}
    path = out_dir / f"{name}.corpus.json"
    atomic_write_json(path, payload)
    return path
