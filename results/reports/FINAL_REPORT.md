# Does Your Tokenizer Speak Cloud?
## Measuring domain specialization on Microsoft technical documentation

_Profile: **full**. This report is generated from committed result tables; every figure has a source CSV under `results/tables/`._

> **Scope.** This study measures **tokenization only** — token counts, compression, fragmentation, vocabulary utilization, and CPU runtime. It makes **no claim** about model output quality, accuracy, reasoning, understanding, GPU latency, or cost (plan.md §4, §26).

## 1. Research question
At a fixed tokenizer algorithm, vocabulary size, training-data size, normalization policy, and evaluation set, does training a byte-level BPE tokenizer on Azure documentation reduce tokens-per-1000-UTF-8-bytes on unseen technical documentation versus training on byte-matched general English?

## 2. Hypotheses
- **Primary:** Azure-trained tokenizer uses fewer tokens/1000 bytes on the Azure cross-service holdout than a byte-matched general-English tokenizer.
- **Secondary:** partial transfer to other Microsoft repos; larger gains on technical syntax; Mixed retains much of the gain with less general-English regression; diminishing returns with vocab size; compression ≠ runtime.

## 3. Corpus construction & leakage controls
- Byte-matched corpora (content UTF-8 bytes): `{'azure': 33554432, 'general': 33554432, 'mixed': 33554432}`; byte-match within 0.1%: **True** (spread 0 bytes).
- Azure exact dedup: 2 removed of 5340. Azure near-dup removal (threshold 0.8): 86 removed, 163 pairs found.
- General exact dedup: 134 removed of 14900; general near-dup removed: 0 (before train/eval split, so no identical WikiText content spans the split).
- Cross-corpus near-dup eval removal (eval items that near-duplicate any training doc): **9** removed.
- Azure group-aware splits: `{'azure_cross_service_holdout': 965, 'azure_same_service_holdout': 488, 'azure_train': 3799, 'n_cross_service_holdout_services': 5, 'n_leakage_groups': 20, 'n_services': 20}`. Leakage violations: **none**.
- Splits are group-aware: whole services route to the cross-service holdout; whole near-duplicate clusters stay on one side of the train/eval boundary (plan.md §11).
- Source table: `data/audit/audit_summary.json`.

## 4. Controlled tokenizer design (Track A)
Byte-level BPE (Hugging Face `tokenizers`), Unicode NFC, no lowercasing, no accent stripping, fixed byte-level pre-tokenizer + decoder, fixed special tokens, full byte-level initial alphabet, min-frequency 2. Only the training corpus changes: General / Azure / Mixed 50-50. Provenance: `artifacts/tokenizers/*.json`.

## 5. Primary compression result
Tokens per 1000 UTF-8 bytes on the **Azure cross-service holdout** (principal set; lower is better):

| Tokenizer | tokens/1000 bytes (micro) | chars/token | round-trip |
|---|---:|---:|---:|
| `azure-bytebpe-16384` | 240.18 | 4.161 | 1.000 |
| `azure-bytebpe-32768` | 232.78 | 4.294 | 1.000 |
| `azure-bytebpe-8192` | 256.21 | 3.901 | 1.000 |
| `general-bytebpe-16384` | 379.30 | 2.635 | 1.000 |
| `general-bytebpe-32768` | 360.38 | 2.773 | 1.000 |
| `general-bytebpe-8192` | 403.23 | 2.479 | 1.000 |
| `mixed-bytebpe-16384` | 249.52 | 4.005 | 1.000 |
| `mixed-bytebpe-32768` | 238.82 | 4.185 | 1.000 |
| `mixed-bytebpe-8192` | 270.92 | 3.689 | 1.000 |

Source: `results/tables/eval_aggregate.csv`, figure `results/figures/fig02_tokens_per_1k.png`.

### Effect size with paired bootstrap (95% CI)
| Comparison | reduction % | 95% CI | win rate |
|---|---:|---|---:|
| azure_vs_general:16384:azure_cross_service_holdout | 36.68 | [35.77, 37.62] | 1.000 |
| azure_vs_general:32768:azure_cross_service_holdout | 35.41 | [34.45, 36.41] | 1.000 |
| azure_vs_general:8192:azure_cross_service_holdout | 36.46 | [35.59, 37.33] | 1.000 |
| mixed_vs_general:16384:azure_cross_service_holdout | 34.21 | [33.30, 35.16] | 1.000 |
| mixed_vs_general:32768:azure_cross_service_holdout | 33.73 | [32.79, 34.73] | 1.000 |
| mixed_vs_general:8192:azure_cross_service_holdout | 32.81 | [31.95, 33.68] | 1.000 |

Paired bootstrap over documents, 10000 resamples, seed fixed. Source: `results/processed/bootstrap.json`.

## 6. Cross-repository transfer & general-English regression
Transfer to other MicrosoftDocs repos, external technical docs (Kubernetes), and the general-English regression are in `results/tables/fig_transfer_by_eval_set.csv`. In-domain gains are reported **alongside** out-of-domain regressions (plan.md §26).

