# RUN LOG

> Concise chronology (plan.md §19). Detailed logs live under `results/raw/logs/`.

- **2026-07-09 23:50** — Session start. Read `plan.md` (1524 lines). Inspected repo:
  empty except `plan.md`, no commits.
- **2026-07-09 23:51** — Environment probe: macOS 26.5, Apple M3 Pro, 12 cores, 36 GB
  RAM, 607 GB free disk. `uv` missing, system Python 3.9.6, `gh` authenticated.
- **2026-07-09 23:52** — Installed `uv` 0.11.28. Started `caffeinate` (10h). Pinned
  project to Python 3.12.
- **2026-07-09 23:53** — `uv sync`: tokenizers 0.21.4, tiktoken 0.9.0, numpy 2.5.1,
  pandas 2.3.3, scipy, pyarrow, datasketch, matplotlib, nbformat installed.
- **2026-07-09 23:54–00:20** — Built library: config, provenance, schemas, normalize,
  markdown_extract, dedup, splitting, sampling, metrics, stats, train, encoders,
  baselines, evaluate, vocab, runtime_bench, staging, corpus, acquire, sources,
  synthetic, pipeline, report, cli. Fixture corpus + 8 test modules.
- **2026-07-09 00:05** — Fixed tokenizers 0.21 `__getstate__` pickled-bytes pitfall
  (read merges/unk from tokenizer.json). **`uv run pytest` → 63 passed** (1.23s).
  Network test confirms tiktoken baselines load + round-trip.
- **2026-07-09 00:20** — Inspected source repos via gh api: azure-docs (CC-BY-4.0,
  144 services), sql-docs / azure-devops-docs / architecture-center / kubernetes
  website all CC-BY-4.0; PowerShell-Docs = NOASSERTION (pending review).
- **2026-07-10 00:25** — Wrote `configs/experiment.yaml`, `configs/sources.yaml`,
  Makefile, scripts (doctor/overnight/resume/verify_all), STATE/DECISIONS/FINDINGS.
- **Next** — Launch Phase-1 sub-agents (research, discovery, license, methodology);
  synthesize pilot spec; run pilot.
