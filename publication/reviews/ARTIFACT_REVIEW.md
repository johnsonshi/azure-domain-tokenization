# Artifact Review — public-artifact quality gate (plan-2.md §14)

Reviewer: independent artifact reviewer  
Date: 2026-07-10  
Branch: `publication/arxiv-prep`  
Environment used: `export PATH="$HOME/.local/bin:$PATH" TOKENIZERS_PARALLELISM=false`

## Checklist

| # | Gate item | Result | Evidence |
|---:|---|---|---|
| 1 | Root README understandable without prior context | **FAIL** | `README.md` explains the question, controlled setup, tokenization-only scope, no GPU/cloud/model training, raw corpora not committed, and reproduction commands (`README.md` lines 7-47, 59-61). However, it does **not** include a main figure above the fold, does not clearly state the primary result is the 16K slice, does not state Track B is observational, and does not provide exact resource usage in the root README. |
| 2 | Primary result reconciles programmatically | **PASS** | `uv run python scripts/verify_claims.py` reported `CLAIM VERIFICATION: 44/44 passed — ALL OK`, including `PRIMARY_REDUCTION_16K`, CI, win rate, and tokens/1K bytes. Independent recompute from `results/raw/eval_rows.parquet`: General `3946661` tokens / `10405241` bytes = `379.295492` tokens/1K bytes; Azure `2499133` tokens / same bytes = `240.180213`; relative reduction = **36.677282%**. |
| 3 | Mixed-tokenizer result reconciles | **PASS** | `verify_claims.py` passed `MIXED_REDUCTION_PRINCIPAL` actual `34.21406094924291` and `MIXED_REGRESSION` actual `-4.394184590401533`. `results/processed/eval_aggregate.csv` has Mixed 16K `249.523101` vs General `379.295492` on Azure holdout, and Mixed `238.353928` vs General `228.321078` on general English. |
| 4 | All public figures regenerate | **FAIL** | `uv run python scripts/make_figures.py` produced 6 publication figures (`fig01_primary` through `fig06_runtime`) with PNG/PDF outputs and source CSVs, but `git status` immediately afterward showed all six `paper/figures/figNN_*.pdf` files modified. This does not satisfy the unchanged/deterministic regeneration gate. |
| 5 | Public tables regenerate / have sources | **PASS** | Spot-check of `results/figures/FIGURES.md` maps each public figure to an existing source CSV: `fig01_primary_reduction.csv`, `fig02_tradeoff.csv`, `fig03_transfer.csv`, `fig_relative_reduction_by_vocab.csv`, `fig05_content.csv`, `fig06_runtime.csv`; all files exist. |
| 6 | No secret-scan blockers | **PASS** | `publication/audits/SECRET_SCAN.md` verdict is `PASS` / `NO SECRET BLOCKERS`; findings are documented as provenance hashes (`artifact_sha256`, `config_sha256`, `training_manifest_sha256`, commit SHAs, content hashes), with 0 history credential matches. |
| 7 | No raw corpora tracked | **PASS** | `git ls-files | grep -E '(^|/)data/raw|(^|/)external|corpus\.txt$|tokenizer\.json$'` returned no matches. |
| 8 | License + attribution records complete | **PASS** | `data/manifests/sources.lock.json` contains 8 locked sources. Each source repository/dataset has a matching row in `licenses/SOURCE_LICENSES.csv` and corresponding text in `licenses/ATTRIBUTION.md`. Top-level `LICENSE` exists. |
| 9 | Relative links pass | **PASS** | `uv run python scripts/publication_verify.py` reported `PUBLICATION VERIFY: OK (9 checks passed)`, including `relative Markdown links resolve — all resolve`. |
| 10 | Analysis-only reproduction passes | **PASS** | `make verify && make verify-claims && make figures && make report` completed successfully from committed results. No acquire/audit/train/evaluate targets were invoked; output used committed result artifacts. Note: the commands rewrote generated reports/notebooks/PDFs, then I restored those side effects to keep the review read-only. |
| 11 | `make verify` passes (8/8) | **PASS** | `make verify` output: `verify: PASS (8/8)` with `all_ok: true`; checks included byte match, no leakage, roundtrip, totals reconcile, provenance, artifact distribution marking, and sources lock. |
| 12 | Result terminology consistent | **PASS** | `README.md`, `docs/results.md`, and `results/README.md` consistently use tokens per 1,000 UTF-8 bytes, positive relative reduction = fewer tokens, micro as primary corpus endpoint, and Track A/B labels. `results/README.md` explicitly defines micro/macro and Track A controlled vs Track B observational. |
| 13 | Limitations visible | **PASS** | `docs/limitations.md` prominently states the 32 MiB budget, Azure-vs-general-English confound, no downstream quality evaluation, no GPU/serving benchmark, and no inference latency/cost scope. README surfaces tokenization-only scope and no model-quality/latency/cost claims, plus no GPU/no model training. |
| 14 | Snapshot tagged | **PASS** | `git tag --list experiment-full-verified-20260709` returned `experiment-full-verified-20260709`. |
| 15 | No forbidden claims | **PASS** | Grep over `README.md` and `docs/` for model quality, accuracy, reasoning, inference latency, GPU, cost, drop-in/substitution, endorsement, official Microsoft, and serving/billing terms found disclaimers/caveats only. No real forbidden claim identified. |

## Independently recomputed primary reduction

Primary micro reduction on `azure_cross_service_holdout` for `general-bytebpe-16384` vs `azure-bytebpe-16384`:

- General: `1000 * 3,946,661 / 10,405,241 = 379.295492` tokens per 1,000 UTF-8 bytes
- Azure: `1000 * 2,499,133 / 10,405,241 = 240.180213` tokens per 1,000 UTF-8 bytes
- Relative reduction: `100 * (379.295492 - 240.180213) / 379.295492 = 36.677282%`

## Blockers

1. **README gate is incomplete**: root README lacks a main figure above the fold, exact resource usage, explicit 16K primary-slice wording, and explicit Track B observational framing.
2. **Figure regeneration is not clean**: `scripts/make_figures.py` regenerated the six public figures but left all six tracked PDF files modified.

## Non-blocking recommendations

- Add the primary figure near the top of `README.md` and include a short resource-usage block for verification, figure, report, and full-recompute paths.
- Make figure PDF generation byte-stable, likely by controlling PDF metadata timestamps/IDs or checking in outputs produced by the current script version.
- Consider making `make report` default to the publication/full profile or documenting that the default `PROFILE=pilot` is intentional.

ARTIFACT REVIEW: NO-GO
