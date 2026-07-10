# Author and Submission Inputs Requiring Human Approval

> plan-2.md §23, §27. These decisions require the author. The agent must NOT
> fabricate any of these values, and must NOT push, release, mint a DOI, or
> submit to arXiv without explicit approval. Placeholders (`<...>`) remain in
> `CITATION.cff`, `paper/metadata/authors.example.yaml`, and the paper title
> page until the author supplies real values.

## Author identity (currently placeholders)

| Field | Needed value | Status |
|---|---|---|
| Legal author name | `<AUTHOR LEGAL NAME>` | REQUIRED |
| Preferred publication name | `<AUTHOR PUBLICATION NAME>` | REQUIRED |
| Email | `<AUTHOR EMAIL>` | REQUIRED |
| ORCID | `<0000-0000-0000-0000>` | optional but recommended |
| Affiliation | `<AFFILIATION>` | REQUIRED |
| Copyright holder (LICENSE) | currently "The msdocs-tokenizer study authors" | confirm/replace |

## Affiliation and employer review

- **Microsoft affiliation:** If the author is employed by Microsoft, state the
  relationship accurately if listed. Do **not** claim Microsoft sponsorship or
  endorsement. This study uses only public documentation and is **not** an
  official Microsoft result. **Check applicable employer publication-review
  requirements before submission.** — HUMAN GATE.
- Coauthors and contribution approval: `<none / list>` — REQUIRED if any.
- Acknowledgments: `<optional>`.
- Funding: `<none / list>`.
- Conflicts of interest: `<state, e.g., employment>`.

## Submission decisions

| Field | Recommendation | Status |
|---|---|---|
| Primary arXiv category | `cs.CL` (recommended) | confirm |
| Cross-list categories | `cs.LG`, `cs.AI`, `cs.CE` (candidates — investigate, do not assume) | confirm |
| Paper license | e.g., CC BY 4.0 or arXiv default (`arXiv.org perpetual, non-exclusive`) | REQUIRED — HUMAN GATE |
| Final title | choose among plan-2 §15 candidates (literature+writing agents recommend) | confirm |
| Final abstract | draft in `paper/metadata/abstract.txt` | confirm |
| Repository URL | `<https://github.com/<user>/<repo>>` | REQUIRED for CITATION/paper |
| Release DOI (Zenodo etc.) | `<none / DOI>` | optional |
| Distribute generated tokenizers? | Azure-only = OK w/ attribution; General/Mixed = local-use-only (legal review) | confirm |
| Anonymous vs named pre-review copies | `<preference>` | optional |

## Actions blocked pending approval (plan-2.md §27)

- `git push` / publishing to GitHub
- Creating a GitHub release or tag intended for publication
- Minting a DOI
- Submitting to arXiv
- Any destructive git-history rewrite
