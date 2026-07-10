"""Deterministic, byte-budgeted corpus sampling (plan.md §9).

Corpora are matched by cleaned UTF-8 *bytes*, not document count. Selection is a
pure function of (seed, source_commit, document_id, target_byte_budget), so the
same inputs always yield byte-identical corpora.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .provenance import sha256_text


@dataclass
class SelectedDoc:
    document_id: str
    utf8_bytes: int
    truncated: bool = False


@dataclass
class SampleResult:
    docs: list[SelectedDoc] = field(default_factory=list)
    total_bytes: int = 0
    target_bytes: int = 0
    texts: dict[str, str] = field(default_factory=dict)  # document_id -> (possibly truncated) text

    @property
    def within_tolerance(self) -> bool:
        if self.target_bytes == 0:
            return True
        return abs(self.total_bytes - self.target_bytes) / self.target_bytes <= 0.001


def _priority(seed: int, source_commit: str, document_id: str) -> str:
    return sha256_text(f"{seed}|{source_commit}|{document_id}")


def _truncate_to_bytes(text: str, max_bytes: int) -> str:
    """Return the longest UTF-8-valid prefix of ``text`` within ``max_bytes``."""
    raw = text.encode("utf-8")
    if len(raw) <= max_bytes:
        return text
    return raw[:max_bytes].decode("utf-8", errors="ignore")


def deterministic_sample(
    docs: list[tuple[str, str]],
    target_bytes: int,
    seed: int,
    source_commit: str,
    truncate_final: bool = True,
) -> SampleResult:
    """Select documents (in deterministic priority order) up to a byte budget.

    ``docs`` = [(document_id, text)]. The final document may be truncated on a
    UTF-8 character boundary so the total lands on ``target_bytes`` exactly.
    """
    ordered = sorted(docs, key=lambda d: _priority(seed, source_commit, d[0]))
    result = SampleResult(target_bytes=target_bytes)
    for doc_id, text in ordered:
        b = len(text.encode("utf-8"))
        remaining = target_bytes - result.total_bytes
        if remaining <= 0:
            break
        if b <= remaining:
            result.docs.append(SelectedDoc(doc_id, b, truncated=False))
            result.texts[doc_id] = text
            result.total_bytes += b
        elif truncate_final:
            piece = _truncate_to_bytes(text, remaining)
            pb = len(piece.encode("utf-8"))
            if pb > 0:
                result.docs.append(SelectedDoc(doc_id, pb, truncated=True))
                result.texts[doc_id] = piece
                result.total_bytes += pb
            break
        else:
            break
    return result


def interleave_mixed(
    part_a: list[tuple[str, str]],
    part_b: list[tuple[str, str]],
    target_bytes: int,
    seed: int,
    commit_a: str,
    commit_b: str,
) -> tuple[SampleResult, SampleResult]:
    """Build a 50/50 (by bytes) mixed corpus deterministically.

    Returns (sample_a, sample_b), each targeted at target_bytes/2, so the union
    is byte-matched to a single-source corpus of ``target_bytes``.
    """
    half = target_bytes // 2
    sa = deterministic_sample(part_a, half, seed, commit_a, truncate_final=True)
    sb = deterministic_sample(part_b, target_bytes - half, seed, commit_b, truncate_final=True)
    return sa, sb
