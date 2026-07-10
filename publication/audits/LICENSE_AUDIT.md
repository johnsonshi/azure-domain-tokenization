# License audit

Date: 2026-07-10. This is not legal advice.

Read-only evidence used: `data/manifests/sources.lock.json`, `licenses/SOURCE_LICENSES.csv`, `licenses/ATTRIBUTION.md`, `licenses/RESTRICTIONS.md`, `plan-2.md` §13, `artifacts/tokenizers/*.json`, `.gitignore`, and `git ls-files`.

## Verdict

**LICENSE AUDIT: 4 blockers**

1. `MicrosoftDocs/fabric-docs` is in `data/manifests/sources.lock.json` but has no row in `licenses/SOURCE_LICENSES.csv` and no paste-ready entry in `licenses/ATTRIBUTION.md`.
2. `MicrosoftDocs/microsoft-365-docs` is in `data/manifests/sources.lock.json` but has no row in `licenses/SOURCE_LICENSES.csv` and no paste-ready entry in `licenses/ATTRIBUTION.md`.
3. `Salesforce/wikitext` is recorded in `sources.lock.json` as `commit_sha: hf:main`; `licenses/SOURCE_LICENSES.csv` cites reviewed Hugging Face README revision `b08601e04326c79dfdd32d625aee71d232d685c3`. The source lock is not pinned to the reviewed licensing revision.
4. No top-level `LICENSE`/`COPYING` file is tracked for the repository's original code and writing, although `plan-2.md` §13 requires `LICENSE` for original repository code and writing.

## GO / NO-GO

| Release decision | Result | Reason |
|---|---:|---|
| Publish scripts + manifests + hashes + aggregate results | **NO-GO until blockers fixed** | The intended publication path avoids raw corpus redistribution, but source license/attribution records are incomplete for two manifest sources, WikiText revision pinning is inconsistent, and the repository lacks its own top-level license. |
| Distribute Azure tokenizer artifact | **GO with attribution** | All `azure-bytebpe-*.json` metadata has `distributable: true` and states CC-BY-4.0 Azure documentation with attribution; `licenses/RESTRICTIONS.md` permits tokenizer artifacts trained solely from CC-BY-4.0 documentation sources with attribution. |
| Do not distribute raw corpora / General+Mixed artifacts | **GO / required** | `licenses/RESTRICTIONS.md` says no raw corpora are committed and vetoes WikiText-only or mixed-with-WikiText tokenizer artifacts. All General/Mixed metadata has `distributable: false` and local-use-only notes. |

## Per-source cross-check

| Source in lock | Role | Acquisition / pin in `sources.lock.json` | License record status | License | Redistribution: raw text | Redistribution: tokenizer artifact | Redistribution: scripts + hashes + aggregates |
|---|---|---|---|---|---|---|---|
| `MicrosoftDocs/azure-docs` | anchor | sparse git clone; `80e8be2fca4160d1ff2528ae84bbf96f4a90d46e` | Present; repo, commit, license, attribution, raw/tokenizer/script status match. | CC-BY-4.0 docs; MIT code | License allows with attribution, but project policy is **NO-GO to commit raw text**. | **GO** for Azure-only artifacts with attribution. | **GO** |
| `MicrosoftDocs/architecture-center` | transfer | GitHub API deterministic selection; `9bb6e65cf6b109039e966e27aad44ce71ab4120b` | Present; repo, commit, license, attribution, raw/tokenizer/script status match. | CC-BY-4.0 docs; MIT code | License allows with attribution, but project policy is **NO-GO to commit raw text**. | **GO** if trained solely with CC-BY-4.0 sources and attribution. | **GO** |
| `MicrosoftDocs/azure-devops-docs` | transfer | GitHub API deterministic selection; `83e590364fe13aab331d166cab63b5cbea0b35ab` | Present; repo, commit, license, attribution, raw/tokenizer/script status match. | CC-BY-4.0 docs; MIT code | License allows with attribution, but project policy is **NO-GO to commit raw text**. | **GO** if trained solely with CC-BY-4.0 sources and attribution. | **GO** |
| `MicrosoftDocs/sql-docs` | transfer | GitHub API deterministic selection; `b1212537b039d992f1acafa81747239794ff32a1` | Present; repo, commit, license, attribution, raw/tokenizer/script status match. | CC-BY-4.0 docs; MIT code | License allows with attribution, but project policy is **NO-GO to commit raw text**. | **GO** if trained solely with CC-BY-4.0 sources and attribution. | **GO** |
| `MicrosoftDocs/fabric-docs` | transfer | GitHub API deterministic selection; `e8925d869c90b57daf9a41b984f16b3636d227ac` | **Missing from `SOURCE_LICENSES.csv`; missing from `ATTRIBUTION.md`.** | Lock says CC-BY-4.0, but no audited license row. | **NO-GO until license row/attribution added;** no raw text should be committed regardless. | **NO-GO until license row/attribution added** for any artifact depending on this source. | **NO-GO until license row/attribution added.** |
| `MicrosoftDocs/microsoft-365-docs` | transfer | GitHub API deterministic selection; `eab9d7696cdff87474698b08a1fb328091102a2f` | **Missing from `SOURCE_LICENSES.csv`; missing from `ATTRIBUTION.md`.** | Lock says CC-BY-4.0, but no audited license row. | **NO-GO until license row/attribution added;** no raw text should be committed regardless. | **NO-GO until license row/attribution added** for any artifact depending on this source. | **NO-GO until license row/attribution added.** |
| `kubernetes/website` | external_technical | GitHub API deterministic selection; `71d23f81e3479361befc94564e2b955860c03164` | Present; repo, commit, license, attribution, raw/tokenizer/script status match. | CC-BY-4.0 | License allows with attribution, but project policy is **NO-GO to commit raw text**. | **GO** if trained solely with CC-BY-4.0 sources and attribution. | **GO** |
| `Salesforce/wikitext` / `wikitext-103-raw-v1` | general_english | Hugging Face download; lock uses `hf:main`; CSV reviewed README revision `b08601e04326c79dfdd32d625aee71d232d685c3` | Present, but **revision pin mismatch**; license text is internally inconsistent in CSV/card notes. | CSV: CC-BY-SA-3.0 AND GFDL-1.3-or-later metadata; card text also says CC-BY-SA-4.0 | **NO-GO/VETO** for raw redistribution. | **NO-GO/VETO; LOCAL-USE-ONLY** for WikiText-only or mixed-corpus tokenizer artifacts pending legal review. | **GO only after pin mismatch is resolved;** preferred path remains scripts/manifests/hashes/aggregates, not raw text/artifacts. |