## 7. Identifier fragmentation (mechanism)
Mean tokens per item on the Azure cross-service holdout (lower = less fragmented):

| Category | azure-16384 | general-16384 | mixed-16384 |
|---|---:|---:|---:|
| cli_flag | 4.56 | 8.02 | 4.86 |
| identifier_camel | 2.88 | 6.52 | 3.45 |
| identifier_snake | 4.91 | 7.39 | 5.31 |
| prose_word | 1.64 | 2.88 | 1.92 |
| resource_provider | 10.55 | 22.64 | 11.86 |
| url_path | 26.35 | 42.87 | 27.66 |

The Azure tokenizer fragments Azure-specific constructs (resource providers, CLI flags, URLs, identifiers) far less than General — the mechanism behind the compression gain. Source: `results/tables/fragmentation.csv`.

## 8. Vocabulary utilization
On the Azure cross-service holdout:

| Tokenizer | frac vocab used | unused | top-10% occurrence share |
|---|---:|---:|---:|
| `general-bytebpe-16384` | 0.485 | 8441 | 0.953 |
| `azure-bytebpe-16384` | 0.817 | 2992 | 0.844 |
| `mixed-bytebpe-16384` | 0.680 | 5238 | 0.852 |

Source: `results/tables/vocab_utilization.csv`.

## 9. Runtime (reported separately from compression)
| Tokenizer | MB/s median | MB/s p95 |
|---|---:|---:|
| `general-bytebpe-8192` | 5.13 | 5.40 |
| `general-bytebpe-16384` | 5.16 | 5.44 |
| `general-bytebpe-32768` | 5.19 | 5.48 |
| `azure-bytebpe-8192` | 5.44 | 5.71 |
| `azure-bytebpe-16384` | 5.47 | 5.77 |
| `azure-bytebpe-32768` | 5.47 | 5.76 |
| `mixed-bytebpe-8192` | 5.41 | 5.68 |
| `mixed-bytebpe-16384` | 5.45 | 5.74 |
| `mixed-bytebpe-32768` | 5.43 | 5.74 |
| `tiktoken-r50k_base` | 18.66 | 19.53 |
| `tiktoken-cl100k_base` | 19.83 | 21.31 |
| `tiktoken-o200k_base` | 11.61 | 12.10 |

Source: `results/tables/runtime_throughput.csv`. CPU tokenizer throughput only — **not** inference throughput.

## 10. Existing tokenizers (Track B — observational, not controlled)
tiktoken `r50k_base` / `cl100k_base` / `o200k_base` differ in training data, vocab size, normalization, and intended model; they are reported in a **separate** table (`results/tables/eval_aggregate.csv`, rows `tiktoken-*`) and never treated as controlled comparisons (plan.md §5).

## 11. Sources, licenses, provenance
| Repository | Commit | License | Files |
|---|---|---|---:|
| `MicrosoftDocs/azure-docs` | `80e8be2fca41` | CC-BY-4.0 | 5340 |
| `MicrosoftDocs/architecture-center` | `9bb6e65cf6b1` | CC-BY-4.0 | 220 |
| `MicrosoftDocs/azure-devops-docs` | `83e590364fe1` | CC-BY-4.0 | 220 |
| `MicrosoftDocs/sql-docs` | `b1212537b039` | CC-BY-4.0 | 220 |
| `MicrosoftDocs/fabric-docs` | `e8925d869c90` | CC-BY-4.0 | 150 |
| `MicrosoftDocs/microsoft-365-docs` | `eab9d7696cdf` | CC-BY-4.0 | 200 |
| `kubernetes/website` | `71d23f81e347` | CC-BY-4.0 | 250 |
| `Salesforce/wikitext` | `hf:main` | CC-BY-SA-3.0 | 14900 |

Full pins: `data/manifests/sources.lock.json`. License review: `licenses/`.

**Artifact distribution policy.** Per `licenses/RESTRICTIONS.md`: raw source text is never committed (git-ignored); only scripts, manifests, hashes, and aggregate results are published. The **Azure-only** tokenizer artifact is redistributable with CC-BY attribution. The **General** and **Mixed** tokenizer artifacts are trained on WikiText (CC-BY-SA, unclear redistribution) and are **LOCAL-USE-ONLY** pending legal review — their `tokenizer.json` files are git-ignored; only their provenance metadata (hashes, config, timing) is tracked. Each tokenizer's `distributable` flag is recorded in `artifacts/tokenizers/*.json`.

## 12. Limitations
- Tokenization-only; no model-quality, GPU, or cost claims.
- Corpus sizes are bounded by the local run budget; see profile above.
- Existing-tokenizer comparisons are observational.
- Context/billing figures are labelled estimates, not measured costs.

## 13. Reproduction
```bash
uv sync && bash scripts/doctor.sh
make acquire-pilot audit-pilot train-pilot evaluate-pilot analyze report verify
```
Deterministic from the global seed, pinned source commits, and content hashes.

## 14. Conclusions (limited to measured tokenization behaviour)
See §5 effect sizes. Claims are restricted to token counts on the stated corpora under the stated controls.
