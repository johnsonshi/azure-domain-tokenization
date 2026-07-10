# FINDINGS

> Verified findings only (plan.md §19). Numbers below were produced by the full
> pipeline and passed the automated `verify` gate (8/8). Independent red-team
> sign-off tracked in `research/PILOT_REVIEW.md`.

Profile: **full** (32 MiB byte-matched General/Azure/Mixed corpora; full
General/Azure/Mixed × 8K/16K/32K byte-level BPE matrix). The **16K** slice is the
primary comparison. Leakage-clean: general exact-dedup (134 removed) before split
+ cross-corpus near-dup eval filter (9 removed); verify 8/8. Seed 20260709.
Sources pinned in `data/manifests/sources.lock.json`.

## F-PRIMARY — Azure tokenizer compresses the Azure cross-service holdout
- **Result:** On `azure_cross_service_holdout` (5 held-out services, n=964 docs), the
  Azure-trained 16K tokenizer uses **36.68% fewer tokens per 1,000 UTF-8 bytes**
  than the byte-matched General tokenizer (240.18 vs 379.30). 95% paired-bootstrap
  CI **[35.77%, 37.62%]**, win rate **1.000**.
- **Result files:** `results/processed/eval_aggregate.csv`, `results/processed/bootstrap.json`,
  `results/tables/reduction_azure_vs_general_16384.csv`.
- **Repro:** `PROFILE=full make analyze report verify`.
- **Reviewer:** automated verify 8/8; red-team re-review: blockers resolved in
  `research/PILOT_REVIEW.md`; numbers regenerated on leakage-clean data.
- **Caveat:** tokenization only; no model-quality/latency/cost implication.

## F-REGRESSION — Out-of-domain regression on general English
- **Result:** The Azure tokenizer is **34.75% worse** on held-out general English
  (CI [-35.10%, -34.40%]). Reported alongside the in-domain gain (plan.md §26).
- **Result file:** `results/processed/bootstrap.json` (`by_eval_set.general_english`).

## F-MIXED — Mixed 50/50 retains most of the gain with far less regression
- **Result:** Mixed tokenizer = **+34.21%** on the Azure holdout (vs Azure's +36.68%) but
  only **-4.39%** regression on general English (vs Azure's -34.75%). Secondary
  hypothesis 3 supported for the 32 MiB profile.
- **Result file:** `results/processed/eval_aggregate.csv`.

## F-TRANSFER — Partial transfer to other Microsoft + external technical docs
- **Result (Azure vs General 16K, % token reduction):** same-service holdout +35.03%,
  MS data +32.94%, MS DevOps +31.76%, external technical (Kubernetes) +31.18%,
  MS architecture +26.03%, MS broad enterprise +25.89%. All listed CIs exclude 0.
- **Result file:** `results/processed/bootstrap.json` (`by_eval_set`).

## F-VOCAB — In-domain gain is stable across the controlled vocab sizes
- **Result:** Azure-vs-General reduction on the principal holdout is +36.46% at 8K,
  +36.68% at 16K, and +35.41% at 32K.
- **Result file:** `results/tables/fig_relative_reduction_by_vocab.csv`.

## F-CONTENT — Gain persists on prose alone (not only code)
- **Result:** On the principal holdout, prose-dominant docs (n=900) show +36.75%
  (CI [35.87, 37.63]); headings +37.49%; tables +44.30%; inline_code +33.28%.
  The gain is **not** an artifact of code fences alone.
- **Result file:** `results/processed/bootstrap.json` (`by_content_type`).

## F-ROUNDTRIP — Exact reconstruction, zero UNK
- **Result:** 100% encode→decode round-trip and 0 `[UNK]` across **12 encoders × 9 eval
  sets = 59,160 rows**. Byte-level BPE full-coverage confirmed.
- **Result files:** `results/raw/eval_rows.parquet`, `results/reports/VERIFICATION.md`.

## F-RUNTIME — Compression != runtime (reported separately)
- **Result:** Track A tokenizers ~5.1-5.5 MB/s; Track B tiktoken 11-19 MB/s. The
  specialized tokenizers compress better but are slower than tiktoken on CPU.
  Secondary hypothesis 5 (compression and runtime must be reported separately) supported.
- **Result file:** `results/tables/runtime_throughput.csv`.
- **Caveat:** CPU tokenizer throughput only; not inference throughput; thermally
  variable laptop -- small differences not overinterpreted.
