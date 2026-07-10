"""Unified encoder interface over trained HF tokenizers and existing baselines
(tiktoken / WordPiece). Track A (trained) and Track B (existing) share this
harness but are always reported in separate tables (plan.md §5).
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from tokenizers import Tokenizer


@runtime_checkable
class Encoder(Protocol):
    tokenizer_id: str
    track: str  # "A" (controlled) or "B" (existing baseline)

    def encode(self, text: str) -> list[int]: ...
    def decode(self, ids: list[int]) -> str: ...
    def count_tokens(self, text: str) -> int: ...
    def unk_count(self, text: str) -> int: ...


class HFEncoder:
    """Wraps a Hugging Face ``tokenizers.Tokenizer`` (byte-level BPE)."""

    track = "A"

    def __init__(self, tokenizer_id: str, tok: Tokenizer):
        self.tokenizer_id = tokenizer_id
        self._tok = tok
        # None => no UNK token exists (byte-level BPE) => zero UNK by construction.
        try:
            import json

            model = json.loads(tok.to_str()).get("model", {})
            self._unk_token = model.get("unk_token")
        except Exception:
            self._unk_token = None

    @classmethod
    def from_file(cls, tokenizer_id: str, path: str) -> "HFEncoder":
        return cls(tokenizer_id, Tokenizer.from_file(path))

    def encode(self, text: str) -> list[int]:
        return self._tok.encode(text, add_special_tokens=False).ids

    def decode(self, ids: list[int]) -> str:
        return self._tok.decode(ids, skip_special_tokens=False)

    def count_tokens(self, text: str) -> int:
        return len(self._tok.encode(text, add_special_tokens=False).ids)

    def unk_count(self, text: str) -> int:
        if self._unk_token is None:
            return 0
        toks = self._tok.encode(text, add_special_tokens=False).tokens
        return sum(1 for t in toks if t == self._unk_token)


class TiktokenEncoder:
    """Wraps a tiktoken encoding (existing general-purpose baseline, Track B)."""

    track = "B"

    def __init__(self, tokenizer_id: str, encoding):
        self.tokenizer_id = tokenizer_id
        self._enc = encoding

    @classmethod
    def from_name(cls, encoding_name: str) -> "TiktokenEncoder":
        import tiktoken

        return cls(f"tiktoken-{encoding_name}", tiktoken.get_encoding(encoding_name))

    def encode(self, text: str) -> list[int]:
        return self._enc.encode(text, disallowed_special=())

    def decode(self, ids: list[int]) -> str:
        return self._enc.decode(ids)

    def count_tokens(self, text: str) -> int:
        return len(self._enc.encode(text, disallowed_special=()))

    def unk_count(self, text: str) -> int:
        # Byte-level BPE (tiktoken) has full byte coverage => no UNK.
        return 0


def roundtrip_ok(enc: Encoder, text: str) -> bool:
    """Exact encode->decode reconstruction check."""
    try:
        return enc.decode(enc.encode(text)) == text
    except Exception:
        return False