Notes: `licenses/SOURCE_LICENSES.csv` has no dedicated `role` or `acquisition_method` columns; those values were cross-checked from `sources.lock.json` (`notes` and `command`). The CSV also contains `MicrosoftDocs/PowerShell-Docs`, which is not one of the 8 locked sources.

## Raw corpus tracking and ignore policy

- `git ls-files | grep -E 'data/raw|external|corpus.txt'` returned no tracked raw-corpus paths.
- `.gitignore` excludes `/external/` and `/data/raw/`.
- `git check-ignore -v external data/raw data/raw/ external/` confirmed local `external/` and `data/raw/` are ignored.
- `corpus.txt` is not explicitly listed in `.gitignore`; no tracked `corpus.txt` was found. Add an explicit ignore rule in Phase B if any workflow may generate a root or nested `corpus.txt`.

## Tokenizer artifact redistribution

- All `artifacts/tokenizers/azure-bytebpe-*.json` files carry `distributable: true` with note: trained only on CC-BY-4.0 Azure documentation; redistributable with attribution.
- All `artifacts/tokenizers/general-bytebpe-*.json` and `mixed-bytebpe-*.json` files carry `distributable: false` with note: trained on WikiText; local-use-only; do not redistribute pending legal review.
- `git ls-files artifacts/ | grep tokenizer.json` returned empty; no generated `tokenizer.json` artifact is tracked.
- This matches `licenses/RESTRICTIONS.md`: Azure/CC-BY-only tokenizer artifacts may be distributed with attribution; WikiText-only and mixed-with-WikiText artifacts are vetoed/local-use-only.

## WikiText share-alike implications

WikiText is Wikipedia-derived and `licenses/SOURCE_LICENSES.csv` / `licenses/RESTRICTIONS.md` record unresolved license-version evidence: CC-BY-SA-3.0 plus GFDL in metadata, with card text also saying CC-BY-SA-4.0. CC-BY-SA can require adaptations to use the same or a compatible license. If a tokenizer vocabulary/merge table is considered adapted material or a database extraction from WikiText, a Mixed-corpus tokenizer could inherit share-alike obligations and article-level attribution/history requirements.

This does **not** constrain the repository's own original code or paper license if the release publishes only scripts, manifests, hashes, and aggregate results and does not publish raw WikiText or WikiText-derived General/Mixed tokenizer artifacts. It **does** require keeping General/Mixed artifacts local-use-only unless legal review resolves the license version, share-alike plan, and attribution path.

## Original repository license gap

`git ls-files | grep -E '(^|/)LICENSE($|\.)|(^|/)COPYING($|\.)'` returned no top-level repository license. This violates the `plan-2.md` §13 requirement to clearly separate the original code/writing license from third-party documentation licenses, generated-tokenizer redistribution status, and raw-corpus redistribution status. Phase B should add a top-level `LICENSE` for the repository's original code/writing and avoid implying that it licenses third-party corpus content.

## Attribution completeness

`licenses/ATTRIBUTION.md` provides paste-ready attribution for:

- `MicrosoftDocs/azure-docs`
- `MicrosoftDocs/architecture-center`
- `MicrosoftDocs/azure-devops-docs`
- `MicrosoftDocs/sql-docs`
- `kubernetes/website`
- `Salesforce/wikitext` / `wikitext-103-raw-v1`

It does **not** provide paste-ready attribution for the locked sources `MicrosoftDocs/fabric-docs` or `MicrosoftDocs/microsoft-365-docs`. It also contains `MicrosoftDocs/PowerShell-Docs`, which is not present in `sources.lock.json`.

## License files cited/read

- `licenses/SOURCE_LICENSES.csv`
- `licenses/ATTRIBUTION.md`
- `licenses/RESTRICTIONS.md`
- `data/manifests/sources.lock.json`
- `plan-2.md` §13
- `artifacts/tokenizers/*.json`
- `.gitignore`
