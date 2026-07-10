"""Paired bootstrap over documents (plan.md §16).

Token counts are deterministic; uncertainty comes from the sampled documents.
We resample documents (with replacement), keeping the SAME documents paired
across the two tokenizers, and report a 95% CI on the relative token reduction.

Reproducible: identical (seed, data) always yields identical intervals.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class BootstrapResult:
    metric: str
    point_estimate: float
    ci_low: float
    ci_high: float
    mean_paired_diff: float
    median_paired_diff: float
    win_rate: float
    tie_rate: float
    loss_rate: float
    n_documents: int
    n_resamples: int
    seed: int


def paired_bootstrap_relative_reduction(
    tokens_general: np.ndarray | list[float],
    tokens_specialized: np.ndarray | list[float],
    n_resamples: int = 10000,
    seed: int = 0,
    ci: float = 0.95,
) -> BootstrapResult:
    """Bootstrap the corpus-level relative token reduction (specialized vs general).

    Both arrays are per-document token counts, aligned by document index.
    Relative reduction on a resample = 100 * (sum(G) - sum(A)) / sum(G).
    """
    g = np.asarray(tokens_general, dtype=float)
    a = np.asarray(tokens_specialized, dtype=float)
    if g.shape != a.shape:
        raise ValueError("paired arrays must have equal shape")
    n = g.shape[0]
    if n == 0:
        raise ValueError("no documents to bootstrap")

    rng = np.random.default_rng(seed)

    point = 100.0 * (g.sum() - a.sum()) / g.sum() if g.sum() else 0.0

    stats = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        gs = g[idx].sum()
        as_ = a[idx].sum()
        stats[i] = 100.0 * (gs - as_) / gs if gs else 0.0

    alpha = (1.0 - ci) / 2.0
    lo = float(np.percentile(stats, 100 * alpha))
    hi = float(np.percentile(stats, 100 * (1 - alpha)))

    diff = g - a  # tokens saved per doc by specialized
    wins = int((diff > 0).sum())
    ties = int((diff == 0).sum())
    losses = int((diff < 0).sum())

    return BootstrapResult(
        metric="relative_token_reduction_pct",
        point_estimate=float(point),
        ci_low=lo,
        ci_high=hi,
        mean_paired_diff=float(diff.mean()),
        median_paired_diff=float(np.median(diff)),
        win_rate=wins / n,
        tie_rate=ties / n,
        loss_rate=losses / n,
        n_documents=n,
        n_resamples=n_resamples,
        seed=seed,
    )


def stratified_bootstrap(
    tokens_general: np.ndarray | list[float],
    tokens_specialized: np.ndarray | list[float],
    strata: list[str],
    n_resamples: int = 10000,
    seed: int = 0,
    ci: float = 0.95,
) -> dict[str, BootstrapResult]:
    """Run the paired bootstrap within each stratum (e.g. repo or content_type)."""
    g = np.asarray(tokens_general, dtype=float)
    a = np.asarray(tokens_specialized, dtype=float)
    strata_arr = np.asarray(strata)
    out: dict[str, BootstrapResult] = {}
    for s in sorted(set(strata)):
        mask = strata_arr == s
        if mask.sum() == 0:
            continue
        out[s] = paired_bootstrap_relative_reduction(
            g[mask], a[mask], n_resamples=n_resamples, seed=seed, ci=ci
        )
    return out
