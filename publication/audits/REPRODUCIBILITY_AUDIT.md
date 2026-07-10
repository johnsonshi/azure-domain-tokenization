# Reproducibility Audit

Date: 2026-07-10 11:49-12:00 PDT  
Branch: `publication/arxiv-prep`  
Scope: read-only audit of the completed CPU-only tokenizer-efficiency study. No retraining or acquisition was run. Environment used for commands:

```bash
export PATH="$HOME/.local/bin:$PATH" TOKENIZERS_PARALLELISM=false
```

## Verdict

**REPRODUCIBILITY AUDIT: 1 blocker**

Blocker: `uv run msdocs-tok verify --profile full` passes all checks, but it updates the tracked timestamp in `results/reports/VERIFICATION.md`. I restored that file after the audit. For a public read-only verification path, `verify` should either avoid writing tracked artifacts or write only to an explicitly ignored/ephemeral location.

Non-blocking gaps:
- No `docs/reproducibility.md` file is present, although plan context says it should document environment, install, reproduction modes, cost, and determinism notes.
- `scripts/verify_claims.py` writes `publication/claim_evidence.csv`; in this run it left no git diff, but users should know it is not strictly stdout-only.

## Command results

| Check | Command | Result | Notes |
|---|---|---:|---|
| uv version | `uv --version` | OK | `uv 0.11.28` |
| Lock freshness | `uv lock --check` | OK | Resolved 87 packages in 4 ms; lock matches `pyproject.toml`. |
| Frozen sync | `uv sync --frozen` | OK | Checked 84 packages in 2 ms; no lock update required. |
| Python | `uv run python -c ...` | OK | Python `3.12.13` in the uv environment. System `/usr/bin/python3` is `3.9.6`, so reproduction docs should instruct users to run through `uv`. |
| Doctor | `bash scripts/doctor.sh` | OK | `DOCTOR: OK (0 warning(s))`; uv/git/gh/caffeinate present, gh authenticated, Python 3.12.13, core packages import, 12 logical cores / 10 sustained workers, 611.2 GiB free disk. |
| Tests | `uv run pytest -q -m "not network"` | OK | 67 non-network tests passed. |
| Full verification | `uv run msdocs-tok verify --profile full` | OK | PASS 8/8; `all_ok=true`. Caveat: updated tracked `results/reports/VERIFICATION.md` timestamp; restored after audit. |
| Claim verification | `uv run python scripts/verify_claims.py` | OK | 39/39 claims passed; wrote `publication/claim_evidence.csv` with no final diff observed. |
| Analysis-only | `uv run msdocs-tok analyze --profile full` | OK | Returned `{ "skipped": true, "bootstrap": ".../results/processed/bootstrap.json" }` because the local stage marker matched committed outputs. Source code confirms the analyze stage consumes `results/raw/eval_rows.parquet` and writes processed tables/figures, so it does not require corpora. |

### Key package versions from `uv.lock`

| Package | Locked version |
|---|---:|
| `tokenizers` | `0.21.4` |
| `tiktoken` | `0.9.0` |
| `numpy` | `2.5.1` |
| `pandas` | `2.3.3` |

## `msdocs-tok verify --profile full` checks

```json
{
  "all_ok": true,
  "checks": [
    {"name": "byte_match_ok", "ok": true, "detail": "{'azure': 33554432, 'general': 33554432, 'mixed': 33554432}"},
    {"name": "no_leakage", "ok": true, "detail": "[]"},
    {"name": "leakage_controls_present", "ok": true, "detail": "cross_corpus_removed=9"},
    {"name": "roundtrip_all_ok", "ok": true, "detail": "0 failures"},
    {"name": "totals_reconcile", "ok": true, "detail": ""},
    {"name": "provenance_complete", "ok": true, "detail": ""},
    {"name": "artifact_distribution_marked", "ok": true, "detail": "all_marked=True, no_tokenizer_json_committed=True"},
    {"name": "sources_lock_exists", "ok": true, "detail": ""}
  ]
}
```

## Make target inventory and safety

| Target | Safety class | Retrains/downloads? | Notes |
|---|---|---:|---|
| `help` | INFO | No | Lists targets. |
| `setup` | SETUP | No | Runs `uv sync`; environment mutation only. |
| `doctor` | VERIFY | No | Safe preflight. |
| `test` | VERIFY | No | Non-network tests. |
| `inventory` | NETWORK / ACQUISITION SUPPORT | Possible network | Calls `msdocs-tok inventory` / gh. |
| `research` | INFO | No | Prints pointer to curated research artifacts. |
| `acquire-pilot` | EXPENSIVE | Yes | Network/source acquisition. |
| `audit-pilot` | EXPENSIVE | No network expected | Rebuilds corpora/splits from acquired data. |
| `train-pilot` | EXPENSIVE | No | CPU tokenizer training. |
| `evaluate-pilot` | EXPENSIVE | No | CPU evaluation. |
| `pilot` | EXPENSIVE CHAIN | Yes | Full pilot chain. |
| `acquire-full` | EXPENSIVE | Yes | Network/source acquisition. |
| `audit-full` | EXPENSIVE | No network expected | Rebuilds corpora/splits from acquired data. |
| `train-all` | EXPENSIVE | No | Trains nine controlled tokenizers. |
| `evaluate-all` | EXPENSIVE | No | Evaluates full matrix. |
| `benchmark-runtime` | EXPENSIVE CPU | No | Serialized runtime benchmark. |
| `analyze` | ANALYSIS-ONLY | No | Uses committed `results/raw/eval_rows.parquet`; may regenerate processed tables/figures. |
| `report` | ANALYSIS-ONLY | No | Generates report/notebooks from existing results. |
| `verify` | VERIFY | No | Checks existing artifacts; caveat: writes tracked `results/reports/VERIFICATION.md`. |
| `clean-derived` | DESTRUCTIVE | No | Deletes derived data/results; not reproducibility-safe. |
| `verify-claims` | VERIFY | No | Checks registered claims; writes evidence CSV. |
| `figures` | ANALYSIS-ONLY | No | Regenerates publication figures from committed source tables. |
| `paper` | PAPER-ONLY | No | Compiles arXiv manuscript under `paper/`. |
| `paper-check` | PAPER-ONLY VERIFY | No | Citation/reference/link/claim/LaTeX checks. |
| `arxiv-package` | PAPER-ONLY | No | Builds source archive; does not submit. |
| `publication-verify` | PUBLICATION VERIFY | No downloads/retrain expected | Full publication gate: verify + claims + links + figures + paper. |

