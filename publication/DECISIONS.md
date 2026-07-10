# Publication DECISIONS

> Append-only decision log for publication preparation (plan-2.md §4.4).

### 2026-07-10 · PD-0001 · Preserve verified snapshot on a dedicated branch
- **Decision:** Tag the verified experiment (`a7d0301`) as `experiment-full-verified-20260709`; do all publication work on branch `publication/arxiv-prep`. Never rewrite raw results in place.
- **Evidence:** plan-2.md §4.1. `git describe` = experiment-full-verified-20260709-1-gc37ad07.
- **Revisit:** only on a publication-blocking scientific defect (would require user consent to alter the experiment).

### 2026-07-10 · PD-0002 · Programmatic claim registry as single source of truth
- **Decision:** `publication/claims.yaml` (39 claims) + `scripts/verify_claims.py`. Each claim's `display_value` is frozen from its authoritative `source_file` and re-checked within `tolerance`. No public number may appear unless registered and passing.
- **Alternatives:** hand-maintained numbers in prose (rejected — drift risk).
- **Evidence:** plan-2.md §4.2, §12. Initial run 39/39 PASS.
- **Revisit:** extend when new public numbers (e.g., runtime min/max, corpus table) are introduced.

### 2026-07-10 · PD-0003 · Toolchain choices
- **Decision:** LaTeX via local TeX Live (`pdflatex`/`latexmk`/`bibtex`/`biber` present). Secret scanning via `detect-secrets` (installed as a dev tool; no cloud upload). Experiment-design diagram via TikZ (paper) + Mermaid (README) since Graphviz `dot` is absent.
- **Evidence:** plan-2.md §5 (local secret scan only), §10, §22. Env probe this session.
- **Revisit:** if a target-venue LaTeX template is later chosen.

### 2026-07-10 · PD-0004 · Numbers reconcile to files, not to plan-2 §1
- **Decision:** All display values are extracted from `results/` files, not copied from plan-2 §1. (They matched plan-2 §1, which itself used the verified files.)
- **Evidence:** plan-2.md §1 preamble ("Do not copy numbers … without reconciling"). Verified via build_claims + verify_claims.

### 2026-07-10 · PD-0005 · Link checker ignores Markdown inside code spans
- **Decision:** `scripts/publication_verify.py::check_links` strips fenced (```` ``` ````) and inline (`` ` ``) code before scanning for relative links. A `` `![alt](path)` `` embed quoted inside backticks in a review doc is literal text, not a live link, so it must not be resolved/flagged. This removed a false-positive "broken link" (`ARTIFACT_REVIEW.md -> results/figures/fig01_primary.png`) without weakening real link checks.
- **Alternatives:** rewrite the review-doc text to avoid `](...)` (rejected — recurs whenever docs legitimately quote Markdown); resolve links from repo root (rejected — breaks standard file-relative semantics).
- **Evidence:** CommonMark treats code-span content as literal; `make publication-verify` → OK (11/11) after the fix.
- **Revisit:** if a doc needs a real link that only appears inside a code span (none today).

### 2026-07-10 · PD-0006 · arXiv packaging = local preflight only, stop before submission
- **Decision:** Phase G produces the upload archive + manifest + reference PDF + build log + checklist and verifies a clean-room **pdflatex-only** build using the bundled `.bbl`. Submission itself, author metadata, license, category, employer review, push, release, and DOI are human-only gates and are NOT performed by the agent.
- **Evidence:** plan-2.md §22, §27, §30; `paper/arxiv/submission-checklist.md` Part C; `publication/AUTHOR_INPUTS_REQUIRED.md`.
- **Revisit:** on explicit user approval to submit.
