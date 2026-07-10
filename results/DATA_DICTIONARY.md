# Data dictionary

Schemas for the committed result files. Units and sign conventions are in
[`README.md`](README.md).

## `raw/eval_rows.parquet` — per-(tokenizer, document) rows (ground truth)

One row per (tokenizer, evaluation document). Contains **no source text** — only
hashes and counts, so it is publishable.

| Column | Type | Unit / meaning |
|---|---|---|
| `tokenizer_id` | string | tokenizer, e.g. `azure-bytebpe-16384` or `tiktoken-cl100k_base` |
| `eval_set` | string | one of the 9 evaluation sets (see results README) |
| `repository` | string | source repository/dataset the document came from |
| `document_id` | string | `sha256:…` content-addressed document id (no text) |
| `content_type` | string | dominant content type (prose, heading, table, inline_code, code, …) |
| `utf8_bytes` | int | UTF-8 byte length of the document |
| `unicode_chars` | int | Unicode code-point count |
| `whitespace_words` | int | whitespace-delimited word count |
| `token_count` | int | tokens produced by `tokenizer_id` for this document |
| `roundtrip_ok` | bool | exact encode→decode reconstruction succeeded |
| `unk_count` | int | number of unknown tokens (0 for byte-level BPE) |

Rows: 59,160 (`COVERAGE_ROWS`) = 12 encoders × 9 eval sets.

## `processed/eval_aggregate.csv` — corpus-level aggregates

One row per (tokenizer_id, eval_set). Key columns:

| Column | Type | Meaning |
|---|---|---|
| `tokenizer_id`, `eval_set` | string | grouping keys |
| `n_documents` | int | documents in the group |
| `total_tokens`, `total_utf8_bytes`, `total_unicode_chars`, `total_whitespace_words` | int | sums |
| `tokens_per_1000_utf8_bytes_micro` | float | **primary metric (micro)**: `1000 * total_tokens / total_utf8_bytes` |
| `tokens_per_1000_utf8_bytes_macro` | float | mean of per-document ratios (macro) |
| `tokens_per_1000_unicode_chars` | float | secondary compression metric |
| `chars_per_token`, `utf8_bytes_per_token`, `tokens_per_word` | float | secondary metrics |
| `roundtrip_ok_rate` | float | fraction of documents with exact round-trip |
| `unk_total` | int | total unknown tokens in the group |

## `processed/bootstrap.json` — paired-bootstrap effect sizes

```jsonc
{
  "profile": "full", "n_resamples": 10000, "seed": 20260709,
  "comparisons": {                       // keyed "azure_vs_general:<vocab>:<eval_set>" etc.
    "azure_vs_general:16384:azure_cross_service_holdout": {
      "point_estimate": 36.68,           // relative reduction %
      "ci_low": 35.77, "ci_high": 37.62, // 95% paired-bootstrap CI
      "win_rate": 1.0, "n_documents": 964,
      "mean_paired_diff": ..., "median_paired_diff": ...,
      "tie_rate": ..., "loss_rate": ...
    }, ...
  },
  "by_eval_set":     { "<eval_set>":    { point_estimate, ci_low, ci_high, win_rate, n_documents } },
  "by_content_type": { "<content_type>":{ ... , n_documents } },
  "by_repository":   { "<repository>":  { ... } }
}
```

Sign convention: `point_estimate` > 0 means the specialized tokenizer uses fewer
tokens; `by_eval_set.general_english` is negative (regression).

## `tables/*.csv` — figure source tables + summaries

| File | Contents |
|---|---|
| `fig01_primary_reduction.csv` | vocab, reduction_pct, ci_low, ci_high |
| `fig02_tradeoff.csv` | tokenizer, azure_holdout_pct, general_english_pct |
| `fig03_transfer.csv` | eval_set, label, reduction_pct, ci_low, ci_high |
| `fig05_content.csv` | content_type, reduction_pct, ci_low, ci_high, n |
| `fig06_runtime.csv` | tokenizer_id, tokens_per_1000_bytes, mb_per_second_median, track |
| `fig_relative_reduction_by_vocab.csv` | vocab, relative_token_reduction_pct |
| `eval_aggregate.csv` | copy of processed aggregates |
| `reduction_azure_vs_general_16384.csv`, `reduction_mixed_vs_general_16384.csv` | per-eval-set reductions |
| `fragmentation.csv` | category, tokenizer_id, mean/median/p95 tokens per item, frac_1/2/3+ |
| `vocab_utilization.csv` | tokenizer_id, frac_used, used_ge_10/100/1000, unused, top-share, mean token byte len |
| `runtime_throughput.csv` | tokenizer_id, mb_per_second_median/p95, load_seconds |
| `runtime_summary.csv` | track (A/B), min, max median MB/s |

## `../data/audit/audit_summary.json` — corpus audit

Byte-match (`corpora_content_bytes`, `byte_match_ok`), exact/near-dedup counts
(`exact_dedup_general`, `near_dup_azure`, `cross_corpus_near_dup_eval`), Azure
split sizes (`azure_splits`), and leakage-violation list (empty).

To introspect any file: `uv run python -c "import pandas as pd; print(pd.read_parquet('results/raw/eval_rows.parquet').dtypes)"`.
