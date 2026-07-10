"""Evaluation aggregation + reconciliation (plan.md §23)."""
from __future__ import annotations

from msdocs_tokenizer import evaluate
from msdocs_tokenizer.schemas import EvaluationRow


def _rows():
    return [
        EvaluationRow(tokenizer_id="A", eval_set="s1", repository="r", document_id="d1",
                      content_type="prose", utf8_bytes=1000, unicode_chars=1000,
                      whitespace_words=100, token_count=200, roundtrip_ok=True, unk_count=0),
        EvaluationRow(tokenizer_id="A", eval_set="s1", repository="r", document_id="d2",
                      content_type="code", utf8_bytes=1000, unicode_chars=1000,
                      whitespace_words=100, token_count=300, roundtrip_ok=True, unk_count=0),
        EvaluationRow(tokenizer_id="G", eval_set="s1", repository="r", document_id="d1",
                      content_type="prose", utf8_bytes=1000, unicode_chars=1000,
                      whitespace_words=100, token_count=250, roundtrip_ok=True, unk_count=0),
        EvaluationRow(tokenizer_id="G", eval_set="s1", repository="r", document_id="d2",
                      content_type="code", utf8_bytes=1000, unicode_chars=1000,
                      whitespace_words=100, token_count=350, roundtrip_ok=True, unk_count=0),
    ]


def test_aggregate_reconciles():
    df = evaluate.rows_to_frame(_rows())
    agg = evaluate.aggregate(df)
    a = agg[agg["tokenizer_id"] == "A"].iloc[0]
    # 500 tokens over 2000 bytes -> 250 tokens/1000 bytes micro
    assert a["total_tokens"] == 500
    assert a["total_utf8_bytes"] == 2000
    assert a["tokens_per_1000_utf8_bytes_micro"] == 250.0
    # macro = mean(200/1000*1000, 300/1000*1000) = mean(200,300) = 250
    assert a["tokens_per_1000_utf8_bytes_macro"] == 250.0
    assert a["roundtrip_ok_rate"] == 1.0
    assert a["unk_total"] == 0


def test_paired_reduction_table():
    df = evaluate.rows_to_frame(_rows())
    agg = evaluate.aggregate(df)
    tbl = evaluate.paired_reduction_table(agg, general_id="G", specialized_id="A")
    row = tbl[tbl["eval_set"] == "s1"].iloc[0]
    # G: 600 tokens/2000 bytes = 300; A: 500/2000 = 250; reduction = 100*(300-250)/300
    assert abs(row["relative_token_reduction_pct"] - (100 * 50 / 300)) < 1e-9


def test_totals_reconcile_across_docs():
    df = evaluate.rows_to_frame(_rows())
    # Segment/doc/corpus totals must reconcile: sum of per-doc == corpus total
    for tok_id in ["A", "G"]:
        sub = df[df["tokenizer_id"] == tok_id]
        assert sub["token_count"].sum() == evaluate.aggregate(df).set_index(
            "tokenizer_id").loc[tok_id, "total_tokens"]
