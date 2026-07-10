# Does Your Tokenizer Speak Cloud?
## Measuring domain specialization on Microsoft technical documentation

_Profile: **pilot**. This report is generated from committed result tables; every figure has a source CSV under `results/tables/`._

> **Scope.** This study measures **tokenization only** — token counts, compression, fragmentation, vocabulary utilization, and CPU runtime. It makes **no claim** about model output quality, accuracy, reasoning, understanding, GPU latency, or cost (plan.md §4, §26).

## 1. Research question
At a fixed tokenizer algorithm, vocabulary size, training-data size, normalization policy, and evaluation set, does training a byte-level BPE tokenizer on Azure documentation reduce tokens-per-1000-UTF-8-bytes on unseen technical documentation versus training on byte-matched general English?

## 2. Hypotheses
- **Primary:** Azure-trained tokenizer uses fewer tokens/1000 bytes on the Azure cross-service holdout than a byte-matched general-English tokenizer.
- **Secondary:** partial transfer to other Microsoft repos; larger gains on technical syntax; Mixed retains much of the gain with less general-English regression; diminishing returns with vocab size; compression ≠ runtime.

## 3. Corpus construction & leakage controls
- Byte-matched corpora (content UTF-8 bytes): `{'azure': 33554432, 'general': 33554432, 'mixed': 33554432}`; byte-match within 0.1%: **True** (spread 0 bytes).
- Exact dedup: 2 removed of 5340. Near-dup (threshold 0.8): 0 items in 0 clusters.
- Azure group-aware splits: `{'azure_cross_service_holdout': 964, 'azure_same_service_holdout': 487, 'azure_train': 3802, 'n_cross_service_holdout_services': 5, 'n_leakage_groups': 20, 'n_services': 20}`. Leakage violations: **none**.
- Splits are group-aware: whole services route to the cross-service holdout; whole near-duplicate clusters stay on one side of the train/eval boundary (plan.md §11).
- Source table: `data/audit/audit_summary.json`.

## 4. Controlled tokenizer design (Track A)
Byte-level BPE (Hugging Face `tokenizers`), Unicode NFC, no lowercasing, no accent stripping, fixed byte-level pre-tokenizer + decoder, fixed special tokens, full byte-level initial alphabet, min-frequency 2. Only the training corpus changes: General / Azure / Mixed 50-50. Provenance: `artifacts/tokenizers/*.json`.

## 5. Primary compression result
Tokens per 1000 UTF-8 bytes on the **Azure cross-service holdout** (principal set; lower is better):

| Tokenizer | tokens/1000 bytes (micro) | chars/token | round-trip |
|---|---:|---:|---:|
| `azure-bytebpe-16384` | 240.13 | 4.162 | 1.000 |
| `general-bytebpe-16384` | 379.76 | 2.632 | 1.000 |
| `mixed-bytebpe-16384` | 250.05 | 3.997 | 1.000 |

Source: `results/tables/eval_aggregate.csv`, figure `results/figures/fig02_tokens_per_1k.png`.

### Effect size with paired bootstrap (95% CI)
| Comparison | reduction % | 95% CI | win rate |
|---|---:|---|---:|
| azure_vs_general:16384:azure_cross_service_holdout | 36.77 | [35.83, 37.74] | 1.000 |
| mixed_vs_general:16384:azure_cross_service_holdout | 34.15 | [33.21, 35.12] | 1.000 |

Paired bootstrap over documents, 10000 resamples, seed fixed. Source: `results/processed/bootstrap.json`.

## 6. Cross-repository transfer & general-English regression
Transfer to other MicrosoftDocs repos, external technical docs (Kubernetes), and the general-English regression are in `results/tables/fig_transfer_by_eval_set.csv`. In-domain gains are reported **alongside** out-of-domain regressions (plan.md §26).

## 7. Runtime (reported separately from compression)
_Runtime benchmark pending (`make benchmark-runtime`)._

## 8. Existing tokenizers (Track B — observational, not controlled)
tiktoken `r50k_base` / `cl100k_base` / `o200k_base` differ in training data, vocab size, normalization, and intended model; they are reported in a **separate** table (`results/tables/eval_aggregate.csv`, rows `tiktoken-*`) and never treated as controlled comparisons (plan.md §5).

## 9. Sources, licenses, provenance
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

## 10. Limitations
- Tokenization-only; no model-quality, GPU, or cost claims.
- Corpus sizes are bounded by the local run budget; see profile above.
- Existing-tokenizer comparisons are observational.
- Context/billing figures are labelled estimates, not measured costs.

## 11. Reproduction
```bash
uv sync && bash scripts/doctor.sh
make acquire-pilot audit-pilot train-pilot evaluate-pilot analyze report verify
```
Deterministic from the global seed, pinned source commits, and content hashes.

## 12. Conclusions (limited to measured tokenization behaviour)
See §5 effect sizes. Claims are restricted to token counts on the stated corpora under the stated controls.
