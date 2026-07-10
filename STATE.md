# STATE

> Canonical run state. Keep under 250 lines. A fresh agent must be able to resume
> from this file + repository state alone (plan.md §19).

- **Updated:** 2026-07-10T00:45-07:00
- **Phase:** 1 → 2/3 (research+discovery complete; running the corpus+tokenizer pilot)
- **Profile target:** pilot (32 MiB corpora, 16K vocab) → then full matrix if budget allows
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
      Pipeline validated end-to-end on the smoke profile.
- [ ] Phase 2 corpus pilot (running)
- [ ] Phase 3 tokenizer pilot (PILOT_REVIEW.md)
- [ ] Phase 4 full corpus + EXPERIMENT_SPEC freeze
- [ ] Phase 5 full matrix (9 tokenizers)
- [ ] Phase 6 compression + fragmentation
- [ ] Phase 7 runtime benchmark
- [ ] Phase 8 statistics
- [ ] Phase 9 report

## Active tasks

- TASK-0006 corpus_engineer → run `acquire-pilot` + `audit-pilot` (in progress)
- TASK-0007 tokenizer_engineer → `train-pilot` + `evaluate-pilot` (next)

## Blocked

- (none)

## Best next action

1. `make acquire-pilot` (git sparse azure-docs 20 services + gh_api transfer/external + wikitext).
2. `make audit-pilot` → byte-matched 32 MiB corpora + leakage audit gate.
3. `make train-pilot evaluate-pilot analyze report` → pilot results.
4. Red-team review → `research/PILOT_REVIEW.md`; then Phase 4+ (full matrix if budget).

## Last verified commands

- `uv run pytest -q` → **63 passed** (2026-07-09)
- `bash scripts/doctor.sh` → OK
- `uv run msdocs-tok --help` → OK

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
- Provenance (once run): `data/manifests/sources.lock.json`, `artifacts/tokenizers/*.json`
- Results (once run): `results/tables/`, `results/figures/`, `results/reports/FINAL_REPORT.md`
