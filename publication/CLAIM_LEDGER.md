# Claim Ledger

> Human-readable index of the programmatic claim registry. The machine-readable
> source of truth is [`claims.yaml`](claims.yaml); resolved values are in
> [`claim_evidence.csv`](claim_evidence.csv). Regenerate/verify with
> `make verify-claims` (`uv run python scripts/verify_claims.py`).

- **Total registered claims:** 39
- **Last verification:** 39/39 PASS
- **Rule:** No number may appear in README, docs, figures, tables, captions,
  social copy, release notes, or the paper unless it is registered here and
  passes verification.

## Headline claims (all reconciled to `results/`)

| Claim ID | Value | Source file | Key/column |
|---|---:|---|---|
| PRIMARY_REDUCTION_16K | 36.68% | results/processed/bootstrap.json | comparisons.azure_vs_general:16384:azure_cross_service_holdout.point_estimate |
| PRIMARY_CI_LOW / HIGH | 35.77% / 37.62% | results/processed/bootstrap.json | …ci_low / ci_high |
| PRIMARY_WIN_RATE | 1.000 | results/processed/bootstrap.json | …win_rate |
| PRIMARY_N_DOCS | 964 | results/processed/bootstrap.json | …n_documents |
| PRIMARY_AZURE_TPK / GENERAL_TPK | 240.18 / 379.30 | results/processed/eval_aggregate.csv | tokens_per_1000_utf8_bytes_micro |
| MIXED_REDUCTION_PRINCIPAL | 34.21% | results/processed/bootstrap.json | comparisons.mixed_vs_general:… |
| GENERAL_REGRESSION_AZURE | −34.75% | results/processed/bootstrap.json | by_eval_set.general_english.point_estimate |
| MIXED_REGRESSION | −4.39% | results/processed/eval_aggregate.csv | computed reduction (mixed vs general) |
| TRANSFER_* (6 sets) | +25.89% … +35.03% | results/processed/bootstrap.json | by_eval_set.* |
| VOCAB_8192/16384/32768 | 36.46 / 36.68 / 35.41% | results/tables/fig_relative_reduction_by_vocab.csv | relative_token_reduction_pct |
| CONTENT_PROSE/HEADING/TABLE/INLINE | 36.75 / 37.49 / 44.30 / 33.28% | results/processed/bootstrap.json | by_content_type.* |
| COVERAGE_ROWS / ENCODERS / EVALSETS | 59160 / 12 / 9 | results/raw/eval_rows.parquet | row/distinct counts |
| COVERAGE_UNK / ROUNDTRIP_OK | 0 / True | results/raw/eval_rows.parquet | sum / all-ok |
| CORPUS_BYTES / BYTE_MATCH_OK | 33554432 / True | data/audit/audit_summary.json | corpora_content_bytes.azure |
| DEDUP_GENERAL_EXACT / CROSS_CORPUS_REMOVED | 134 / 9 | data/audit/audit_summary.json | dedup keys |
| SEED | 20260709 | configs/experiment.yaml | seed |

See `claims.yaml` for the full 39-entry registry with extraction commands,
tolerances, and the figures/tables/paper sections each claim feeds.

## Pending additions

- Runtime Track A / Track B min–max MB/s (register against a `results/tables/runtime_summary.csv` built in Phase C).
