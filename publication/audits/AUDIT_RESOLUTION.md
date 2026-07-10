# Audit Blocker Resolution (Phase A)

Tracks how each publication-blocking audit finding was resolved. Audit reports
themselves are preserved as authored under `publication/audits/`.

## Secret scan — PASS (no blockers)

- `SECRET_SCAN.md`: no secrets; 20 "Hex High Entropy String" hits are SHA-256
  provenance hashes + git commit SHAs. Baseline `.secrets.baseline` records them.

## License audit — 4 blockers → RESOLVED

| # | Blocker | Resolution |
|---|---|---|
| 1 | `fabric-docs` missing license/attribution record | Added row to `licenses/SOURCE_LICENSES.csv` + section to `licenses/ATTRIBUTION.md` (CC-BY-4.0; LICENSE/LICENSE-CODE/ThirdPartyNotices verified present via gh api; pinned `e8925d8…`). |
| 2 | `microsoft-365-docs` missing license/attribution record | Added row + attribution (CC-BY-4.0; files verified; pinned `eab9d76…`, default branch `public`). |
| 3 | WikiText lock revision mismatch (`hf:main` vs reviewed README rev) | Documented in `licenses/RESTRICTIONS.md` (acquisition used dataset `main`; license reviewed at `b08601e…`; pin revision for exact repro). WikiText + General/Mixed artifacts remain VETOED/local-use-only. Not a redistribution path. |
| 4 | No top-level `LICENSE` | Added `LICENSE` (MIT, matching `pyproject.toml`) scoped to original code/writing only, explicitly excluding third-party corpora, generated tokenizer artifacts, trademarks, and the paper (paper license = author gate). |

Also: `*.corpus.txt` added to `.gitignore`; PowerShell-Docs annotated as
reviewed-but-not-selected in `RESTRICTIONS.md`.

## Reproducibility audit — 1 blocker → RESOLVED

- `make verify` previously rewrote `results/reports/VERIFICATION.md` with a
  wall-clock timestamp (dirtied the worktree). Fixed `run_verify` to emit a
  fully deterministic report (no timestamp/commit). Verified idempotent (running
  `verify` twice produces no diff). All plan-2 §12 Make targets present.

## Repository audit — 3 blockers → RESOLVED / in-progress

| # | Blocker | Resolution |
|---|---|---|
| 1 | Absolute machine paths in tracked manifests/docs | Fixed `corpus.build_corpus_file` to store repo-relative paths; surgically sanitized the `path` field in `data/manifests/{azure,general,mixed}.corpus.json` and `research/PILOT_REVIEW.md` (no scientific values changed). `git grep /Users/johnsonshi` over tracked non-publication files = clean. |
| 2 | `uv.lock` not tracked (excluded by the user's *global* `~/.gitignore_global` `*.lock`) | `git add -f uv.lock` — now tracked for reproducible installs. |
| 3 | Worktree not release-clean / some publication Make targets unreliable from a fresh clone | Worktree becomes clean after the Phase-A commit. `verify-claims` + `figures` targets work now; `paper`/`paper-check`/`arxiv-package` are implemented in Phases E–G (paper/Makefile). `publication-verify` script added in Phase C. |

Repo audit's 12 should-fix + 6 nice-to-have (missing README/doc sections,
result docs) are addressed in Phase B (repository information architecture).

## Verification after fixes

- `uv run pytest -q -m "not network"` → 67 passed
- `uv run msdocs-tok verify --profile full` → 8/8 (idempotent)
- `uv run python scripts/verify_claims.py` → 43/43

**No experiment result was altered.** Only provenance-path formatting and the
verify-report format changed (both non-scientific).
