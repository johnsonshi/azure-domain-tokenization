# Repository audit

Audit target: `plan-2.md` §5 (`plan-2.md:300-331`) for public/arXiv release readiness. The experiment itself is treated as frozen; this audit did not edit code, configs, or results.

Validation commands used included `git ls-files`, `git status --short --untracked-files=all`, `wc`, `du`, `uv lock --check`, `uv sync --locked --dry-run`, and `uv run python scripts/verify_claims.py`.

## Overall verdict

The scientific result tables and claim registry are largely coherent: `scripts/verify_claims.py` reported **39/39 claims passed**, and `uv lock --check` plus `uv sync --locked --dry-run` were clean in the current machine environment. The repository is **not yet public-release clean** because release-critical generated files are untracked, some publication Make targets fail or depend on untracked files, and tracked provenance contains machine-local absolute paths.

## Findings

### BLOCKER-1 — Worktree is not release-clean

- **Severity:** BLOCKER
- **File:** worktree state from `git status --short --untracked-files=all`
- **Evidence:** `git status --short --untracked-files=all` is not clean. At final audit verification it showed modified `licenses/ATTRIBUTION.md` and `licenses/SOURCE_LICENSES.csv`, plus untracked `LICENSE`, `scripts/make_figures.py`, `publication/audits/LICENSE_AUDIT.md`, `publication/audits/REPRODUCIBILITY_AUDIT.md`, `results/figures/FIGURES.md`, six new `results/figures/*.png`, six `paper/figures/*.pdf`, and new figure/runtime tables under `results/tables/`.
- **Recommendation:** Before tagging/public release, either commit the intended generated publication artifacts and their generation script, or remove them and regenerate in Phase B. Do not release with a dirty worktree.

### BLOCKER-2 — Tracked provenance contains local absolute paths

- **Severity:** BLOCKER
- **Files:** `data/manifests/azure.corpus.json:7`, `data/manifests/general.corpus.json:7`, `data/manifests/mixed.corpus.json:7`, `research/PILOT_REVIEW.md:3`, `publication/audits/SECRET_SCAN.md:34`
- **Evidence:** The corpus manifests record `/Users/johnsonshi/repos/ai/tokenizer/data/splits/...`; `research/PILOT_REVIEW.md:3` records `uv run --project /Users/johnsonshi/repos/ai/tokenizer python`. `publication/audits/SECRET_SCAN.md:34` says no such paths are hard-coded, which is contradicted by the manifests.
- **Recommendation:** Replace machine-local path fields with repository-relative paths or explicitly label them non-portable local-run metadata. Update `SECRET_SCAN.md` after the path audit is corrected.

### BLOCKER-3 — Publication Make targets are not reliable from a fresh clone

- **Severity:** BLOCKER
- **Files:** `Makefile:85-98`, `scripts/make_figures.py:1-13`, `plan-2.md:1420-1427`
- **Evidence:** `make figures` delegates to `scripts/make_figures.py` (`Makefile:85-86`), but that script is currently untracked. `make paper`, `make paper-check`, and `make arxiv-package` delegate to `paper/Makefile` (`Makefile:88-95`), but no `paper/Makefile` is tracked. `plan-2.md:1420-1421` references `make publication-audit` and `make publication-docs`; no recipes exist.
- **Recommendation:** Commit the publication figure script and paper build system, or remove/guard these targets until implemented. Add actual recipes for `publication-audit` and `publication-docs` or remove them from the gate list.

### SHOULD-FIX-1 — `uv.lock` is present but not tracked

- **Severity:** SHOULD-FIX
- **Files:** `plan-2.md:351-364`, user/global ignore rule `*.lock`
- **Evidence:** `plan-2.md` target layout includes `uv.lock` (`plan-2.md:363`). `uv.lock` exists locally and `uv lock --check` / `uv sync --locked --dry-run` are clean, but `git ls-files uv.lock` is empty because `/Users/johnsonshi/.gitignore_global:42` ignores `*.lock`.
- **Recommendation:** Force-add `uv.lock` (`git add -f uv.lock`) or add a repository-level negated rule if needed. Public reproducibility should not depend on the auditor's local lockfile.

### SHOULD-FIX-2 — Required public docs directory is absent

- **Severity:** SHOULD-FIX
- **Files:** `plan-2.md:370-378`, `plan-2.md:460-579`
- **Evidence:** The target information architecture requires `docs/experiment-design.md`, `docs/methodology.md`, `docs/datasets-and-licenses.md`, `docs/reproducibility.md`, `docs/results.md`, `docs/limitations.md`, `docs/repository-map.md`, and `docs/artifact-evaluation.md`; no `docs/` directory exists.
- **Recommendation:** Create the required docs or intentionally revise `plan-2.md` to point to existing `research/`, `results/reports/`, and `licenses/` documents.

### SHOULD-FIX-3 — README is accurate but incomplete against the publication plan