### Plan-2 §12 missing Make targets

None observed. These plan-2 §12/publication targets are present: `setup`, `doctor`, `verify`, `analyze`, `figures`, `report`, `paper`, `paper-check`, `arxiv-package`, and `publication-verify`.

## Determinism notes

- Single global seed is `20260709` in `configs/experiment.yaml` and `src/msdocs_tokenizer/config.py` (`GLOBAL_SEED`, overrideable by `MSDOCS_SEED`).
- Sampling is deterministic: `sampling.deterministic_sample()` sorts by SHA-256 over `(seed, source_commit, document_id)` and truncates on UTF-8 byte boundaries.
- General train/eval split uses SHA-256 over `geneval|seed|document_id`; Azure split assignment uses stable SHA-256 fractions over leakage groups and near-duplicate clusters.
- Bootstrap uses `numpy.random.default_rng(seed)` and records `seed` in bootstrap output.
- Runtime benchmark randomizes tokenizer order with `random.Random(seed)`; runtime metrics remain subject to thermal/CPU scheduling variance.
- Token counts are deterministic, but users should keep `TOKENIZERS_PARALLELISM=false` as requested to avoid thread-scheduling variation in HF tokenizers/runtime measurements.
- Acquisition reproducibility depends on pinned source locks in `data/manifests/locks/*.json` and `data/manifests/sources.lock.json`; regenerating raw results requires downloading those pinned sources.

## Analysis-only reproduction without corpora

Confirmed locally:

- `uv run msdocs-tok verify --profile full` works from existing artifacts and reports 8/8, `all_ok=true`.
- `uv run python scripts/verify_claims.py` works from committed result/evidence files and reports 39/39.
- `uv run msdocs-tok analyze --profile full` works without corpora in this checkout; it skipped due to a matching local `data/.stages/analyze-full.done.json` marker. The analyze stage input is `results/raw/eval_rows.parquet`, and the committed source outputs include `results/processed/bootstrap.json`, `results/processed/eval_aggregate.csv`, and tables under `results/tables/`.
- Raw corpora and source clones are not committed: `git ls-files data/splits/*.corpus.txt data/raw external` returned 0 paths, while `git status --ignored` shows `data/raw/`, `data/splits/`, and `external/` ignored.
- Regenerating raw `eval_rows.parquet` requires acquisition/audit/train/evaluate using pinned source manifests.

## Expected cost and resources

Measured/provenance sources: `results/raw/logs/pipeline.log`, `data/.stages/*.done.json`, and `du -sh external data results artifacts`.

| Reproduction mode | Downloads? | Expected wall time | Disk | Memory/CPU notes |
|---|---:|---:|---:|---|
| Full reproduction from pinned sources | Yes | ~21-22 min observed for full acquisition + audit + train + evaluate + analyze/report; user-provided rollup: acquisition ~11 min, audit ~4 min, train 9 tokenizers ~1 min, evaluate ~5 min. | External source clone ~2.2 GiB; `data/` ~468-470 MiB; `artifacts/` ~12 MiB; `results/` ~1.6 MiB. Ignored generated/source directories. | CPU-only. Doctor found 12 logical cores and recommends 10 sustained workers. Free disk check requires >=15%; current free disk 611.2 GiB. |
| Analysis-only from committed results | No | Seconds to a few minutes. In this checkout: verify ~instant, claims ~seconds, analyze skipped due to current marker; clean clone may recompute processed tables/figures from `eval_rows.parquet`. | Committed result files only; no source clones/corpora required. | Low memory relative to full run; reads `results/raw/eval_rows.parquet` and processed CSV/JSON. |
| Paper-only | No | Seconds to minutes, depending on local TeX/toolchain and paper checks. | Paper build artifacts/source archive only. | No tokenizer training/evaluation; possible LaTeX dependency/toolchain requirements. |

## Audit cleanup

The verify command modified only the generated timestamp in `results/reports/VERIFICATION.md`; I restored that tracked file after recording the result. The only intentional file written by this audit is `publication/audits/REPRODUCIBILITY_AUDIT.md`.
