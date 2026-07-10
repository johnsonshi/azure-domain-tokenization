# STATE

> Canonical run state. Keep under 250 lines. A fresh agent must be able to resume
> from this file + repository state alone (plan.md §19).

- **Updated:** 2026-07-09T23:59-07:00
- **Phase:** 0 → 1 (bootstrap complete; launching parallel research/discovery)
- **Profile target:** pilot (32 MiB corpora, 16K vocab) → then full matrix if budget allows
- **Runtime budget:** 10h. **Disk:** 607 GiB free (32% used) — well above 15% floor.
- **Workers:** 10 (max(1, 12−2)). **Seed:** 20260709.

## Completed gates

- [x] **Phase 0 bootstrap**: repo skeleton, `uv` env (Python 3.12), library, CLI,
      Makefile, scripts, fixture corpus, **63 tests passing**, `doctor.sh` green.
- [ ] Phase 1 research + discovery (in progress)
- [ ] Phase 2 corpus pilot
- [ ] Phase 3 tokenizer pilot (PILOT_REVIEW.md)
- [ ] Phase 4 full corpus + EXPERIMENT_SPEC freeze
- [ ] Phase 5 full matrix (9 tokenizers)
- [ ] Phase 6 compression + fragmentation
- [ ] Phase 7 runtime benchmark
- [ ] Phase 8 statistics
- [ ] Phase 9 report

## Active tasks

- TASK-0002 literature_researcher → research/ (sub-agent)
- TASK-0003 repo_scout → inventory/ (sub-agent)
- TASK-0004 licensing_reviewer → licenses/ (sub-agent)
- TASK-0005 methodologist → research/EXPERIMENT_SPEC.md (sub-agent)

## Blocked

- (none)

## Best next action

1. Run the four Phase-1 sub-agents in parallel (research, discovery, license, methodology).
2. Synthesize into `research/PILOT_SPEC.md`; freeze `configs/sources.yaml`.
3. `make acquire-pilot audit-pilot train-pilot evaluate-pilot analyze report verify`.

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
