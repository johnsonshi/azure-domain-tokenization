"""Deterministic byte-level BPE tokenizer training (plan.md §13).

Fixed, identical settings across the controlled comparison; only the training
corpus changes. Byte-level BPE gives complete UTF-8 coverage, so ordinary text
never produces ``[UNK]`` (zero byte-level UNK by construction).
"""
from __future__ import annotations

import json
import resource
import time
from dataclasses import dataclass
from pathlib import Path

from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers

from . import config
from .provenance import (
    atomic_write_json,
    git_commit,
    machine_id,
    package_versions,
    sha256_file,
    sha256_text,
)
from .schemas import TokenizerProvenance

MIN_FREQUENCY = 2


def build_byte_level_bpe(vocab_size: int) -> tuple[Tokenizer, trainers.BpeTrainer]:
    """Construct an untrained byte-level BPE tokenizer + trainer with fixed config."""
    tok = Tokenizer(models.BPE(unk_token=None))
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False, use_regex=True)
    tok.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=MIN_FREQUENCY,
        special_tokens=list(config.SPECIAL_TOKENS),
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        show_progress=False,
    )
    return tok, trainer


def tokenizer_config_dict(vocab_size: int) -> dict:
    """Canonical config used both to train and to hash for provenance."""
    return {
        "algorithm": "byte_level_bpe",
        "vocab_size_requested": vocab_size,
        "min_frequency": MIN_FREQUENCY,
        "special_tokens": list(config.SPECIAL_TOKENS),
        "normalization": "NFC",
        "lowercase": False,
        "strip_accents": False,
        "pre_tokenizer": "ByteLevel(add_prefix_space=False, use_regex=True)",
        "decoder": "ByteLevel",
        "initial_alphabet": "full_byte_level",
        "special_tokens_count_in_vocab": True,
    }


@dataclass
class TrainOutcome:
    tokenizer: Tokenizer
    provenance: TokenizerProvenance
    artifact_path: Path


def _maxrss_bytes() -> int:
    # macOS reports ru_maxrss in bytes; Linux in KiB. Normalize to bytes.
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    import sys

    return raw if sys.platform == "darwin" else raw * 1024


def train_tokenizer(
    corpus_path: str | Path,
    vocab_size: int,
    tokenizer_id: str,
    training_corpus: str,
    training_bytes: int,
    training_documents: int,
    training_manifest_sha256: str,
    out_dir: str | Path | None = None,
) -> TrainOutcome:
    """Train and persist one controlled tokenizer + its provenance record."""
    corpus_path = Path(corpus_path)
    out_dir = Path(out_dir) if out_dir else (config.ARTIFACTS / tokenizer_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = tokenizer_config_dict(vocab_size)
    config_sha = sha256_text(json.dumps(cfg, sort_keys=True))

    tok, trainer = build_byte_level_bpe(vocab_size)

    ru0 = resource.getrusage(resource.RUSAGE_SELF)
    wall0 = time.perf_counter()
    tok.train([str(corpus_path)], trainer)
    wall = time.perf_counter() - wall0
    ru1 = resource.getrusage(resource.RUSAGE_SELF)
    cpu = (ru1.ru_utime - ru0.ru_utime) + (ru1.ru_stime - ru0.ru_stime)

    artifact_path = out_dir / "tokenizer.json"
    tok.save(str(artifact_path))

    vocab_actual = tok.get_vocab_size()
    # merges live in the serialized model JSON (API-stable across tokenizers versions)
    tok_json = json.loads(artifact_path.read_text(encoding="utf-8"))
    merge_count = len(tok_json.get("model", {}).get("merges", []))

    prov = TokenizerProvenance(
        tokenizer_id=tokenizer_id,
        algorithm="byte_level_bpe",
        vocab_size_requested=vocab_size,
        vocab_size_actual=vocab_actual,
        special_tokens_count_in_vocab=True,
        training_corpus=training_corpus,
        training_bytes=training_bytes,
        training_documents=training_documents,
        merge_count=merge_count,
        training_manifest_sha256=training_manifest_sha256,
        config_sha256=config_sha,
        artifact_sha256=sha256_file(artifact_path),
        artifact_bytes=artifact_path.stat().st_size,
        wall_seconds=round(wall, 4),
        cpu_seconds=round(cpu, 4),
        peak_rss_bytes=_maxrss_bytes(),
        package_versions=package_versions(),
        machine_id=machine_id(),
        git_commit=git_commit(),
        created_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        seed=config.GLOBAL_SEED,
        distributable=(training_corpus == "azure"),
        distribution_note=(
            "Trained only on CC-BY-4.0 Azure documentation; redistributable WITH attribution."
            if training_corpus == "azure" else
            "Trained on WikiText (CC-BY-SA, unclear redistribution) — LOCAL-USE-ONLY, do not "
            "redistribute the tokenizer.json artifact pending legal review (licenses/RESTRICTIONS.md)."
        ),
    )
    # Persist provenance next to the artifact and in the tracked index.
    atomic_write_json(out_dir / "provenance.json", prov.model_dump())
    atomic_write_json(out_dir.parent / f"{tokenizer_id}.json", prov.model_dump())
    return TrainOutcome(tokenizer=tok, provenance=prov, artifact_path=artifact_path)


def load_tokenizer(path: str | Path) -> Tokenizer:
    return Tokenizer.from_file(str(path))
