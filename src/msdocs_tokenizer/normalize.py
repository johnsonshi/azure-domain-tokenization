"""Unicode normalization and text-quality accounting (plan.md §11).

Policy:
- Apply Unicode NFC.
- Do NOT lowercase or strip accents.
- Preserve case, punctuation, code whitespace, Unicode, emoji, versions,
  placeholders.
- Count and quarantine malformed input rather than silently changing it.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field


@dataclass
class NormalizationReport:
    total: int = 0
    changed_by_nfc: int = 0
    malformed: int = 0
    empty: int = 0
    quarantined: list[str] = field(default_factory=list)


def nfc(text: str) -> str:
    """Unicode NFC normalization (idempotent, case- and accent-preserving)."""
    return unicodedata.normalize("NFC", text)


def is_nfc(text: str) -> bool:
    return unicodedata.is_normalized("NFC", text)


# UTF-8 that round-trips cleanly is required; surrogate escapes signal malformed
# decoding upstream.
_SURROGATE_RE = re.compile(r"[\ud800-\udfff]")


def decode_utf8_strict(raw: bytes) -> tuple[str | None, bool]:
    """Decode bytes as UTF-8. Returns (text, ok). ok=False => malformed."""
    try:
        return raw.decode("utf-8"), True
    except UnicodeDecodeError:
        return None, False


def normalize_document(text: str, report: NormalizationReport | None = None) -> str | None:
    """NFC-normalize a single document string, tracking whether it changed.

    Returns None (and records malformed) if the text contains lone surrogates.
    """
    if report is not None:
        report.total += 1
    if _SURROGATE_RE.search(text):
        if report is not None:
            report.malformed += 1
            report.quarantined.append(text[:80])
        return None
    normed = nfc(text)
    if report is not None:
        if normed != text:
            report.changed_by_nfc += 1
        if not normed.strip():
            report.empty += 1
    return normed


def count_metrics(text: str) -> tuple[int, int, int]:
    """Return (utf8_bytes, unicode_chars, whitespace_words)."""
    utf8_bytes = len(text.encode("utf-8"))
    unicode_chars = len(text)
    whitespace_words = len(text.split())
    return utf8_bytes, unicode_chars, whitespace_words
