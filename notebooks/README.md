# Notebooks

These Jupyter notebooks are explanatory release artifacts for the completed CPU-only tokenizer-efficiency study. They are **not** the core execution path: use `make verify`, `make analyze`, `make figures`, and `make report` for reproduction and verification.

The notebooks read only committed result, provenance, and report files. They do **not** download corpora, retrain tokenizers, or modify experiment outputs. Numbers shown in the notebooks trace to the claim registry in [`publication/CLAIM_LEDGER.md`](../publication/CLAIM_LEDGER.md) and the public report in [`results/reports/FINAL_REPORT.md`](../results/reports/FINAL_REPORT.md).

## Execution order

1. `01_repository_inventory.ipynb` — repository inventory, scoring, and selected sources from `inventory/`.
2. `02_corpus_audit.ipynb` — byte matching, deduplication, near-duplicate checks, and split audit from `data/audit/`.
3. `03_tokenizer_training.ipynb` — committed tokenizer artifact/provenance inventory only; no training.
4. `04_compression_results.ipynb` — token-count compression tables and bootstrap summaries from `results/`.
5. `05_fragmentation_analysis.ipynb` — fragmentation and vocabulary-utilization mechanism tables.
6. `06_runtime_benchmark.ipynb` — CPU tokenizer-throughput summaries only; no model-quality, GPU latency, or cost claims.
7. `07_final_report.ipynb` — final report excerpt and claim-evidence traceability.

## Running notebooks

From the repository root:

```bash
export PATH="$HOME/.local/bin:$PATH" TOKENIZERS_PARALLELISM=false
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=180 notebooks/<notebook>.ipynb
```

If `nbconvert` is unavailable, run the same notebooks through `nbclient`:

```bash
export PATH="$HOME/.local/bin:$PATH" TOKENIZERS_PARALLELISM=false
uv run python -c "import nbformat; from nbclient import NotebookClient; p='notebooks/<notebook>.ipynb'; nb=nbformat.read(p,4); NotebookClient(nb, timeout=180, resources={'metadata':{'path':'notebooks/'}}).execute(); nbformat.write(nb,p)"
```

Each notebook resolves the repository root by walking upward to `plan.md`, so it does not require absolute local paths. Missing optional detail files are reported as notes and the notebook continues.
