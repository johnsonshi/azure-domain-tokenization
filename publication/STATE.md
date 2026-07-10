# Publication STATE

> Canonical publication-prep state (plan-2.md §4.4). A fresh agent resumes from
> this file + repository state alone. Keep concise.

- **Updated:** 2026-07-10T12:35-07:00
- **Branch:** `publication/arxiv-prep` (experiment preserved on `main`; snapshot tag `experiment-full-verified-20260709` → commit a7d0301)
- **Phase:** PART I COMPLETE (artifact review GO) -> Part II / Phase E (manuscript). Claim registry 44/44; publication_verify 10/10; literature package 26 verified citations.
- **Scientific record:** FROZEN. Do not rerun/alter the experiment. Primary = 36.68% (Azure vs General, 16K, azure_cross_service_holdout; CI [35.77,37.62]; win 1.0; n=964).

## Phase gates (plan-2.md §26)

- [x] **Phase A** preserve + audit: snapshot ✓, branch ✓, claim registry ✓ (43 claims, 43/43 PASS), 5 audits ✓, blockers resolved ✓ (`publication/audits/AUDIT_RESOLUTION.md`), 6 publication figures ✓ (`scripts/make_figures.py`).
- [~] **Phase B** repository IA: README ✓, docs/ (8) ✓, results/README+DATA_DICTIONARY ✓, notebooks cleaned+executed ✓, community files ✓, LICENSE/CITATION ✓, Make targets ✓, publication_verify 9/9 ✓. Remaining: artifact review (Phase C gate).
- [x] **Phase C** figures + claim verification + artifact review (GO). Part I public-artifact quality gate PASSED.
- [x] **Phase D** literature review: 26 verified citations (0 unresolved), paper/references.bib + paper/literature/*.
- [~] **Phase E** manuscript draft (LaTeX) — starting.
- [ ] **Phase F** independent reviews (statistical, method red team, claim red team, citation, reproducibility)
- [ ] **Phase G** arXiv package (stop before submission)

## Best next action

1. Run Phase-A audit sub-agents (repository, license, secret-scan, link-check, reproducibility) → `publication/audits/*`.
2. Resolve any publication-blocking findings.
3. Phase B: README rewrite + `docs/` + results dictionary.

## Claim registry

- Source of truth: `publication/claims.yaml` (39 claims). Verifier: `scripts/verify_claims.py` (`make verify-claims`). Evidence: `publication/claim_evidence.csv`. Status: 39/39 PASS.
- Rule: no number in README/docs/figures/tables/paper unless registered + passing.

## Human-approval gates (do NOT do without user)

- Author identity/affiliation/ORCID/email; employer publication review; paper license; final title; arXiv category/endorsement; GitHub publish/release/DOI; arXiv submission.
- Tracked in `publication/AUTHOR_INPUTS_REQUIRED.md` (to be created in Phase B/G).

## Key artifacts

- Plan: `plan-2.md` · Ledgers: `publication/{DECISIONS,CLAIM_LEDGER,OPEN_ISSUES,REVIEW_LOG}.md`, `publication/work_queue.jsonl`
- Audits: `publication/audits/` · Reviews: `publication/reviews/`
- Experiment (frozen): `results/`, `data/manifests/`, `artifacts/tokenizers/*.json`, `research/`