- **Severity:** SHOULD-FIX
- **Files:** `README.md:1-62`, `plan-2.md:415-453`
- **Evidence:** The README states the core result and quick-start commands, but plan-2 requires a compact results table, one primary figure above the fold, experimental design diagram, paper/citation sections, author/affiliation disclaimer, exact expected resource usage, and fuller verification/licensing guidance.
- **Recommendation:** Expand README for public readers while preserving the tokenization-only caveat at `README.md:18-20` and raw-corpora caveat at `README.md:59-62`.

### SHOULD-FIX-4 — Large tracked artifacts need explicit policy

- **Severity:** SHOULD-FIX
- **Files:** `inventory/microsoftdocs_repos.json`, `results/raw/eval_rows.parquet`, `.gitignore:25-28`
- **Evidence:** `inventory/microsoftdocs_repos.json` is 5,234,259 bytes. `results/raw/eval_rows.parquet` is 897,508 bytes and is tracked even though `.gitignore:25-28` says `results/raw/*.parquet` should be ignored.
- **Recommendation:** Compress/LFS the raw inventory JSON or replace it with compact derived CSVs. Either keep `eval_rows.parquet` with a documented exception or move it to `git-lfs`/release artifacts.

### SHOULD-FIX-5 — Ignored reproduction artifacts are referenced as if they are present

- **Severity:** SHOULD-FIX
- **Files:** `research/PILOT_REVIEW.md:9-17`, `results/reports/FINAL_REPORT.md:22`, `DECISIONS.md:73`, `RUN_LOG.md:3`
- **Evidence:** Reader-visible references point to ignored files such as `data/audit/audit_summary.json`, `data/audit/*.parquet`, `data/splits/azure_splits.parquet`, `data/evaluation/eval_docs.parquet`, and `results/raw/logs`.
- **Recommendation:** Add “generated by reproduction, not committed” wording where these appear, and provide committed summaries for any public claim that depends on ignored artifacts.

### SHOULD-FIX-6 — Stale pilot review contradicts current release state

- **Severity:** SHOULD-FIX
- **Files:** `research/PILOT_REVIEW.md:9`, `results/reports/VERIFICATION.md:8-17`, `STATE.md:21-33`
- **Evidence:** `research/PILOT_REVIEW.md:9` records a **FAIL** for general-English leakage in a pilot review. Current verification says leakage controls pass (`results/reports/VERIFICATION.md:8-17`) and `STATE.md:21-33` says blockers were resolved.
- **Recommendation:** Add a dated supersession note at the top of `PILOT_REVIEW.md` or create a final red-team review so readers do not interpret the stale pilot failure as current.

### SHOULD-FIX-7 — Figure generation paths exist only partly in tracked state

- **Severity:** SHOULD-FIX
- **Files:** `src/msdocs_tokenizer/pipeline.py:673-725`, `scripts/make_figures.py:60-65`, `results/figures/FIGURES.md:1-21`
- **Evidence:** Tracked pipeline generation creates `fig01_relative_reduction.png`, `fig02_tokens_per_1k.png`, and source CSVs (`pipeline.py:673-725`). The richer publication figure script and figure manifest include six figures, PDFs, captions, alt text, and source tables (`scripts/make_figures.py:60-65`, `results/figures/FIGURES.md:1-21`), but these are currently untracked.
- **Recommendation:** Commit the richer figure generation path and outputs, or remove the untracked figure set and rely on the tracked pipeline figures. Ensure every public image has a committed source table and alt text.

### SHOULD-FIX-8 — Chart accessibility is incomplete in tracked docs

- **Severity:** SHOULD-FIX
- **Files:** `results/reports/FINAL_REPORT.md:42`, `results/figures/FIGURES.md:14-21`
- **Evidence:** The tracked final report references a PNG path but does not embed images or alt text (`FINAL_REPORT.md:42`). The untracked `FIGURES.md` provides useful alt text (`FIGURES.md:14-21`) but is not part of a fresh clone.
- **Recommendation:** Commit the figure manifest and ensure README/paper figure embeds include concise alt text or adjacent textual summaries.

### SHOULD-FIX-9 — Duplicate aggregate result table

- **Severity:** SHOULD-FIX
- **Files:** `results/processed/eval_aggregate.csv`, `results/tables/eval_aggregate.csv`
- **Evidence:** The two files have identical SHA-256 (`5e56b4f33d6976991bcfdda1cdde169fe55de1ba5b45cda81885158249533399`).
- **Recommendation:** Keep one canonical table or document why both `processed/` and `tables/` copies are needed.

### SHOULD-FIX-10 — Root-level clutter and duplicate tracking docs

- **Severity:** SHOULD-FIX
- **Files:** root tree, `publication/STATE.md`, `publication/DECISIONS.md`, `publication/OPEN_ISSUES.md`, root `STATE.md`, `DECISIONS.md`, `RUN_LOG.md`, `work_queue.jsonl`
- **Evidence:** There are 13 tracked root-level files, including run-state/tracking files intended for orchestration. There is also a second tracking set under `publication/`.
- **Recommendation:** For public release, designate a canonical public status/reproducibility document and move internal orchestration logs under `publication/` or `docs/repository-map.md` as appropriate.

