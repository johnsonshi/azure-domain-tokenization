# Author and Submission Inputs Requiring Human Approval

> plan-2.md §23, §27. These decisions require the author. The agent must NOT
> fabricate any of these values. **Author identity, ORCID, affiliation, final
> title, and repository URL were confirmed by the author on 2026-07-10** and have
> been written into `CITATION.cff`, `paper/metadata/authors.yaml`, the LaTeX
> title/author block, and the README. The remaining **open human gates** are:
> employer publication review, paper license choice, and the explicit decision to
> submit to arXiv / mint a DOI. The user authorized creating and publishing the
> GitHub repository on 2026-07-10.

## Author identity (CONFIRMED 2026-07-10)

| Field | Value | Status |
|---|---|---|
| Legal author name | Johnson Shi | ✅ confirmed |
| Preferred publication name | Johnson Shi | ✅ confirmed |
| Email (corresponding) | johnsonshi86@gmail.com | ✅ confirmed |
| Email (alternate) | johnson.shi@microsoft.com | ✅ confirmed |
| ORCID | 0009-0001-2638-6007 | ✅ confirmed |
| Affiliation | Microsoft | ✅ confirmed |
| Copyright holder (LICENSE) | Johnson Shi | ✅ set |

## Affiliation and employer review

- **Microsoft affiliation:** The author is employed by Microsoft; the affiliation
  is stated accurately. The paper and repo do **not** claim Microsoft sponsorship
  or endorsement, and state that this is not an official Microsoft result.
  **Applicable employer publication-review requirements must be satisfied before
  public submission/release.** — HUMAN GATE (open).
- Coauthors and contribution approval: none (single author).
- Acknowledgments: `<optional>`.
- Funding: none stated.
- Conflicts of interest: the author is employed by Microsoft, the vendor of the
  studied documentation (stated in the paper's non-endorsement note).

## Submission decisions

| Field | Recommendation | Status |
|---|---|---|
| Primary arXiv category | `cs.CL` (recommended) | confirm |
| Cross-list categories | `cs.LG`, `cs.AI`, `cs.CE` (candidates — investigate, do not assume) | confirm |
| Paper license | e.g., CC BY 4.0 or arXiv default (`arXiv.org perpetual, non-exclusive`) | **REQUIRED — HUMAN GATE (open)** |
| Final title | Domain-Specialized Byte-Level BPE for Technical Documentation: Compression Gains and General-English Tradeoffs | ✅ confirmed |
| Final abstract | `paper/metadata/abstract.txt` (revised 2026-07-10) | ✅ confirmed |
| Repository URL | `https://github.com/johnsonshi/azure-domain-tokenization` | ✅ confirmed |
| Release DOI (Zenodo etc.) | `<none / DOI>` | optional |
| Distribute generated tokenizers? | Azure-only = OK w/ attribution; General/Mixed = local-use-only (legal review) | confirm |
| Anonymous vs named pre-review copies | `<preference>` | optional |

## Actions blocked pending approval (plan-2.md §27)

- `git push` / publishing to GitHub
- Creating a GitHub release or tag intended for publication
- Minting a DOI
- Submitting to arXiv
- Any destructive git-history rewrite
