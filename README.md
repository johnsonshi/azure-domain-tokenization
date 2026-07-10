# Does Your Tokenizer Speak Cloud?

**Measuring domain specialization on Microsoft technical documentation — a controlled, CPU-only, reproducible study.**

> Status: **bootstrapping** (Phase 0). See [`STATE.md`](STATE.md) for the live status, [`plan.md`](plan.md) for the full execution specification, and [`FINDINGS.md`](FINDINGS.md) for verified results.

## What this is

At a fixed tokenizer algorithm, vocabulary size, training-data size, normalization policy, and evaluation set, does training a byte-level BPE tokenizer on Azure technical documentation reduce the number of tokens required to encode unseen technical documentation compared with training on general English?

This repository contains a fully reproducible, local-only (no cloud, no GPU, no model training) harness that answers that question with a controlled experiment and preserves all provenance.

## What this is NOT

This study measures **tokenization only**. It makes **no claim** about model output quality, accuracy, reasoning, understanding, GPU latency, or cost. A trained model's embedding table is tied to its tokenizer vocabulary; swapping tokenizers is out of scope.

## Quick start

```bash
# 1. Install uv (https://astral.sh/uv), then:
uv sync

# 2. Sanity-check the environment
bash scripts/doctor.sh

# 3. Run the test suite (no network needed; uses a tiny fixture corpus)
uv run pytest

# 4. Drive the pipeline (each target is safe to re-run)
make inventory        # MicrosoftDocs repo inventory + scores
make research         # literature review artifacts
make acquire-pilot    # pin + fetch 32 MiB pilot corpora
make audit-pilot      # clean, dedupe, split, leakage audit
make train-pilot      # 16K Azure / General / Mixed tokenizers
make evaluate-pilot   # compression + round-trip on held-out sets
make report           # final report + figures + notebooks
make verify           # end-to-end reproduction check
```

## Layout

See [`plan.md` §18](plan.md) for the canonical repository structure. Key entry points:

- `src/msdocs_tokenizer/` — the pipeline library and `msdocs-tok` CLI.
- `configs/` — versioned experiment / cleaning / tokenizer configs.
- `research/`, `inventory/`, `licenses/` — frozen research + provenance artifacts.
- `results/` — raw per-document results, processed tables, figures, reports.
- `.agents/roles/` — sub-agent role briefs used by the orchestrator.

## Reproducibility & licensing

Raw source corpora are **never committed** (see `.gitignore`). We publish acquisition scripts, pinned source commits, content hashes, manifests, license records, and aggregate results. Tokenizer artifact redistribution is gated on the licensing review in `licenses/`.
