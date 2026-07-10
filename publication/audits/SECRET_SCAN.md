# Secret Scan

**Scope:** worktree (tracked files) + full git history on all branches.
**Tool:** `detect-secrets` 1.5.0 (local only — no repository contents uploaded to any third-party scanner, per plan-2.md §5).
**Date:** 2026-07-10. **Branch:** `publication/arxiv-prep`.

## Result: ✅ NO SECRET BLOCKERS

No credentials, private keys, API keys, or tokens were found in tracked files or git history.

### `detect-secrets scan` (tracked files)

20 files were flagged for **"Hex High Entropy String"**. Every hit is a **provenance hash**, not a secret:

- `artifacts/tokenizers/*.json` (lines 4, 5, 31): `artifact_sha256`, `config_sha256`, `training_manifest_sha256` — SHA-256 content hashes of the trained tokenizer artifacts and configs (reproducibility provenance).
- `data/manifests/*.json` and `data/manifests/locks/*.json`: `commit_sha` (40-hex git commit SHAs of pinned public sources) and `sha256` content hashes.

Example (confirmed benign):
```
"artifact_sha256": "e678e2df0227eb118a772affbd24dd3a728655c6649620753074b6108cbd9a41"
"commit_sha": "80e8be2fca4160d1ff2528ae84bbf96f4a90d46e"
```

These are intentional, publishable checksums and pinned commit identifiers required for reproducibility. They are recorded as audited non-secrets in `.secrets.baseline`.

### Git-history credential scan

Bounded pattern scan across `git log --all -p` for GitHub tokens (`gh[pousr]_…`), AWS keys (`AKIA…`), private-key blocks (`BEGIN … PRIVATE KEY`), Slack tokens (`xox…`), and `password/secret/api_key = "<literal>"` assignments:

- **0 matches.** No real credentials in history.

### Machine paths / usernames

- No local absolute paths (`/Users/johnsonshi`, `/home/…`) are hard-coded in tracked source, configs, or docs (excluding lockfiles and this `publication/` audit trail). Any incidental username appears only in git author metadata and commit trailers, which is expected and non-sensitive.

## Baseline

`.secrets.baseline` was generated so `detect-secrets scan --baseline .secrets.baseline` and pre-commit hooks treat the provenance hashes as known non-secrets. CI/reviewers should re-run `detect-secrets scan $(git ls-files)` and diff against the baseline.

## Verdict

**PASS** — no publication-blocking secret findings. Note: raw corpora and the local git clone (`external/`, `data/raw/`) are git-ignored and were never committed, so they cannot leak.
