"""Existing-tokenizer baselines (Track B, descriptive only) — plan.md §5.

These are NOT controlled comparisons: they differ in training data, vocabulary
size, normalization, algorithm, and intended model. Reported in separate tables.
"""
from __future__ import annotations

from .encoders import TiktokenEncoder

# tiktoken encodings that ship locally (no network) via the tiktoken package.
TIKTOKEN_BASELINES = ("r50k_base", "cl100k_base", "o200k_base")


def load_tiktoken_baselines(names: tuple[str, ...] = TIKTOKEN_BASELINES) -> list[TiktokenEncoder]:
    encs: list[TiktokenEncoder] = []
    for name in names:
        try:
            encs.append(TiktokenEncoder.from_name(name))
        except Exception as exc:  # pragma: no cover - network/cache dependent
            # tiktoken may need to download the BPE ranks on first use.
            raise RuntimeError(f"could not load tiktoken baseline {name!r}: {exc}") from exc
    return encs


def baseline_metadata() -> list[dict]:
    """Descriptive metadata for the baseline table (labelled observational)."""
    return [
        {"tokenizer_id": "tiktoken-r50k_base", "vocab_size": 50257,
         "intended_model": "GPT-3 / davinci", "algorithm": "byte_level_bpe", "track": "B"},
        {"tokenizer_id": "tiktoken-cl100k_base", "vocab_size": 100277,
         "intended_model": "GPT-3.5 / GPT-4", "algorithm": "byte_level_bpe", "track": "B"},
        {"tokenizer_id": "tiktoken-o200k_base", "vocab_size": 200019,
         "intended_model": "GPT-4o", "algorithm": "byte_level_bpe", "track": "B"},
    ]
