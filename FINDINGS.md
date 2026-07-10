# FINDINGS

> Verified findings only (plan.md §19). Numbers below were produced by the pilot
> pipeline and passed the automated `verify` gate (6/6). Independent red-team
> sign-off tracked in `research/PILOT_REVIEW.md`.

Profile: **pilot** (32 MiB byte-matched General/Azure/Mixed corpora; three 16,384-vocab
byte-level BPE tokenizers; identical config; merges=16,126 each; training bytes =
33,554,432 each). Seed 20260709. Sources pinned in `data/manifests/sources.lock.json`.

## F-PRIMARY — Azure tokenizer compresses the Azure cross-service holdout
- **Result:** On `azure_cross_service_holdout` (5 held-out services, n=964 docs), the
  Azure-trained tokenizer uses **36.77% fewer tokens per 1,000 UTF-8 bytes** than the
  byte-matched General tokenizer (240.13 vs 379.76). 95% paired-bootstrap CI
  **[35.83%, 37.74%]**, win rate **1.000**.
- **Result files:** `results/processed/eval_aggregate.csv`, `results/processed/bootstrap.json`,
  `results/tables/reduction_azure_vs_general_16384.csv`.
- **Repro:** `make audit-pilot train-pilot evaluate-pilot analyze`
- **Reviewer:** automated verify 6/6; red-team pending (`research/PILOT_REVIEW.md`).
- **Caveat:** tokenization only; no model-quality/latency/cost implication.

## F-REGRESSION — Out-of-domain regression on general English
- **Result:** The Azure tokenizer is **34.83% worse** on held-out general English
  (307.81 vs 228.29 tokens/1000 bytes; CI [-35.19%, -34.48%]). Reported alongside the
  in-domain gain (plan.md §26).
- **Result file:** `results/processed/bootstrap.json` (`by_eval_set.general_english`).

## F-MIXED — Mixed 50/50 retains most of the gain with far less regression
- **Result:** Mixed tokenizer = **+34.15%** on the Azure holdout (vs Azure's +36.77%) but
  only **-4.42%** regression on general English (vs Azure's -34.83%). Secondary
  hypothesis 3 supported at pilot scale.
- **Result file:** `results/processed/eval_aggregate.csv`.

## F-TRANSFER — Partial transfer to other Microsoft + external technical docs
- **Result (azure vs general, % token reduction):** same-service holdout +35.67%,
  MS data (sql/fabric) +33.06%, MS DevOps +31.64%, external technical (Kubernetes)
  +31.04%, MS architecture +26.08%, MS broad enterprise +26.03%. All CIs exclude 0.
- **Result file:** `results/processed/bootstrap.json` (`by_eval_set`).

## F-CONTENT — Gain persists on prose alone (not only code)
- **Result:** On the principal holdout, prose-dominant docs (n=900) show +36.84%
  (CI [35.93, 37.78]); headings +37.51%; tables +44.44%; inline_code +33.31%. The gain
  is **not** an artifact of code fences alone.
- **Result file:** `results/processed/bootstrap.json` (`by_content_type`).

## F-ROUNDTRIP — Exact reconstruction, zero UNK
- **Result:** 100% encode->decode round-trip and 0 `[UNK]` across all 6 encoders x 9 eval
  sets (29,748 rows). Byte-level BPE full-coverage confirmed.
- **Result files:** `results/raw/eval_rows.parquet`, `results/reports/VERIFICATION.md`.

## F-RUNTIME — Compression != runtime (reported separately)
- **Result:** Track A tokenizers ~5.1-5.5 MB/s; Track B tiktoken 11-19 MB/s. The
  specialized tokenizers compress better but are slower than tiktoken on CPU. Secondary
  hypothesis 5 (compression and runtime must be reported separately) supported.
- **Result file:** `results/tables/runtime_throughput.csv`.
- **Caveat:** CPU tokenizer throughput only; not inference throughput; thermally
  variable laptop -- small differences not overinterpreted.
