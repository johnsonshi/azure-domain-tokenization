# STATE

> Canonical run state. Keep under 250 lines. A fresh agent must be able to resume
> from this file + repository state alone (plan.md §19).

- **Updated:** 2026-07-10T10:22-07:00
- **Phase:** COMPLETE — full 9-tokenizer matrix, leakage-clean, verify 8/8, verify_all OK, red-team blockers resolved. Report/article/notebooks delivered.
- **Profile delivered:** full matrix (General/Azure/Mixed × 8K/16K/32K) at byte-matched 32 MiB; 16K also serves as the pilot. Optional `scale` (96 MiB) profile available if more Azure services are acquired.
- **Runtime budget:** 10h. **Disk:** 607 GiB free (32% used) — well above 15% floor.
- **Workers:** 10 (max(1, 12−2)). **Seed:** 20260709.

## Completed gates

- [x] **Phase 0 bootstrap**: repo skeleton, `uv` env (Python 3.12), library, CLI,
      Makefile, scripts, fixture corpus, **67 tests passing**, `doctor.sh` green.
- [x] **Phase 1 research + discovery**: literature review (16 verified papers +
      3 plan arXiv IDs confirmed real), MicrosoftDocs inventory + scores + selection
      (5 transfer repos / 4 strata, pinned commits), license review (all sources
      CC-BY-4.0 except WikiText CC-BY-SA local-only; VETO on artifact redistribution),
      frozen EXPERIMENT_SPEC + DEVIATIONS. Methodologist code gaps all fixed.
- [x] **Phase 2 corpus**: byte-matched 32 MiB General/Azure/Mixed; leakage-audited
      (union-find split groups, near-dup removal, general exact-dedup, cross-corpus filter).
- [x] **Phase 3 tokenizer pilot**: 16K General/Azure/Mixed; round-trip 100% / 0 UNK;
      red-team review (two passes) — blockers resolved; `research/PILOT_REVIEW.md`.
- [x] **Phase 4 full corpus + freeze**: EXPERIMENT_SPEC frozen; byte budget deviation
      (256→32 MiB, azure_train caps at 38.8 MiB) recorded in `research/DEVIATIONS.md`.
- [x] **Phase 5 full matrix**: nine controlled tokenizers trained with provenance + checksums.
- [x] **Phase 6 compression + fragmentation**: 12 encoders × 9 eval sets = 59,160 rows;
      fragmentation + vocab-utilization tables.
- [x] **Phase 7 runtime benchmark**: serialized, 5 rounds, randomized order, raw obs preserved.
- [x] **Phase 8 statistics**: paired bootstrap (10k), by eval_set / content_type / repository.
- [x] **Phase 9 report**: FINAL_REPORT.md (14 sections), ARTICLE_DRAFT.md, 7 notebooks,
      figures + source tables; `verify_all.sh` = OK.

## Active tasks

- (none — study complete)

## Blocked

- (none)

## Best next action

- Study is complete per plan.md §32. Optional enhancements only:
  1. `scale` run (96 MiB) — first expand the azure-docs sparse-checkout to more of the
     144 `articles/` services, then `msdocs-tok acquire/audit/train/... --profile scale`.
  2. Regenerate any figure PNGs from the committed `results/tables/*` source tables.
- To reproduce the pilot slice from a clean checkout: `uv sync && make acquire-pilot audit-pilot train-pilot evaluate-pilot analyze report verify`.
- To reproduce the completed matrix: `uv sync && make acquire-full audit-full train-all evaluate-all && PROFILE=full make analyze report verify` (equivalently use `msdocs-tok ... --profile full`).

## Last verified commands

- `uv run pytest -q -m "not network"` → **67 passed** (2026-07-10)
- `uv run msdocs-tok verify --profile full` → **8/8 all_ok=True**
- `bash scripts/verify_all.sh full` → **OK**
- `bash scripts/doctor.sh` → OK

## Key decisions (see DECISIONS.md)

- General-English control = Wikipedia-derived **wikitext-103-raw** (HF `Salesforce/wikitext`).
- External technical control = **kubernetes/website** `content/en/docs` (CC-BY-4.0).
- Azure anchor = **MicrosoftDocs/azure-docs** `articles/*` (CC-BY-4.0), 20 diverse services.
- Byte-level BPE via HF `tokenizers`; NFC; no lowercasing; special tokens count toward vocab.

## Artifacts index

- Plan: `plan.md` · Decisions: `DECISIONS.md` · Findings: `FINDINGS.md` · Log: `RUN_LOG.md`
- Queue: `work_queue.jsonl` · Roles: `.agents/roles/` · Task schema: `.agents/task_contract.schema.json`
- Config: `configs/experiment.yaml`, `configs/sources.yaml`
- Code: `src/msdocs_tokenizer/` · Tests: `tests/` · Harness: `Makefile`, `scripts/`
- Provenance: `data/manifests/sources.lock.json`, `artifacts/tokenizers/*.json` (9 tokenizers)
- Results: `results/tables/`, `results/figures/`, `results/processed/`, `results/raw/eval_rows.parquet`,
  `results/reports/FINAL_REPORT.md`, `results/reports/ARTICLE_DRAFT.md`, `results/reports/VERIFICATION.md`
- Review: `research/PILOT_REVIEW.md` (red-team, two passes)

## Results snapshot (full matrix, 32 MiB, leakage-clean)

- Primary (Azure vs General, cross-service holdout, 16K): **+36.68%** token reduction, CI [35.77, 37.62], win 1.0, n=964.
- General-English regression: **-34.75%**. Mixed: +34.21% on Azure, only -4.4% English.
- Vocab sensitivity: 8K/16K/32K reductions 36.46/36.68/35.41%; absolute tokens fall with vocab.
- Fragmentation: Azure fragments resource-providers/URLs/CLI/identifiers ~2x less. Vocab used: Azure 82% vs General 48%.
- Runtime (separate): Track A ~5.4 MB/s vs tiktoken 11-19 MB/s.
- Leakage controls: general exact-dedup (134 removed) + cross-corpus near-dup eval filter (9 removed); byte-match spread 0; verify 8/8.

## Remaining to close the study

- [x] Red-team: two passes; blockers 1&2 RESOLVED, blocker 3 resolved (stale smoke artifacts removed + verify gate). See research/PILOT_REVIEW.md.
- [x] FINAL_REPORT.md (14 sections), ARTICLE_DRAFT.md, 7 notebooks (execute clean), figures + source tables.
- [x] `bash scripts/verify_all.sh` = OK. Optional `scale` (96 MiB) run remains available if more Azure services are acquired.
