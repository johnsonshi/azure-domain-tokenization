"""Pydantic schemas for segments, evaluation rows, tokenizer provenance, and
source locks (plan.md §10, §24). These are the machine-readable contracts every
result must satisfy.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from .config import CONTENT_TYPES

ContentType = Literal[
    "prose", "heading", "table", "inline_code", "code", "cli",
    "json", "yaml", "powershell", "bicep", "url_path", "mixed", "unknown",
]
SplitName = Literal[
    "azure_train",
    "azure_same_service_holdout",
    "azure_cross_service_holdout",
    "eval",
    "unassigned",
]


class Segment(BaseModel):
    """A reader-visible unit of text with full provenance (plan.md §10)."""

    source_repo: str
    source_commit: str
    source_path: str
    document_id: str
    segment_id: str
    content_type: str
    language: str = "en"
    utf8_bytes: int = Field(ge=0)
    unicode_chars: int = Field(ge=0)
    whitespace_words: int = Field(ge=0)
    sha256: str
    split: SplitName = "unassigned"
    license_id: str = "UNKNOWN"
    text: str = ""
    classifier_rule: str = ""
    classifier_confidence: float = 1.0

    @field_validator("content_type")
    @classmethod
    def _valid_content_type(cls, v: str) -> str:
        if v not in CONTENT_TYPES:
            raise ValueError(f"content_type {v!r} not in {CONTENT_TYPES}")
        return v


class EvaluationRow(BaseModel):
    """One (tokenizer, document) measurement (plan.md §24)."""

    tokenizer_id: str
    eval_set: str
    repository: str
    document_id: str
    content_type: str
    utf8_bytes: int = Field(ge=0)
    unicode_chars: int = Field(ge=0)
    whitespace_words: int = Field(ge=0)
    token_count: int = Field(ge=0)
    roundtrip_ok: bool
    unk_count: int = Field(ge=0)


class TokenizerProvenance(BaseModel):
    """Full provenance for one trained tokenizer (plan.md §24)."""

    tokenizer_id: str
    algorithm: str = "byte_level_bpe"
    vocab_size_requested: int
    vocab_size_actual: int
    special_tokens_count_in_vocab: bool
    training_corpus: str
    training_bytes: int
    training_documents: int
    merge_count: int
    training_manifest_sha256: str
    config_sha256: str
    artifact_sha256: str
    artifact_bytes: int
    wall_seconds: float
    cpu_seconds: float
    peak_rss_bytes: int
    package_versions: dict = Field(default_factory=dict)
    machine_id: str = ""
    git_commit: str = ""
    created_at: str = ""
    seed: int = 0
    distributable: bool = False
    distribution_note: str = ""


class SourceLock(BaseModel):
    """One pinned source in data/manifests/sources.lock.json (plan.md §9)."""

    repository: str
    url: str
    commit_sha: str
    acquired_at: str
    command: str
    sparse_paths: list[str] = Field(default_factory=list)
    file_count: int = 0
    source_bytes: int = 0
    retained_clean_bytes: int = 0
    license_id: str = "UNKNOWN"
    redistributable: Optional[bool] = None
    notes: str = ""
