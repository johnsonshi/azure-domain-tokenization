# Results guide

How the result files are organized, which are authoritative, and how each layer
regenerates. Schema details: [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md). Every
number shown publicly is registered in
[`../publication/claims.yaml`](../publication/claims.yaml) and checked by
`make verify-claims`.

## Authoritative files

| File | Authoritative for |
|---|---|
| `raw/eval_rows.parquet` | per-(tokenizer, document) counts — the ground truth all aggregates derive from |
| `processed/eval_aggregate.csv` | corpus-level aggregates per (tokenizer, eval set) |
| `processed/bootstrap.json` | paired-bootstrap effect sizes + CIs (comparisons / by_eval_set / by_content_type / by_repository) |
| `tables/*.csv` | figure source tables + summaries |
| `figures/*.png`, `../paper/figures/*.pdf` | figures (each has a source CSV; see `figures/FIGURES.md`) |
| `reports/FINAL_REPORT.md` | narrative report |
| `reports/VERIFICATION.md` | deterministic verify-gate summary (8/8) |
| `../data/audit/audit_summary.json` | byte-match, dedup, split, leakage record |

## Layers and how they regenerate

```
sources ──acquire/audit──▶ (corpora, git-ignored)
   │
   ├─train-all──▶ artifacts/tokenizers/*.json (provenance)
   └─evaluate-all──▶ results/raw/eval_rows.parquet     ← RAW (ground truth)
                        │
              make analyze ▶ results/processed/{eval_aggregate.csv, bootstrap.json}
                        │        + results/tables/* (fragmentation, vocab_utilization, …)
              make figures ▶ results/figures/*.png + paper/figures/*.pdf + tables/figNN_*.csv
              make report  ▶ results/reports/FINAL_REPORT.md
```

- **From committed results only (no downloads):** `make analyze`, `make figures`,
  `make report`, `make verify`, `make verify-claims` all run from
  `raw/eval_rows.parquet` and the processed files, which are committed.
- **Full recompute (downloads pinned sources):** `make acquire-full audit-full
  train-all evaluate-all` then the analysis targets.

## Version control

- **Committed (publishable):** `raw/eval_rows.parquet` (no source text — only
  hashes + counts), `processed/*`, `tables/*`, `figures/*.png`, `reports/*`,
  `data/manifests/*`, `data/audit/*`, `artifacts/tokenizers/*.json`.
- **Git-ignored:** raw log files, corpora under `data/{raw,normalized,segments,
  splits,evaluation}`, the `external/` clone, and `.stages/` markers.

## Units and conventions

- **Primary metric:** tokens per **1,000 UTF-8 bytes** (lower = more compression).
- **Relative reduction (%):** `100 * (general − specialized) / general`. **Positive
  = specialized uses fewer tokens.** Negative = a regression.
- **Micro** aggregation = over all bytes (`1000 * Σ tokens / Σ bytes`); **macro** =
  mean of per-document ratios. The primary corpus-level endpoint is micro.
- **Confidence intervals:** 95%, from a **paired bootstrap over documents**
  (10,000 resamples; the same documents resampled for both tokenizers).
- **Win rate:** fraction of documents on which the specialized tokenizer uses
  strictly fewer tokens.

## Stable identifiers

- **Tokenizers (Track A, controlled):** `{general,azure,mixed}-bytebpe-{8192,16384,32768}`.
- **Tokenizers (Track B, observational):** `tiktoken-{r50k_base,cl100k_base,o200k_base}`.
- **Evaluation sets (9):** `azure_cross_service_holdout` (principal),
  `azure_same_service_holdout`, `ms_architecture`, `ms_devops`, `ms_data`,
  `ms_broad_enterprise`, `external_technical`, `general_english`, `synthetic`.

## Verifying the numbers

```bash
make verify-claims   # extracts every registered number from its source file, checks tolerance
```

See [`../publication/CLAIM_LEDGER.md`](../publication/CLAIM_LEDGER.md) and
[`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).
