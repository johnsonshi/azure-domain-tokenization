"""Metric formulas on hand-worked examples + context estimates (plan.md §23)."""
from __future__ import annotations

import math

from msdocs_tokenizer import metrics


def test_tokens_per_1000_bytes_hand_worked():
    # 250 tokens over 1000 bytes -> exactly 250 tokens / 1000 bytes
    assert metrics.tokens_per_1000_utf8_bytes(250, 1000) == 250.0
    assert metrics.tokens_per_1000_utf8_bytes(0, 0) == 0.0


def test_relative_token_reduction_hand_worked():
    # general=100, specialized=80 -> 20% reduction
    assert metrics.relative_token_reduction(100, 80) == 20.0
    # regression: specialized uses MORE -> negative
    assert metrics.relative_token_reduction(100, 120) == -20.0
    assert metrics.relative_token_reduction(0, 0) == 0.0


def test_secondary_metrics_hand_worked():
    assert metrics.chars_per_token(1000, 250) == 4.0
    assert metrics.utf8_bytes_per_token(1000, 250) == 4.0
    assert metrics.tokens_per_1000_unicode_chars(250, 1000) == 250.0
    assert metrics.tokens_per_word(300, 100) == 3.0


def test_macro_mean():
    assert metrics.macro_mean([1.0, 2.0, 3.0]) == 2.0
    assert metrics.macro_mean([]) == 0.0


def test_context_estimates():
    est = metrics.context_estimates(chars_per_tok=4.0, bytes_per_tok=4.0)
    assert est["4096"]["estimated_chars"] == 4096 * 4.0
    assert est["131072"]["estimated_utf8_bytes"] == 131072 * 4.0
    assert set(est.keys()) == {"4096", "8192", "32768", "131072"}


def test_billing_delta_is_estimate():
    # 200 tokens saved at $1/1k tokens => $0.20
    assert math.isclose(metrics.estimated_token_billing_delta(1000, 800, 1.0), 0.2)


def test_fragmentation_stats_hand_worked():
    stats = metrics.fragmentation_stats([1, 1, 2, 3, 3, 3])
    assert stats.n == 6
    assert math.isclose(stats.mean, 13 / 6)
    assert math.isclose(stats.frac_one_token, 2 / 6)
    assert math.isclose(stats.frac_two_tokens, 1 / 6)
    assert math.isclose(stats.frac_three_plus, 3 / 6)


def test_fragmentation_empty():
    stats = metrics.fragmentation_stats([])
    assert stats.n == 0 and stats.mean == 0
