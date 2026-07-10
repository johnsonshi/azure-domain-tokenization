# Statistical Review

Independent read-only recomputation from `results/raw/eval_rows.parquet`; reference files were used only as paper-value comparators. Commands used `export PATH="$HOME/.local/bin:$PATH" TOKENIZERS_PARALLELISM=false` and `uv run python`.

| Statistic | Paper value | Recomputed value | Match |
|---|---:|---:|:---:|
| Primary General 16K micro tokens/1K bytes (Azure cross-service) | 379.30 | 379.30 | Y |
| Primary Azure 16K micro tokens/1K bytes (Azure cross-service) | 240.18 | 240.18 | Y |
| Primary relative reduction (Azure vs General 16K) | 36.68% | 36.6773% | Y |
| Independent paired bootstrap 95% CI | [35.77%, 37.62%] | [35.7679%, 37.6182%] | Y |
| Primary paired win rate | 1.000 | 1.000 (n=964) | Y |
| General-English Azure regression | -34.75% | -34.7474% | Y |
| Mixed reduction on principal holdout | +34.21% | 34.2141% | Y |
| Mixed regression on general English | -4.39% | -4.3942% | Y |
| Transfer: Same-service holdout | 35.03% | 35.0257% (n=487) | Y |
| Transfer: MS Data | 32.94% | 32.9365% (n=369) | Y |
| Transfer: MS DevOps | 31.76% | 31.7585% (n=219) | Y |
| Transfer: External technical (Kubernetes) | 31.18% | 31.1772% (n=237) | Y |
| Transfer: MS Architecture | 26.03% | 26.0294% (n=220) | Y |
| Transfer: MS Broad Enterprise | 25.89% | 25.8855% (n=200) | Y |
| Vocabulary size 8K reduction | 36.46% | 36.4598% (G=403.23, A=256.21) | Y |
| Vocabulary size 16K reduction | 36.68% | 36.6773% (G=379.30, A=240.18) | Y |
| Vocabulary size 32K reduction | 35.41% | 35.4077% (G=360.38, A=232.78) | Y |
| Content type: prose | 36.75% (n=900) | 36.7478% (n=900) | Y |
| Content type: heading | 37.49% | 37.4946% (n=44) | Y |
| Content type: table | 44.30% | 44.2980% (n=6) | Y |
| Content type: inline_code | 33.28% | 33.2837% (n=14) | Y |
| Raw eval row count | 59,160 | 59,160 | Y |
| Round-trip rate on utf8_bytes>0 rows | 100% | 100.00% (59,160/59,160, all_ok=True) | Y |
| Total UNK count | 0 | 0 | Y |
| Runtime Track A median MB/s range | 5.1–5.5 | 5.130–5.470 | Y |
| Runtime Track B median MB/s range | 11.6–19.8 | 11.608–19.834 | Y |
| Micro vs macro terminology | Micro primary; macro per-doc exists | Confirmed in results/README.md lines 52-58; eval_aggregate has tokens_per_1000_utf8_bytes_macro | Y |
| Excluded cross-corpus near-duplicates | 9 removed; excluded from final results | Counts confirmed; Azure removed IDs absent; final eval_rows uses post-removal eval_docs | Y |

## Independent bootstrap

I reimplemented the paired document bootstrap without calling `src/msdocs_tokenizer/stats.py`: merge the 964 document IDs in raw-row order, resample the same document indices for both tokenizers 10,000 times with `numpy.random.default_rng(20260709)`, and compute `100 * (sum(G) - sum(A)) / sum(G)` on each resample.

Result: point estimate 36.677282%, 95% CI [35.767853%, 37.618229%], win rate 1.000000, tie rate 0.000000, loss rate 0.000000. This matches `results/processed/bootstrap.json` primary CI [35.767853%, 37.618229%].

## Notes

- Sign convention confirmed: positive relative reduction means the specialized tokenizer uses fewer tokens; negative values are regressions. Thus Azure on general English is a -34.75% regression, while Azure on Azure holdout is a +36.68% reduction.
- Pairing confirmed: the bootstrap resamples document IDs, not tokenizer rows independently, and applies the same sampled IDs to General and Azure token counts.
- Micro is the primary corpus endpoint (`1000 * Σtokens / Σbytes`); per-document macro also exists in `eval_aggregate.csv`.
- Near-duplicate exclusion: audit_summary records 9 cross-corpus near-duplicate eval removals ({'azure_cross_service_holdout': 1, 'azure_same_service_holdout': 1, 'general_english': 6, 'ms_data': 1}). eval_rows has final eval-set document counts {'azure_cross_service_holdout': 964, 'azure_same_service_holdout': 487, 'external_technical': 237, 'general_english': 2204, 'ms_architecture': 220, 'ms_broad_enterprise': 200, 'ms_data': 369, 'ms_devops': 219, 'synthetic': 30}. For Azure split files, the one removed cross-service id and one removed same-service id are absent from eval_rows: cross=['sha256:b62635ce04f7623856095f9b5bd0b9b7caaae4a2ee394e8073acf632928fafae'], same=['sha256:bc511f5c016e74cb15b367840bcc59dfc13b191b440f1a794c98dcdc05d2d33c']. The audit artifact records counts rather than all nine removed IDs, so the non-Azure six general-English and one ms_data IDs could not be ID-checked directly from audit_summary.
- No discrepancy exceeded the requested ~0.05 percentage-point tolerance.

STATISTICAL REVIEW: PASS
