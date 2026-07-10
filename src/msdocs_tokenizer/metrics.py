"""Compression, fragmentation, and context-estimate metrics (plan.md §15).

All primary formulas are pure functions over aggregate counts so they can be
verified on hand-worked examples (plan.md §23). "Tokenization efficiency" is
never used without a named dimension.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

CONTEXT_WINDOWS = (4096, 8192, 32768, 131072)


# --------------------------------------------------------------------------- #
# Primary endpoint + effect size
# --------------------------------------------------------------------------- #
def tokens_per_1000_utf8_bytes(total_tokens: int, total_utf8_bytes: int) -> float:
    """Primary endpoint. Lower is better."""
    if total_utf8_bytes == 0:
        return 0.0
    return 1000.0 * total_tokens / total_utf8_bytes


def relative_token_reduction(tokens_general: float, tokens_specialized: float) -> float:
    """Percentage token reduction of specialized vs general. Positive = fewer."""
    if tokens_general == 0:
        return 0.0
    return 100.0 * (tokens_general - tokens_specialized) / tokens_general


def macro_mean(ratios: list[float]) -> float:
    return float(np.mean(ratios)) if ratios else 0.0


# --------------------------------------------------------------------------- #
# Secondary compression metrics
# --------------------------------------------------------------------------- #
def chars_per_token(total_unicode_chars: int, total_tokens: int) -> float:
    return (total_unicode_chars / total_tokens) if total_tokens else 0.0


def utf8_bytes_per_token(total_utf8_bytes: int, total_tokens: int) -> float:
    return (total_utf8_bytes / total_tokens) if total_tokens else 0.0


def tokens_per_1000_unicode_chars(total_tokens: int, total_unicode_chars: int) -> float:
    if total_unicode_chars == 0:
        return 0.0
    return 1000.0 * total_tokens / total_unicode_chars


def tokens_per_word(total_tokens: int, total_words: int) -> float:
    return (total_tokens / total_words) if total_words else 0.0


# --------------------------------------------------------------------------- #
# Context + billing estimates (clearly labelled estimates)
# --------------------------------------------------------------------------- #
def context_estimates(chars_per_tok: float, bytes_per_tok: float) -> dict[str, dict[str, float]]:
    """Estimated chars/bytes that fit in each context window. ESTIMATE ONLY."""
    out: dict[str, dict[str, float]] = {}
    for w in CONTEXT_WINDOWS:
        out[str(w)] = {
            "estimated_chars": round(w * chars_per_tok, 2),
            "estimated_utf8_bytes": round(w * bytes_per_tok, 2),
        }
    return out


def estimated_token_billing_delta(tokens_general: float, tokens_specialized: float,
                                  price_per_1k_tokens: float = 1.0) -> float:
    """Estimated per-document billing difference. ESTIMATE ONLY (not measured cost)."""
    return (tokens_general - tokens_specialized) / 1000.0 * price_per_1k_tokens


# --------------------------------------------------------------------------- #
# Fragmentation (plan.md §15)
# --------------------------------------------------------------------------- #
@dataclass
class FragmentationStats:
    n: int
    mean: float
    median: float
    p95: float
    frac_one_token: float
    frac_two_tokens: float
    frac_three_plus: float


def fragmentation_stats(tokens_per_item: list[int]) -> FragmentationStats:
    """Distribution of tokens-per-identifier / per-word / per-flag / per-path."""
    if not tokens_per_item:
        return FragmentationStats(0, 0, 0, 0, 0, 0, 0)
    arr = np.asarray(tokens_per_item, dtype=float)
    n = len(arr)
    return FragmentationStats(
        n=n,
        mean=float(arr.mean()),
        median=float(np.median(arr)),
        p95=float(np.percentile(arr, 95)),
        frac_one_token=float((arr == 1).sum() / n),
        frac_two_tokens=float((arr == 2).sum() / n),
        frac_three_plus=float((arr >= 3).sum() / n),
    )
