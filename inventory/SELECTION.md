# Repository selection for tokenizer-efficiency evaluation

Generated: 2026-07-10. Inventory source: `gh api --paginate --slurp 'orgs/MicrosoftDocs/repos?per_page=100&type=public'`. Path verification used `gh api repos/<repo>/contents/<path>` plus subtree `git/trees/<sha>?recursive=1`; all listed repo paths below had `truncated=false` and contain `.md` files.

## Azure anchor (training corpus)

Full `MicrosoftDocs/azure-docs` is huge (`size_kb=27046986`, about 25.8 GiB) and should not be fully checked out under the 25 GiB source-disk budget. Pin and acquire only the existing sparse training paths.

| repo | branch | pinned commit | sparse paths | verified Markdown | est. cleaned Markdown | hard-filter result |
|---|---|---|---|---:|---:|---|
| MicrosoftDocs/azure-docs | main | `80e8be2fca4160d1ff2528ae84bbf96f4a90d46e` | `articles/storage`, `articles/virtual-network`, `articles/application-gateway`, `articles/frontdoor`, `articles/expressroute`, `articles/app-service`, `articles/azure-functions`, `articles/container-apps`, `articles/batch`, `articles/hdinsight`, `articles/data-factory`, `articles/synapse-analytics`, `articles/service-bus-messaging`, `articles/event-hubs`, `articles/logic-apps`, `articles/api-management`, `articles/iot-hub`, `articles/automation`, `articles/backup`, `articles/site-recovery` | 5,540 files / 62.7 MiB raw MD | ~45.1 MiB | PASS: public, unarchived, English docs, commit-pin-able, sparse checkout disk-affordable, not primarily binary/generated for selected paths. License SPDX `CC-BY-4.0`. |

## Selected MicrosoftDocs transfer set

### Stratum: Azure-adjacent architecture

| repo | branch | pinned commit | exact sparse/API paths | verified Markdown | est. cleaned Markdown | hard-filter result |
|---|---|---|---|---:|---:|---|
| MicrosoftDocs/architecture-center | main | `9bb6e65cf6b109039e966e27aad44ce71ab4120b` | `docs` | 502 files / 10.0 MiB raw MD | ~7.2 MiB | PASS: public, unarchived, English, pin-able, disk-affordable via sparse/API path, selected path is authored Markdown docs not binary/generated. License SPDX `CC-BY-4.0`. |

### Stratum: automation / DevOps

| repo | branch | pinned commit | exact sparse/API paths | verified Markdown | est. cleaned Markdown | hard-filter result |
|---|---|---|---|---:|---:|---|
| MicrosoftDocs/azure-devops-docs | main | `83e590364fe13aab331d166cab63b5cbea0b35ab` | `docs/pipelines` | 393 files / 3.1 MiB raw MD | ~2.2 MiB | PASS: public, unarchived, English, pin-able, disk-affordable via sparse/API path, not primarily binary/generated. License SPDX `CC-BY-4.0`. |

### Stratum: data / database

| repo | branch | pinned commit | exact sparse/API paths | verified Markdown | est. cleaned Markdown | hard-filter result |
|---|---|---|---|---:|---:|---|
| MicrosoftDocs/sql-docs | live | `b1212537b039d992f1acafa81747239794ff32a1` | `docs/relational-databases` | 5,099 files / 38.5 MiB raw MD | ~27.7 MiB | PASS: public, unarchived, English, pin-able, disk-affordable via sparse/API path, not primarily binary/generated. License SPDX `CC-BY-4.0`. |
| MicrosoftDocs/fabric-docs | main | `e8925d869c90b57daf9a41b984f16b3636d227ac` | `docs/data-engineering`, `docs/data-warehouse`, `docs/database/sql`, `docs/database/cosmos-db` | 509 files / 4.3 MiB raw MD | ~3.1 MiB | PASS: public, unarchived, English, pin-able, disk-affordable via sparse/API paths, not primarily binary/generated. License SPDX `CC-BY-4.0`. |

### Stratum: broad enterprise / developer documentation

| repo | branch | pinned commit | exact sparse/API paths | verified Markdown | est. cleaned Markdown | hard-filter result |
|---|---|---|---|---:|---:|---|
| MicrosoftDocs/microsoft-365-docs | public | `eab9d7696cdff87474698b08a1fb328091102a2f` | `microsoft-365/admin`, `microsoft-365/enterprise`, `microsoft-365/security` | 564 files / 4.8 MiB raw MD | ~3.4 MiB | PASS: public, unarchived, English, pin-able, disk-affordable via sparse/API paths, not primarily binary/generated. License SPDX `CC-BY-4.0`. |

## External controls

| role | source | branch/revision | pin | paths/files | verified content | est. cleaned text | notes |
|---|---|---|---|---|---:|---:|---|
| external technical | kubernetes/website | main | `71d23f81e3479361befc94564e2b955860c03164` | `content/en/docs` | 1,672 Markdown files / 14.8 MiB raw MD | ~10.6 MiB | PASS repo filters: public, unarchived, English technical docs, pin-able, disk-affordable, not primarily binary/generated for selected path. License SPDX `CC-BY-4.0`. |
| general English | Salesforce/wikitext | dataset revision to pin during acquisition | `wikitext-103-raw-v1/train-00000-of-00002.parquet` from configs | parquet text corpus | use `max_docs=20000` | n/a before acquisition | Reproducible out-of-domain English control; not a GitHub repo, so repo hard filters do not apply. License in configs: `CC-BY-SA-3.0`. |

## Path corrections versus `configs/sources.yaml`

- Keep `azure-docs` anchor sparse paths as configured; full checkout exceeds the disk budget.
- Keep `architecture-center: docs`, `azure-devops-docs: docs/pipelines`, and `sql-docs: docs/relational-databases`.
- Add `fabric-docs` as a second data/analytics transfer repo with narrow paths: `docs/data-engineering`, `docs/data-warehouse`, `docs/database/sql`, `docs/database/cosmos-db`.
- Add `microsoft-365-docs` broad-enterprise paths: `microsoft-365/admin`, `microsoft-365/enterprise`, `microsoft-365/security`.
- Defer `PowerShell-Docs: reference/7.4` until license review because current GitHub SPDX is `NOASSERTION` despite a verified Markdown path.

## License-review flags

From the scored candidates, route these to the licensing reviewer before use: `MicrosoftDocs/PowerShell-Docs` (`NOASSERTION`) and `MicrosoftDocs/memdocs` (`NOASSERTION`). No selected transfer repo above has null/NOASSERTION SPDX.
