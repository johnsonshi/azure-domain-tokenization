# Does Your Tokenizer Speak Cloud?

**Measuring domain specialization on Microsoft technical documentation — a controlled, CPU-only, reproducible study.**

> Status: **pilot complete, full 9-tokenizer matrix trained and verified (7/7)**. See [`STATE.md`](STATE.md) for live status, [`plan.md`](plan.md) for the full spec, [`FINDINGS.md`](FINDINGS.md) for verified results, and [`results/reports/FINAL_REPORT.md`](results/reports/FINAL_REPORT.md) for the report.

## Headline result

On held-out Azure services, a byte-level BPE tokenizer trained on Azure docs uses **36.7% fewer tokens per 1,000 UTF-8 bytes** than a byte-matched general-English tokenizer (95% paired-bootstrap CI [35.8%, 37.6%], wins on 100% of 964 pages). It is **34.8% worse** on general English (the expected trade-off, reported alongside), while a 50/50 **Mixed** corpus keeps +34.2% on Azure with only −4.4% English regression. The gain survives on prose alone (+36.8%) and transfers to non-Microsoft Kubernetes docs (+31.2%). Mechanism: the Azure tokenizer fragments resource providers, URLs, CLI flags, and identifiers ~2× less and uses 82% of its vocabulary on Azure content vs General's 48%. _Tokenization only — no model-quality/latency/cost claim._


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
