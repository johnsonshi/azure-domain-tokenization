"""Paired bootstrap reproducibility and correctness (plan.md §23)."""
from __future__ import annotations

import numpy as np

from msdocs_tokenizer import stats


def test_bootstrap_reproducible():
    rng = np.random.default_rng(0)
    g = rng.integers(50, 100, size=200).astype(float)
    a = g * 0.9  # specialized always 10% fewer tokens
    r1 = stats.paired_bootstrap_relative_reduction(g, a, n_resamples=2000, seed=123)
    r2 = stats.paired_bootstrap_relative_reduction(g, a, n_resamples=2000, seed=123)
    assert r1.point_estimate == r2.point_estimate
    assert r1.ci_low == r2.ci_low
    assert r1.ci_high == r2.ci_high


def test_bootstrap_recovers_known_effect():
    g = np.full(500, 100.0)
    a = np.full(500, 90.0)  # exactly 10% reduction, no variance
    r = stats.paired_bootstrap_relative_reduction(g, a, n_resamples=1000, seed=1)
    assert abs(r.point_estimate - 10.0) < 1e-9
    # No variance => CI collapses to the point estimate
    assert abs(r.ci_low - 10.0) < 1e-9
    assert abs(r.ci_high - 10.0) < 1e-9
    assert r.win_rate == 1.0


def test_win_tie_loss():
    g = np.array([10.0, 10.0, 10.0, 10.0])
    a = np.array([8.0, 10.0, 12.0, 9.0])  # win, tie, loss, win
    r = stats.paired_bootstrap_relative_reduction(g, a, n_resamples=500, seed=2)
    assert r.win_rate == 0.5
    assert r.tie_rate == 0.25
    assert r.loss_rate == 0.25


def test_ci_ordering():
    rng = np.random.default_rng(5)
    g = rng.integers(50, 150, size=300).astype(float)
    a = g - rng.integers(0, 20, size=300)
    r = stats.paired_bootstrap_relative_reduction(g, a, n_resamples=3000, seed=7)
    assert r.ci_low <= r.point_estimate <= r.ci_high


def test_stratified():
    g = np.full(100, 100.0)
    a = np.full(100, 90.0)
    strata = ["x"] * 50 + ["y"] * 50
    out = stats.stratified_bootstrap(g, a, strata, n_resamples=500, seed=3)
    assert set(out.keys()) == {"x", "y"}
    assert abs(out["x"].point_estimate - 10.0) < 1e-9
