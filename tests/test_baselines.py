"""Existing-tokenizer (Track B) adapters (plan.md §23).

tiktoken may need to fetch BPE ranks on first use; these tests skip gracefully
when offline so the default suite runs without network.
"""
from __future__ import annotations

import pytest

from msdocs_tokenizer import baselines
from msdocs_tokenizer.encoders import roundtrip_ok

SAMPLES = [
    "Azure Container Registry stores images.",
    '{"sku": "Premium"}',
    "café 🚀 版本",
    "az acr create --name myReg",
]


@pytest.mark.network
def test_tiktoken_adapter_roundtrip():
    try:
        encs = baselines.load_tiktoken_baselines(("cl100k_base",))
    except Exception as exc:  # offline / no cache
        pytest.skip(f"tiktoken unavailable offline: {exc}")
    enc = encs[0]
    assert enc.track == "B"
    for s in SAMPLES:
        assert roundtrip_ok(enc, s)
        assert enc.count_tokens(s) == len(enc.encode(s))
        assert enc.unk_count(s) == 0


def test_baseline_metadata_shape():
    md = baselines.baseline_metadata()
    ids = {m["tokenizer_id"] for m in md}
    assert "tiktoken-cl100k_base" in ids
    assert all(m["track"] == "B" for m in md)
    assert all("vocab_size" in m for m in md)
