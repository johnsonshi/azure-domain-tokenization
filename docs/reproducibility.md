# Reproducibility

This guide reproduces the completed CPU-only tokenizer-efficiency study without modifying the scientific record. Use the locked environment in [`../pyproject.toml`](../pyproject.toml) and [`../uv.lock`](../uv.lock), the source manifest in [`../data/manifests/sources.lock.json`](../data/manifests/sources.lock.json), and the claim registry in [`../publication/claim_evidence.csv`](../publication/claim_evidence.csv).

## Supported environment

- macOS or Linux.
- Python 3.12 managed by `uv`.
- CPU-only execution; no GPU is required.
- Keep `TOKENIZERS_PARALLELISM=false` for comparable tokenizer runtime measurements.

Install exactly:

```bash
uv sync
```

Optional preflight:

```bash
make doctor
```

The reproducibility audit verified Python 3.12.13 in the `uv` environment and locked package versions including `tokenizers` 0.21.4, `tiktoken` 0.9.0, `numpy` 2.5.1, and `pandas` 2.3.3. See [`../publication/audits/REPRODUCIBILITY_AUDIT.md`](../publication/audits/REPRODUCIBILITY_AUDIT.md).

## Path 1: analysis-only / paper-only, no corpus download

This path uses committed result artifacts and does not download raw corpora or retrain tokenizers.

```bash
uv sync
export PROFILE=full
make verify
make verify-claims
make analyze
make figures
make report
```

Expected results:

- `make verify`: 8/8 verification checks pass.
- `make verify-claims`: 43/43 registered claims pass in [`../publication/claim_evidence.csv`](../publication/claim_evidence.csv).
- Primary headline value remains 36.68% fewer tokens on the cross-service Azure holdout (`PRIMARY_REDUCTION_16K`).

Expected resources: seconds to a few minutes, no source-corpus downloads, low memory relative to the full pipeline. It reads committed files such as [`../results/raw/eval_rows.parquet`](../results/raw/eval_rows.parquet), [`../results/processed/bootstrap.json`](../results/processed/bootstrap.json), and [`../results/processed/eval_aggregate.csv`](../results/processed/eval_aggregate.csv).

Paper-only commands, if the local paper toolchain is available:

```bash
make paper
make paper-check
make arxiv-package
```

## Path 2: pilot reproduction

The pilot path is the smaller end-to-end pipeline for checking acquisition, audit, training, evaluation, analysis, and verification mechanics.

```bash
uv sync
make doctor
make acquire-pilot
make audit-pilot
make train-pilot
make evaluate-pilot
PROFILE=pilot make analyze
PROFILE=pilot make verify
PROFILE=pilot make report
```

Expected resources: smaller than the full path, but it may still use network access for source acquisition and writes ignored raw/derived data under `data/`, `external/`, `artifacts/`, and `results/`.

## Path 3: full reproduction from pinned sources

This path downloads the locked sources and rebuilds the full matrix.

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

Expected resources from the reproducibility audit:

- Acquisition: about 11 minutes of network-bound work.
- Audit: about 4 minutes.
- Training: about 1 minute for the controlled tokenizer matrix.
- Evaluation: about 5 minutes.
- Full acquisition + audit + train + evaluate + analysis/report observed at about 21--22 minutes.
- External source clone storage: about 2.2 GiB.
- `data/`: about 468--470 MiB.
- `artifacts/`: about 12 MiB.
- `results/`: about 1.6 MiB.
- CPU-only. The audit machine had 12 logical cores and recommended 10 sustained workers.

Generated raw/source directories are intentionally git-ignored.

## Path 4: verify the published numbers

Run the claim verifier against the registered numeric claims:

```bash
make verify-claims
```

Expected output: all 43 registered claims pass. The key published values are resolved from source files, including `PRIMARY_REDUCTION_16K`, `PRIMARY_CI_LOW`, `PRIMARY_CI_HIGH`, `PRIMARY_N_DOCS`, `CORPUS_BYTES`, `DEDUP_GENERAL_EXACT`, `CROSS_CORPUS_REMOVED`, `COVERAGE_ROWS`, `COVERAGE_ENCODERS`, `COVERAGE_EVALSETS`, `COVERAGE_UNK`, `COVERAGE_ROUNDTRIP_OK`, and `SEED`.

## Determinism and known nondeterminism

- A single seed, 20260709 (`SEED`), drives deterministic sampling, Azure/general splitting, and bootstrap resampling.
- Sampling uses stable SHA-256 ordering over seed, source commit, and document identifier.
- Azure split assignment is based on stable hashes over leakage groups and near-duplicate clusters.
- Bootstrap uses NumPy's seeded random generator and records the seed in the output.
- Hugging Face tokenizers can vary in thread scheduling order for runtime measurement; keep `TOKENIZERS_PARALLELISM=false`. Merge outputs and token counts are deterministic for the locked inputs.
- Laptop runtime is thermally and scheduler variable. Treat runtime as measured CPU tokenizer throughput, not model-inference latency or cost.

## Resuming interrupted stages

Each pipeline stage writes content-hash markers under `data/.stages/`. Completed stages are skipped when inputs are unchanged.

Resume the pilot or full pipeline with:

```bash
bash scripts/resume.sh pilot
bash scripts/resume.sh full
```

The resume script prints completed markers and delegates to the overnight pipeline. It does not change the locked source manifest or claim registry.

## Safe and expensive targets

Safe/no-download targets for reviewers: `make doctor`, `make test`, `PROFILE=full make verify`, `make verify-claims`, `PROFILE=full make analyze`, `make figures`, and `PROFILE=full make report`.

Expensive or network targets: `make acquire-pilot`, `make acquire-full`, `make train-pilot`, `make train-all`, `make evaluate-pilot`, `make evaluate-all`, and `make benchmark-runtime`.

Destructive target: `make clean-derived` removes derived data/results and should not be used for artifact evaluation unless intentionally resetting the workspace.
