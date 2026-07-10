"""Vocabulary utilization metrics (plan.md §15) and token classification."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from tokenizers import Tokenizer

_LETTER = re.compile(r"[^\W\d_]", re.UNICODE)
_DIGIT = re.compile(r"\d")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)


def classify_token(token_text: str) -> str:
    """Coarse class for a decoded token: letters/digits/punct/whitespace/mixed."""
    if token_text == "":
        return "empty"
    if token_text.isspace() or token_text.replace("Ġ", " ").isspace():
        return "whitespace"
    clean = token_text.replace("Ġ", "").replace("Ċ", "")
    has_letter = bool(_LETTER.search(clean))
    has_digit = bool(_DIGIT.search(clean))
    has_punct = bool(_PUNCT.search(clean))
    kinds = sum([has_letter, has_digit, has_punct])
    if kinds > 1:
        return "mixed"
    if has_letter:
        return "letters"
    if has_digit:
        return "digits"
    if has_punct:
        return "punctuation"
    return "mixed"


@dataclass
class VocabUtilization:
    vocab_size: int
    used_at_least_once: int
    used_ge_10: int
    used_ge_100: int
    used_ge_1000: int
    unused: int
    frac_used: float
    top1pct_occurrence_share: float
    top5pct_occurrence_share: float
    top10pct_occurrence_share: float
    token_class_counts: dict
    mean_token_byte_len: float


def vocabulary_utilization(tok: Tokenizer, token_id_counts: Counter[int]) -> VocabUtilization:
    """Given a tokenizer and observed token-id counts on an eval set."""
    vocab = tok.get_vocab()  # token_text -> id
    id_to_text = {i: t for t, i in vocab.items()}
    vocab_size = len(vocab)

    used = {tid: c for tid, c in token_id_counts.items() if c > 0}
    counts_sorted = sorted(used.values(), reverse=True)
    total_occ = sum(counts_sorted)

    def share(frac: float) -> float:
        if not counts_sorted or total_occ == 0:
            return 0.0
        k = max(1, int(len(vocab) * frac))
        return sum(counts_sorted[:k]) / total_occ

    byte_lens = [len(t.replace("Ġ", " ").replace("Ċ", "\n").encode("utf-8")) for t in vocab]

    class_counts: dict[str, int] = {}
    for t in vocab:
        c = classify_token(t)
        class_counts[c] = class_counts.get(c, 0) + 1

    return VocabUtilization(
        vocab_size=vocab_size,
        used_at_least_once=len(used),
        used_ge_10=sum(1 for c in used.values() if c >= 10),
        used_ge_100=sum(1 for c in used.values() if c >= 100),
        used_ge_1000=sum(1 for c in used.values() if c >= 1000),
        unused=vocab_size - len(used),
        frac_used=len(used) / vocab_size if vocab_size else 0.0,
        top1pct_occurrence_share=share(0.01),
        top5pct_occurrence_share=share(0.05),
        top10pct_occurrence_share=share(0.10),
        token_class_counts=class_counts,
        mean_token_byte_len=sum(byte_lens) / len(byte_lens) if byte_lens else 0.0,
    )


def vocab_overlap(tok_a: Tokenizer, tok_b: Tokenizer) -> dict:
    """Vocabulary overlap between two trained tokenizers."""
    a = set(tok_a.get_vocab().keys())
    b = set(tok_b.get_vocab().keys())
    inter = a & b
    return {
        "size_a": len(a),
        "size_b": len(b),
        "intersection": len(inter),
        "unique_to_a": len(a - b),
        "unique_to_b": len(b - a),
        "jaccard": len(inter) / len(a | b) if (a or b) else 0.0,
    }
