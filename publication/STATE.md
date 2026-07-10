# Publication STATE

> Canonical publication-prep state (plan-2.md §4.4). A fresh agent resumes from
> this file + repository state alone. Keep concise.

- **Updated:** 2026-07-10T14:40-07:00
- **Branch:** `publication/arxiv-prep` (experiment preserved on `main`; snapshot tag `experiment-full-verified-20260709` → commit a7d0301)
- **Phase:** **ALL PHASES A–G COMPLETE.** Publication-ready pending human-only gates. `make publication-verify` OK (11/11); claim registry 44/44; arXiv package builds clean-room; all 5 independent reviews PASS/GO.
- **Scientific record:** FROZEN. Do not rerun/alter the experiment. Primary = 36.68% (Azure vs General, 16K, azure_cross_service_holdout; CI [35.77,37.62]; win 1.0; n=964).

## Phase gates (plan-2.md §26)

- [x] **Phase A** preserve + audit: snapshot ✓, branch ✓, claim registry ✓ (44 claims, 44/44 PASS), 5 audits ✓, blockers resolved ✓ (`publication/audits/AUDIT_RESOLUTION.md`), 6 publication figures ✓ (`scripts/make_figures.py`).
- [x] **Phase B** repository IA: README ✓, docs/ (8) ✓, results/README+DATA_DICTIONARY ✓, notebooks cleaned+executed ✓, community files ✓, LICENSE/CITATION ✓, Make targets ✓, publication_verify ✓.
- [x] **Phase C** figures + claim verification + artifact review (GO). Part I public-artifact quality gate PASSED.
- [x] **Phase D** literature review: 26 verified citations (0 unresolved), paper/references.bib + paper/literature/*.
- [x] **Phase E** manuscript draft (LaTeX): main.tex + 11 sections + 6 appendices; `make -C paper paper` compiles (17 pp, 0 undefined refs); `make -C paper check` 6/6.
- [x] **Phase F** independent reviews: statistical **PASS**, method red team **PASS** (0 blockers), claim red team **PASS** (final iteration 2; blockers + citation mismatch fixed), citation verification **PASS** (26/26).
- [x] **Phase G** arXiv package: `paper/arxiv/{arxiv-source.tar.gz,MANIFEST.md,compiled-paper.pdf,build-log.txt,submission-checklist.md}` produced; clean-room pdflatex-only build (bundled `.bbl`) → 17 pp, 0 undefined, fonts embedded; `publication/FINAL_VERIFICATION.md` reconciles §30 DoD (15/15). **STOPPED before submission** (human gates in `AUTHOR_INPUTS_REQUIRED.md`).

## Best next action

**Agent scope complete.** Remaining items are human-only (see
`publication/AUTHOR_INPUTS_REQUIRED.md` and `paper/arxiv/submission-checklist.md`
Part C): author identity/affiliation/ORCID, employer publication review, paper
license, final title/category confirmation, repository URL, and explicit approval
to push / release / mint DOI / submit to arXiv. Do NONE of these without the user.

## Claim registry

- Source of truth: `publication/claims.yaml` (44 claims). Verifier: `scripts/verify_claims.py` (`make verify-claims`). Evidence: `publication/claim_evidence.csv`. Status: 44/44 PASS.
- Rule: no number in README/docs/figures/tables/paper unless registered + passing.

## Human-approval gates (do NOT do without user)

- Author identity/affiliation/ORCID/email; employer publication review; paper license; final title; arXiv category/endorsement; GitHub publish/release/DOI; arXiv submission.
- Tracked in `publication/AUTHOR_INPUTS_REQUIRED.md` (to be created in Phase B/G).

## Key artifacts

- Plan: `plan-2.md` · Ledgers: `publication/{DECISIONS,CLAIM_LEDGER,OPEN_ISSUES,REVIEW_LOG}.md`, `publication/work_queue.jsonl`
- Audits: `publication/audits/` · Reviews: `publication/reviews/`
- Experiment (frozen): `results/`, `data/manifests/`, `artifacts/tokenizers/*.json`, `research/`
