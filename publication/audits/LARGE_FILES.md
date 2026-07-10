# Large-file audit

Scope: tracked files only (`git ls-files`), size threshold approximately 500 KiB. The ignored `external/`, `data/raw/`, `data/normalized/`, `data/segments/`, `data/splits/`, `data/evaluation/`, `data/audit/`, and `data/cache/` trees were not scanned for content.

Command basis:

```bash
git ls-files | while read -r f; do wc -c "$f"; done | sort -nr
```

## Tracked files over ~500 KiB

| Size | File | Public-repo suitability | Recommendation |
|---:|---|---|---|
| 5,234,259 bytes (5.0 MiB) | `inventory/microsoftdocs_repos.json` | Borderline. It is provenance for repository selection, but it is a raw GitHub inventory dump rather than a compact curated artifact. | **Compress or replace with a documented derived table.** Keep `inventory/repo_inventory.csv`, `inventory/repo_scores.csv`, and `inventory/SELECTION.md`; move the full JSON to a release artifact or `git-lfs` if exact raw inventory is required. |
| 897,508 bytes (876 KiB) | `results/raw/eval_rows.parquet` | Acceptable for reproducibility if intentionally published: it is the per-row source for claim verification (`scripts/verify_claims.py` verifies coverage claims against it). It conflicts with `.gitignore` intent for `results/raw/*.parquet` (`.gitignore:25-28`). | **Keep with explicit exception or move to `git-lfs`.** If kept in Git, document why this raw result table is publishable and add a negated ignore rule so future contributors understand it is intentional. |

No other tracked file exceeds ~500 KiB at scan time.

## Raw-corpus / clone tracking check

`git ls-files` found **0 tracked files** under:

- `external/`
- `data/raw/`
- `data/normalized/`
- `data/segments/`
- `data/splits/`
- `data/evaluation/`
- `data/audit/`
- `data/cache/`

This confirms the 2.2 GiB local `external/` clone and raw/intermediate corpora are not tracked.

## Unexpected large-file notes

- `uv.lock` exists locally (372 KiB) but is **not tracked** because a global ignore rule matches `*.lock`. This is not over the threshold, but it is release-relevant because `plan-2.md:351-364` expects `uv.lock` in the public repository.
- Newly generated publication figures/tables currently appear as untracked files in `git status`; individually they are below the large-file threshold, but they should be either committed intentionally or removed before release.
