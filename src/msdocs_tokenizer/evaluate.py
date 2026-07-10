"""Per-document evaluation and aggregation (plan.md §15, §24).

Produces one machine-readable ``EvaluationRow`` per (tokenizer, document) and
reconciling aggregates. Every reported number traces back to these rows.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import metrics
from .encoders import Encoder, roundtrip_ok
from .normalize import count_metrics
from .schemas import EvaluationRow


@dataclass
class EvalDoc:
    document_id: str
    repository: str
    content_type: str
    text: str


def evaluate_encoder(enc: Encoder, eval_set: str, docs: list[EvalDoc]) -> list[EvaluationRow]:
    rows: list[EvaluationRow] = []
    for d in docs:
        utf8_bytes, unicode_chars, words = count_metrics(d.text)
        ids = enc.encode(d.text)
        rows.append(
            EvaluationRow(
                tokenizer_id=enc.tokenizer_id,
                eval_set=eval_set,
                repository=d.repository,
                document_id=d.document_id,
                content_type=d.content_type,
                utf8_bytes=utf8_bytes,
                unicode_chars=unicode_chars,
                whitespace_words=words,
                token_count=len(ids),
                roundtrip_ok=roundtrip_ok(enc, d.text),
                unk_count=enc.unk_count(d.text),
            )
        )
    return rows


def rows_to_frame(rows: list[EvaluationRow]) -> pd.DataFrame:
    return pd.DataFrame([r.model_dump() for r in rows])


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """Corpus-level aggregates per (tokenizer_id, eval_set).

    Includes both micro (over all bytes) and macro (mean of per-doc ratios).
    """
    out = []
    for (tok_id, eval_set), g in df.groupby(["tokenizer_id", "eval_set"]):
        total_tokens = int(g["token_count"].sum())
        total_bytes = int(g["utf8_bytes"].sum())
        total_chars = int(g["unicode_chars"].sum())
        total_words = int(g["whitespace_words"].sum())
        per_doc_ratio = (1000.0 * g["token_count"] / g["utf8_bytes"].replace(0, pd.NA)).dropna()
        out.append({
            "tokenizer_id": tok_id,
            "eval_set": eval_set,
            "n_documents": int(len(g)),
            "total_tokens": total_tokens,
            "total_utf8_bytes": total_bytes,
            "total_unicode_chars": total_chars,
            "total_whitespace_words": total_words,
            "tokens_per_1000_utf8_bytes_micro": metrics.tokens_per_1000_utf8_bytes(total_tokens, total_bytes),
            "tokens_per_1000_utf8_bytes_macro": metrics.macro_mean(per_doc_ratio.tolist()),
            "tokens_per_1000_unicode_chars": metrics.tokens_per_1000_unicode_chars(total_tokens, total_chars),
            "chars_per_token": metrics.chars_per_token(total_chars, total_tokens),
            "utf8_bytes_per_token": metrics.utf8_bytes_per_token(total_bytes, total_tokens),
            "tokens_per_word": metrics.tokens_per_word(total_tokens, total_words),
            "roundtrip_ok_rate": float(g["roundtrip_ok"].mean()),
            "unk_total": int(g["unk_count"].sum()),
        })
    return pd.DataFrame(out).sort_values(["eval_set", "tokenizer_id"]).reset_index(drop=True)


def paired_reduction_table(agg: pd.DataFrame, general_id: str, specialized_id: str) -> pd.DataFrame:
    """Relative token reduction (specialized vs general) per eval_set (micro)."""
    g = agg[agg["tokenizer_id"] == general_id].set_index("eval_set")
    a = agg[agg["tokenizer_id"] == specialized_id].set_index("eval_set")
    rows = []
    for eval_set in sorted(set(g.index) & set(a.index)):
        gt = g.loc[eval_set, "tokens_per_1000_utf8_bytes_micro"]
        at = a.loc[eval_set, "tokens_per_1000_utf8_bytes_micro"]
        rows.append({
            "eval_set": eval_set,
            "general_id": general_id,
            "specialized_id": specialized_id,
            "general_tokens_per_1k_bytes": gt,
            "specialized_tokens_per_1k_bytes": at,
            "relative_token_reduction_pct": metrics.relative_token_reduction(gt, at),
        })
    return pd.DataFrame(rows)
