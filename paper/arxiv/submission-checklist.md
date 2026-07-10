# arXiv Submission Checklist

> plan-2.md §22. Local packaging + preflight for the arXiv source archive.
> **This is a preflight only. No submission has been made. Do not upload without
> the human-approval items in Part C below.**
>
> Requirements reverified against the current arXiv TeX guidance
> (<https://info.arxiv.org/help/submit_tex.html>, TeX Submissions / Submission
> System 1.5, retrieved 2026-07-10) and TeX Live at arXiv.

## Package artifacts (`paper/arxiv/`)

| File | Purpose |
|---|---|
| `arxiv-source.tar.gz` | Upload archive — portable LaTeX sources + figures + `.bbl` (32 files) |
| `MANIFEST.md` | Archive contents + sha256 |
| `compiled-paper.pdf` | Reference PDF (17 pages) for the required author PDF review step |
| `build-log.txt` | pdflatex log from the clean-room rebuild |
| `submission-checklist.md` | This file |

Regenerate everything with `make -C paper arxiv` (runs tables → pdflatex → bibtex
→ pdflatex ×2 → package). Archive sha256 is recorded in `MANIFEST.md`.

## Part A — Automated / verified preflight (PASS)

| # | arXiv requirement (§22) | Status | Evidence |
|---|---|:--:|---|
| 1 | Portable LaTeX (article class, TeX Live packages only) | ✅ | `main.tex` uses `article` + `amsmath`, `booktabs`, `graphicx`, `natbib`, `hyperref`, `microtype`, `geometry` — all in arXiv's TeX Live. No custom `.sty`/`.cls` shipped. |
| 2 | No proprietary fonts; fonts embedded & readable | ✅ | `pdffonts compiled-paper.pdf`: all Type 1 (Computer Modern / cm-super), **0 non-embedded**. |
| 3 | No local absolute paths | ✅ | Relative `\input{sections/...}`, `\graphicspath{{figures/}}`; no machine paths. |
| 4 | All figures included (no external links) | ✅ | 6/6 referenced figures bundled as vector PDF; `\includegraphics` count == files. No unused figures. |
| 5 | Bibliography support file (`.bbl`) included | ✅ | `main.bbl` bundled so arXiv need not run BibTeX; `references.bib` also included for INSPIRE/harvesting. |
| 6 | Filename characters ASCII, case-exact, no spaces | ✅ | `make_arxiv_package.py` rejects non-ASCII/space filenames; all lowercase, `_`-separated. |
| 7 | No build caches / logs / aux / unrelated files | ✅ | Archive excludes `build/`, `*.aux/*.log/*.pdf` of `main`, notebooks, `external/`, `data/`, corpora. |
| 8 | Builds in a clean temporary directory | ✅ | Extracted to `mktemp -d`, compiled with **pdflatex only** (no bibtex) using the bundled `.bbl` → 17 pages. |
| 9 | References resolve (no undefined) | ✅ | Clean-room build: **0** undefined references, **0** undefined citations (`scripts/paper_check.py` 6/6). |
| 10 | Hyperlinks work | ✅ | `hyperref` loaded with auto driver (no explicit `pdftex`/`\pdfoutput`); links compile without warnings. |
| 11 | No figures omitted | ✅ | Clean-room build reports no missing-file errors; all 6 PDFs resolve via `\graphicspath`. |
| 12 | `\today` avoided in `\date` (arXiv rebuild guidance) | ✅ | `main.tex` uses `\date{2026}` (static), not `\today`. |
| 13 | Metadata title matches manuscript | ✅ | `paper/metadata/title.txt` == `\title{...}` main line in `main.tex`. |
| 14 | Metadata abstract matches manuscript | ✅ | `paper/metadata/abstract.txt` == `sections/00_abstract.tex` (numbers: 36.68 / −34.75 / +34.21 / −4.39; CI [35.77, 37.62]; win 1.000). |
| 15 | No embedded JavaScript / movies / animated GIF in PDF | ✅ | Static matplotlib-vector figures only; no `animate`/`media9`/JS. |
| 16 | Author placeholders remain obvious until author supplies details | ✅ | `\author` block + `CITATION.cff` + `authors.example.yaml` hold `<...>` placeholders; tracked in `publication/AUTHOR_INPUTS_REQUIRED.md`. |
| 17 | Full local publication gate | ✅ | `make publication-verify` → **OK (11/11)**; `make verify-claims` → 44/44. |

## Part B — Submission-time decisions (recommendation only; author confirms)

| Field | Recommendation | Where |
|---|---|---|
| Primary category | `cs.CL` | `paper/metadata/categories.md` |
| Cross-list (investigate) | `cs.LG`, `cs.AI`, `cs.CE` | `paper/metadata/categories.md` |
| TeX processor | pdfLaTeX (auto-detected by arXiv) | — |
| Report-no / comments | optional | — |

## Part C — Human-only gates (BLOCKING — do NOT proceed without the author)

These are **not** automatable and must be completed by the author before upload
(see `publication/AUTHOR_INPUTS_REQUIRED.md`):

- [ ] Real author name, email, affiliation, ORCID (replace all `<...>` placeholders).
- [ ] **Employer publication review** completed if applicable (this is public-docs
      research, **not** an official Microsoft result; claim no sponsorship/endorsement).
- [ ] Paper **license** chosen (e.g., CC BY 4.0 vs arXiv default perpetual non-exclusive).
- [ ] Final **title** and **abstract** confirmed.
- [ ] arXiv **category** + any cross-lists confirmed; arXiv endorsement in place if required.
- [ ] Repository URL finalized in `CITATION.cff` and the paper.
- [ ] Author has **viewed the arXiv-generated PDF** during submission (arXiv requires this).
- [ ] Explicit approval to submit.

**Blocked until the above are satisfied:** `git push`, GitHub release/tag, DOI
minting, and arXiv submission (plan-2.md §27). The agent will not perform any of
these automatically.
