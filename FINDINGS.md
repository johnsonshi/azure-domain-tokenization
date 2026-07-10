# FINDINGS

> Verified findings only (plan.md §19). Each entry: finding, result file,
> reproduction command, commit, reviewer, caveat. No number appears here until a
> committed result table backs it and an independent check has passed.

---

_No empirical findings yet. The pipeline and controlled design are in place; the
pilot experiment (32 MiB byte-matched General/Azure/Mixed corpora, three 16K
byte-level BPE tokenizers) has not yet been executed._

Findings will be appended after `make evaluate-pilot analyze verify` produces
`results/tables/eval_aggregate.csv` and `results/processed/bootstrap.json`, and the
red-team reviewer signs off in `research/PILOT_REVIEW.md`.

## Placeholders (to be filled by the pilot)

- **F-PRIMARY** — Relative token reduction (Azure vs byte-matched General) on the
  Azure cross-service holdout at 16K vocab, with 95% paired-bootstrap CI.
  - Result: `results/tables/reduction_azure_vs_general_16384.csv`, `results/processed/bootstrap.json`
  - Repro: `make evaluate-pilot analyze`
- **F-REGRESSION** — General-English regression of the Azure tokenizer (reported
  alongside in-domain gains).
- **F-MIXED** — Whether Mixed 50/50 retains most of the Azure gain with less
  general-English regression.
- **F-ROUNDTRIP** — Exact encode/decode round-trip rate + `[UNK]` rate across all
  eval sets (must be 100% / 0 for byte-level BPE).
