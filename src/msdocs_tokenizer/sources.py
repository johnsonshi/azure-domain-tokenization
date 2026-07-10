"""Source-config-driven acquisition of raw documents (plan.md §7-9).

Three source roles:
- markdown repos (Azure anchor + MicrosoftDocs transfer + external technical):
  git blobless clone + cone sparse-checkout of selected paths, pinned to a commit.
- general_english: Wikipedia-derived text (wikitext-103-raw) fetched from the
  Hugging Face Hub as versioned parquet (no rendered-page crawling).

Returns in-memory RawDoc lists + SourceLock provenance. Raw text is cached under
data/raw/ (git-ignored).
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import yaml

from . import acquire, config
from .corpus import RawDoc
from .provenance import sha256_text
from .schemas import SourceLock


@dataclass
class SourceSpec:
    name: str
    role: str            # anchor | transfer | external_technical | general_english
    repo: str = ""       # owner/name for git/gh
    url: str = ""
    paths: list[str] = None  # sparse paths (markdown repos)
    license_id: str = "UNKNOWN"
    method: str = "git"  # git | gh_api | hf_parquet
    hf_repo: str = ""
    hf_files: list[str] = None
    max_docs: int = 0    # 0 = no cap

    def __post_init__(self):
        self.paths = self.paths or []
        self.hf_files = self.hf_files or []


def load_sources_config(path: str | Path) -> list[SourceSpec]:
    data = yaml.safe_load(Path(path).read_text())
    return [SourceSpec(**s) for s in data["sources"]]


# --------------------------------------------------------------------------- #
# Markdown-repo acquisition (git sparse checkout)
# --------------------------------------------------------------------------- #
def acquire_markdown_repo(spec: SourceSpec, dest_root: Path | None = None) -> tuple[list[RawDoc], SourceLock]:
    dest_root = dest_root or config.EXTERNAL
    dest = Path(dest_root) / spec.name
    url = spec.url or f"https://github.com/{spec.repo}.git"
    sha = acquire.clone_blobless(url, dest)
    if spec.paths:
        acquire.sparse_checkout(dest, spec.paths)
    md_paths = acquire.enumerate_markdown(dest, spec.paths or ["."])
    if spec.max_docs:
        md_paths = md_paths[: spec.max_docs]

    raw_docs: list[RawDoc] = []
    total_src = 0
    for p in md_paths:
        rel = str(p.relative_to(dest))
        data = p.read_bytes()
        total_src += len(data)
        raw_docs.append(RawDoc(
            source_repo=spec.repo or spec.name,
            source_commit=sha,
            source_path=rel,
            license_id=spec.license_id,
            raw_bytes=data,
        ))
    lock = SourceLock(
        repository=spec.repo or spec.name,
        url=url,
        commit_sha=sha,
        acquired_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        command=f"git clone --filter=blob:none --no-checkout {url}; sparse-checkout set {' '.join(spec.paths)}",
        sparse_paths=spec.paths,
        file_count=len(raw_docs),
        source_bytes=total_src,
        license_id=spec.license_id,
        notes=f"role={spec.role}",
    )
    return raw_docs, lock


# --------------------------------------------------------------------------- #
# General-English acquisition (Wikipedia-derived, HF Hub parquet)
# --------------------------------------------------------------------------- #
def acquire_general_english(spec: SourceSpec) -> tuple[list[RawDoc], SourceLock]:
    from huggingface_hub import hf_hub_download
    import pyarrow.parquet as pq

    cache = config.CACHE / "hf" / spec.name
    cache.mkdir(parents=True, exist_ok=True)
    raw_docs: list[RawDoc] = []
    total_src = 0
    revision = "main"
    files = spec.hf_files or ["wikitext-103-raw-v1/train-00000-of-00002.parquet"]
    for fname in files:
        local = hf_hub_download(repo_id=spec.hf_repo, filename=fname,
                                repo_type="dataset", revision=revision,
                                cache_dir=str(cache))
        table = pq.read_table(local, columns=["text"])
        texts = table.column("text").to_pylist()
        # wikitext rows are line-fragments; group into articles by ' = Title = ' headers
        articles = _group_wikitext(texts)
        for i, art in enumerate(articles):
            if not art.strip():
                continue
            data = art.encode("utf-8")
            total_src += len(data)
            raw_docs.append(RawDoc(
                source_repo=spec.hf_repo,
                source_commit=f"hf:{spec.hf_repo}@{revision}:{fname}",
                source_path=f"{fname}#article{i}",
                license_id=spec.license_id,
                raw_bytes=data,
            ))
            if spec.max_docs and len(raw_docs) >= spec.max_docs:
                break
        if spec.max_docs and len(raw_docs) >= spec.max_docs:
            break

    lock = SourceLock(
        repository=spec.hf_repo,
        url=f"https://huggingface.co/datasets/{spec.hf_repo}",
        commit_sha=f"hf:{revision}",
        acquired_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        command=f"hf_hub_download({spec.hf_repo}, {files}, repo_type=dataset)",
        sparse_paths=files,
        file_count=len(raw_docs),
        source_bytes=total_src,
        license_id=spec.license_id,
        notes=f"role={spec.role}; grouped wikitext articles",
    )
    return raw_docs, lock


def _group_wikitext(lines: list[str]) -> list[str]:
    """Group wikitext line-fragments into articles delimited by ' = Title = '."""
    articles: list[list[str]] = []
    current: list[str] = []
    for ln in lines:
        stripped = ln.strip()
        is_title = stripped.startswith("= ") and stripped.endswith(" =") and not stripped.startswith("= =")
        if is_title and current:
            articles.append(current)
            current = []
        current.append(ln)
    if current:
        articles.append(current)
    return ["".join(a) for a in articles]


def acquire_source(spec: SourceSpec) -> tuple[list[RawDoc], SourceLock]:
    if spec.role == "general_english" or spec.method == "hf_parquet":
        return acquire_general_english(spec)
    if spec.method == "gh_api":
        return acquire_via_api(spec)
    return acquire_markdown_repo(spec)


def acquire_via_api(spec: SourceSpec) -> tuple[list[RawDoc], SourceLock]:
    """Deterministically select + download up to max_docs markdown blobs via the
    GitHub API (used for eval-only sources to avoid large clones)."""
    sha = acquire.api_pinned_sha(spec.repo)
    prefix = spec.paths[0] if spec.paths else ""
    listing = acquire.api_list_markdown(spec.repo, sha, prefix=prefix)
    # Deterministic selection by hashed path
    listing.sort(key=lambda pb: sha256_text(f"{config.GLOBAL_SEED}|{pb[0]}"))
    if spec.max_docs:
        listing = listing[: spec.max_docs]
    cache = config.CACHE / "gh_blobs" / spec.name
    raw_docs: list[RawDoc] = []
    total_src = 0
    for path, blob_sha in listing:
        try:
            content = acquire.api_download_blob(spec.repo, blob_sha, cache)
        except Exception:
            continue
        total_src += len(content)
        raw_docs.append(RawDoc(
            source_repo=spec.repo, source_commit=sha, source_path=path,
            license_id=spec.license_id, raw_bytes=content,
        ))
    lock = SourceLock(
        repository=spec.repo,
        url=spec.url or f"https://github.com/{spec.repo}",
        commit_sha=sha,
        acquired_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        command=f"gh api git/trees/{sha[:8]} (prefix={prefix}); select<= {spec.max_docs}; download blobs",
        sparse_paths=spec.paths,
        file_count=len(raw_docs),
        source_bytes=total_src,
        license_id=spec.license_id,
        notes=f"role={spec.role}; gh_api deterministic selection",
    )
    return raw_docs, lock