### SHOULD-FIX-11 — Runtime/cost disclosure is present in reports but not in README

- **Severity:** SHOULD-FIX
- **Files:** `README.md:22-47`, `STATE.md:9-10`, `results/reports/FINAL_REPORT.md:84-100`, `plan-2.md:442-453`
- **Evidence:** `STATE.md:9-10` records runtime budget/disk/workers, and `FINAL_REPORT.md:84-100` reports CPU tokenizer throughput. README quick start/full reproduction commands do not state expected runtime, disk, network, or that full reproduction may require large downloads beyond the quick test.
- **Recommendation:** Add an expected resource-cost section to README with pilot/full runtime and disk estimates, and explicitly distinguish quick tests from full reproduction.

### SHOULD-FIX-12 — Internal-only/public terminology needs smoothing

- **Severity:** SHOULD-FIX
- **Files:** `.agents/roles/*`, root tracking docs, `publication/*`, `research/PILOT_REVIEW.md:3`
- **Evidence:** Public tree includes orchestration terminology such as sub-agent roles, red-team role labels, and local audit execution notes. These are not secrets, but they read as internal process artifacts rather than polished public documentation.
- **Recommendation:** Keep audit provenance, but introduce a public-facing `docs/repository-map.md` explaining which files are experiment artifacts vs orchestration logs.

### NICE-TO-HAVE-1 — Notebook outputs are clean

- **Severity:** NICE-TO-HAVE
- **Files:** `notebooks/*.ipynb`
- **Evidence:** All seven notebooks have zero saved outputs and zero execution counts.
- **Recommendation:** Keep this policy. Add a short `notebooks/README.md` explaining that notebooks are generated views over committed artifacts.

### NICE-TO-HAVE-2 — Dead/auxiliary scripts should be documented

- **Severity:** NICE-TO-HAVE
- **Files:** `scripts/overnight.sh:13`, `scripts/resume.sh:11`, `scripts/verify_all.sh:1-40`, `Makefile:71-72`
- **Evidence:** `verify_all.sh` is not exposed as a Make target even though it is cited in `STATE.md:56`. `overnight.sh` uses `caffeinate` unconditionally (`overnight.sh:13`), making it macOS-specific despite public release.
- **Recommendation:** Add a `make verify-all` wrapper or document direct use. Make `caffeinate` optional for non-macOS users.

### NICE-TO-HAVE-3 — Results figures include a tracked sentinel file

- **Severity:** NICE-TO-HAVE
- **File:** `results/figures/.figures_done`
- **Evidence:** A stage sentinel is tracked alongside publishable figures.
- **Recommendation:** Remove from Git or document it as a deliberate reproducibility marker; sentinels usually belong under ignored `data/.stages/`.

### NICE-TO-HAVE-4 — Package/license metadata is placeholder-like

- **Severity:** NICE-TO-HAVE
- **File:** `pyproject.toml:7-8`
- **Evidence:** `license = { text = "MIT" }` and author `msdocs-tokenizer-study` are placeholders pending public-release metadata.
- **Recommendation:** Align with `LICENSE`, `CITATION.cff`, and author-input documents once author approvals are available.

### NICE-TO-HAVE-5 — Case-sensitive path review should be part of final gate

- **Severity:** NICE-TO-HAVE
- **Files:** `results/figures/fig01_*`, `results/tables/fig01_*`, `paper/figures/fig*.pdf`
- **Evidence:** Current names are lower-case and consistent, but the repository is being prepared on Darwin, which is often case-insensitive.
- **Recommendation:** Add a final case-collision check before release (`git ls-files | sort -f | uniq -d` style).

### NICE-TO-HAVE-6 — No raw corpora or external clone are tracked

- **Severity:** NICE-TO-HAVE
- **Files:** `.gitignore:7-18`, `.gitignore:20-28`
- **Evidence:** `git ls-files` found zero tracked paths under `external/` and ignored raw/intermediate corpus trees. This matches the hard constraint in `.gitignore:1-4`.
- **Recommendation:** Preserve this gate in CI/release verification.

## Prioritized fix list

1. Make the worktree clean: decide which untracked generated artifacts/scripts are release artifacts and commit or remove them.
2. Remove or relativize `/Users/johnsonshi/...` paths from tracked manifests/docs; update the secret/path audit.
3. Fix publication Make targets (`figures`, `paper`, `paper-check`, `arxiv-package`, `publication-audit`, `publication-docs`) so they work from a fresh clone or are not advertised.
4. Force-add and verify `uv.lock` for reproducible installs.
5. Add the required public docs/README sections, especially resource-cost disclosure and reader-facing repository map.
6. Resolve large-file policy for `inventory/microsoftdocs_repos.json` and `results/raw/eval_rows.parquet`.
7. Commit or remove the richer figure manifest/alt-text outputs; ensure every figure has a source table and accessible description.
8. Supersede the stale pilot red-team failure with a final review note.
9. Mark ignored generated artifact references as reproduction-required.
10. De-duplicate result tables or document the two-copy convention.

REPOSITORY AUDIT: 3 blockers, 12 should-fix, 6 nice-to-have
