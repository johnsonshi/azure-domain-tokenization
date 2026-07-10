# Repository map

Where to find things. Raw corpora and the local source clone are **git-ignored**
and never committed; only scripts, manifests, hashes, and aggregate results are
published.

```text
.
├── README.md                     # project overview + primary result + reproduction
├── LICENSE                       # MIT (original code/writing only)
├── CITATION.cff                  # citation metadata (Johnson Shi, Microsoft)
├── CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md CHANGELOG.md
├── plan.md                       # original experiment plan (frozen)
├── plan-2.md                     # publication + arXiv preparation plan
├── pyproject.toml  uv.lock       # Python 3.12 env (pinned via uv)
├── Makefile                      # stable commands (see below)
├── configs/                      # frozen experiment + source configs
│   ├── experiment.yaml           # seed, budgets, vocab sizes, bootstrap resamples
│   └── sources.yaml              # 8 sources: roles, paths, methods, eval categories
├── src/msdocs_tokenizer/         # pipeline library + `msdocs-tok` CLI
├── tests/                        # unit tests (67, `uv run pytest`)
├── scripts/                      # doctor, verify_all, verify_claims, make_figures,
│                                 #   publication_verify, overnight, resume
├── data/
│   ├── manifests/                # sources.lock.json (pinned commits), corpus manifests (TRACKED)
│   ├── audit/                    # audit_summary.json + dedup/overlap parquet (TRACKED)
│   ├── raw/ normalized/ segments/ splits/ evaluation/   # intermediate corpora (GIT-IGNORED)
│   └── .stages/                  # resumable stage markers (GIT-IGNORED)
├── external/                     # local source clone (GIT-IGNORED, ~2.2 GB)
├── artifacts/tokenizers/         # *.json provenance + distributable flag (TRACKED);
│                                 #   the tokenizer.json artifacts are NOT committed
├── results/                      # see results/README.md
│   ├── raw/                      # eval_rows.parquet (per-document rows; no text) + logs
│   ├── processed/                # eval_aggregate.csv, bootstrap.json
│   ├── tables/                   # figure source CSVs + summary tables
│   ├── figures/                  # figNN_*.png + FIGURES.md
│   └── reports/                  # FINAL_REPORT.md, VERIFICATION.md, ARTICLE_DRAFT.md
├── research/                     # frozen EXPERIMENT_SPEC, DEVIATIONS, PILOT_REVIEW (red team)
├── inventory/  licenses/         # repo discovery scores; source licenses + attribution
├── docs/                         # this documentation set
├── paper/                        # arXiv LaTeX manuscript (in preparation)
├── notebooks/                    # explanatory notebooks (not the core execution path)
└── publication/                  # claim registry, audits, reviews, publication state
    ├── claims.yaml               # 44 registered numeric claims (single source of truth)
    ├── claim_evidence.csv        # resolved values (from verify_claims.py)
    ├── audits/  reviews/         # repository/license/secret/reproducibility audits; reviews
    └── STATE.md DECISIONS.md CLAIM_LEDGER.md OPEN_ISSUES.md REVIEW_LOG.md work_queue.jsonl
```

## "Where do I find X?"

| I want… | Go to |
|---|---|
| The headline result | [`README.md`](../README.md) · [`docs/results.md`](results.md) |
| How the experiment was designed | [`docs/experiment-design.md`](experiment-design.md) |
| How to reproduce it | [`docs/reproducibility.md`](reproducibility.md) · [`docs/artifact-evaluation.md`](artifact-evaluation.md) |
| Exact procedures | [`docs/methodology.md`](methodology.md) |
| Data sources + licenses | [`docs/datasets-and-licenses.md`](datasets-and-licenses.md) · [`licenses/`](../licenses) |
| The result data + schemas | [`results/README.md`](../results/README.md) · [`results/DATA_DICTIONARY.md`](../results/DATA_DICTIONARY.md) |
| Every published number's source | [`publication/CLAIM_LEDGER.md`](../publication/CLAIM_LEDGER.md) · `make verify-claims` |
| Limitations / scope | [`docs/limitations.md`](limitations.md) |
| The paper | [`paper/`](../paper) |
| Independent review | [`research/PILOT_REVIEW.md`](../research/PILOT_REVIEW.md) · [`publication/reviews/`](../publication/reviews) |

## Make targets

`setup`, `doctor`, `test`, `verify`, `verify-claims`, `analyze`, `figures`,
`report`, `publication-verify` are safe (no retraining) and run from committed
results. `acquire-*`, `audit-*`, `train-*`, `evaluate-*` download sources and
recompute (expensive). `paper`, `paper-check`, `arxiv-package` build the
manuscript. Run `make help` for the full list.
