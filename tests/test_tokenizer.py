"""Tokenizer training: round-trip, zero byte-level UNK, adapters, provenance
(plan.md §23)."""
from __future__ import annotations

from pathlib import Path

import pytest

from msdocs_tokenizer import markdown_extract as mx
from msdocs_tokenizer import train
from msdocs_tokenizer.encoders import HFEncoder, roundtrip_ok
from msdocs_tokenizer.schemas import TokenizerProvenance

ROUNDTRIP_SAMPLES = [
    "Azure Container Registry",
    "az acr create --resource-group myGroup --name myReg --sku Premium",
    '{"sku": "Premium", "adminUserEnabled": false}',
    "Microsoft.ContainerRegistry/registries@2023-07-01",
    "café PÑEÑO 版本 3.14.0 🚀🔥",
    "https://learn.microsoft.com/azure/container-registry",
    "",  # empty string
    "   \t  \n  ",  # unusual whitespace
    "repeat " * 50,
    "GUID: 3f2504e0-4f89-41d3-9a0c-0305e82c3301",
]


@pytest.fixture(scope="module")
def tiny_tokenizer(tmp_path_factory, request):
    fixtures = Path(request.config.rootdir) / "tests" / "fixtures"
    mds = [
        (fixtures / "azure_sample.md").read_text(encoding="utf-8"),
        (fixtures / "general_sample.md").read_text(encoding="utf-8"),
        (fixtures / "automation_sample.md").read_text(encoding="utf-8"),
    ]
    text = "\n\n".join(mx.to_representation(mx.extract_segments(md), "semantic_full") for md in mds)
    tmp = tmp_path_factory.mktemp("tok")
    corpus = tmp / "corpus.txt"
    corpus.write_text((text + "\n") * 60, encoding="utf-8")
    outcome = train.train_tokenizer(
        corpus_path=corpus,
        vocab_size=1500,
        tokenizer_id="test-tiny",
        training_corpus="test",
        training_bytes=corpus.stat().st_size,
        training_documents=3,
        training_manifest_sha256="0" * 64,
        out_dir=tmp / "artifact",
    )
    return outcome


def test_roundtrip_exact(tiny_tokenizer):
    enc = HFEncoder("test-tiny", tiny_tokenizer.tokenizer)
    for sample in ROUNDTRIP_SAMPLES:
        assert roundtrip_ok(enc, sample), f"round-trip failed for {sample!r}"


def test_zero_byte_level_unk(tiny_tokenizer):
    enc = HFEncoder("test-tiny", tiny_tokenizer.tokenizer)
    for sample in ROUNDTRIP_SAMPLES:
        assert enc.unk_count(sample) == 0


def test_count_matches_encode(tiny_tokenizer):
    enc = HFEncoder("test-tiny", tiny_tokenizer.tokenizer)
    for sample in ROUNDTRIP_SAMPLES:
        assert enc.count_tokens(sample) == len(enc.encode(sample))


def test_provenance_complete(tiny_tokenizer):
    prov = tiny_tokenizer.provenance
    assert isinstance(prov, TokenizerProvenance)
    assert prov.vocab_size_actual > 0
    assert prov.vocab_size_actual <= 1500
    assert prov.artifact_sha256 and len(prov.artifact_sha256) == 64
    assert prov.config_sha256 and len(prov.config_sha256) == 64
    assert prov.wall_seconds >= 0
    assert prov.package_versions.get("tokenizers")
    assert prov.machine_id
    assert prov.merge_count > 0
    assert prov.special_tokens_count_in_vocab is True


def test_artifact_and_provenance_written(tiny_tokenizer):
    assert tiny_tokenizer.artifact_path.exists()
    prov_json = tiny_tokenizer.artifact_path.parent / "provenance.json"
    assert prov_json.exists()


def test_special_tokens_present(tiny_tokenizer):
    vocab = tiny_tokenizer.tokenizer.get_vocab()
    assert "<|endoftext|>" in vocab
    assert "<|pad|>" in vocab
