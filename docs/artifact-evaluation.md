# Artifact evaluation checklist

This page is written for an artifact-evaluation committee. It separates no-download checks from full reproduction and gives copy-paste commands.

## Quick verdict path: no corpus downloads

```bash
uv sync
export PROFILE=full
make doctor
make verify
make verify-claims
make analyze
make figures
make report
```

Expected results:

- Verification gate: 8/8 checks pass.
- Claim registry: 43/43 claims pass.
- Primary result: 36.68% fewer tokens for the Azure-trained 16K tokenizer versus the General 16K tokenizer on the Azure cross-service holdout (`PRIMARY_REDUCTION_16K`).
- Corpus byte match: 33,554,432 bytes per controlled corpus (`CORPUS_BYTES`).
- Evaluation coverage: 59,160 rows, 12 encoders, 9 evaluation sets, zero unknown tokens, and exact round-trip reconstruction (`COVERAGE_ROWS`, `COVERAGE_ENCODERS`, `COVERAGE_EVALSETS`, `COVERAGE_UNK`, `COVERAGE_ROUNDTRIP_OK`).

Approximate runtime: seconds to a few minutes after dependencies are installed. Storage: no source clones or raw corpora; only committed result artifacts are read.

## What this reproduces without downloading corpora

- Existing verification gate over committed artifacts.
- Every registered numeric claim in [`../publication/claim_evidence.csv`](../publication/claim_evidence.csv).
- Processed tables and figures from committed evaluation rows.
- Markdown reports from committed result files.
- Paper build/package checks if the local TeX/toolchain is installed.

It does **not** reacquire raw text, rebuild cleaned corpora, retrain tokenizers, or regenerate `results/raw/eval_rows.parquet`.

## Full reproduction requiring downloads

```bash
uv sync
make doctor
make acquire-full
make audit-full
make train-all
make evaluate-all
PROFILE=full make analyze
PROFILE=full make report
PROFILE=full make verify
make verify-claims
```

Expected resources: about 11 minutes for acquisition, about 4 minutes for audit, about 1 minute for training, and about 5 minutes for evaluation; about 21--22 minutes total was observed for full acquisition through analysis/report. Storage is about 2.2 GiB for external source clones, about 468--470 MiB under `data/`, about 12 MiB under `artifacts/`, and about 1.6 MiB under `results/`. Raw/source directories are git-ignored.

## Inspect raw per-document evaluation rows

The committed file [`../results/raw/eval_rows.parquet`](../results/raw/eval_rows.parquet) contains no document text. It contains provenance identifiers and counts only.

Schema:

```text
tokenizer_id, eval_set, repository, document_id, content_type,
utf8_bytes, unicode_chars, whitespace_words, token_count,
roundtrip_ok, unk_count
```

Safe inspection command:

```bash
uv run python - <<'PY'
import pandas as pd
p = 'results/raw/eval_rows.parquet'
df = pd.read_parquet(p)
print(df.dtypes)
print(df[['tokenizer_id','eval_set','repository','document_id','content_type','utf8_bytes','token_count','roundtrip_ok','unk_count']].head())
PY
```

Do not print or reconstruct source text; the parquet file has no text column.

## Regenerate tables and figures

```bash
export PROFILE=full
make analyze
make figures
make report
```

Outputs are written under [`../results/processed/`](../results/processed/), [`../results/tables/`](../results/tables/), [`../results/figures/`](../results/figures/), and paper figure directories. Figures are generated from committed source tables by [`../scripts/make_figures.py`](../scripts/make_figures.py).

## Verification commands

```bash
export PROFILE=full
make verify
make verify-claims
bash scripts/verify_all.sh full
```

`make verify` checks byte matching, leakage controls, round-trip reconstruction, totals reconciliation, provenance completeness, artifact distribution markings, and source-lock presence. `make verify-claims` checks all registered numbers against authoritative source files. `scripts/verify_all.sh full` adds non-network tests, doctor, the pipeline verify gate, and a check that raw corpora or large generated artifacts were not accidentally tracked.

## Licensing checks for reviewers

- Read [`datasets-and-licenses.md`](datasets-and-licenses.md) for the source table and redistribution policy.
- Raw corpora are not redistributed.
- Azure-only tokenizer artifacts are distributable with attribution.
- General and Mixed tokenizer artifacts are local-use-only because they involve WikiText-derived content.
- WikiText raw text and WikiText-derived tokenizer artifacts are vetoed/local-use-only pending legal review of the license-version and article-attribution questions.

## Pass/fail checklist

- [ ] `uv sync` completes from [`../uv.lock`](../uv.lock).
- [ ] `make doctor` passes.
- [ ] `PROFILE=full make verify` reports 8/8 checks passed.
- [ ] `make verify-claims` reports 43/43 claims passed.
- [ ] `make figures` regenerates figure files from committed source tables.
- [ ] `PROFILE=full make report` regenerates report artifacts.
- [ ] No raw corpora are printed, committed, or redistributed.
