# Pilot red-team review

Role: `red_team_reviewer` publication gate. Scope: pilot Track A 16,384-vocab CPU-only tokenizer-efficiency study. I treated automated verification as untrusted and regenerated the main ratios from `results/raw/eval_rows.parquet`.

## Checklist

| # | Item | Verdict | Evidence checked |
|---:|---|---|---|
| 1 | Did evaluation text leak into training? | **FAIL** | Principal Azure split is clean: `data/audit/audit_summary.json` has `leakage_violations=[]`; `data/audit/near_duplicates.parquet` has 161 Azure near-dup pairs, and 0 pairs with both docs kept across splits; `data/audit/exact_duplicates.parquet` has 0 Azure train/eval exact crossings. However, reconstructing `src/msdocs_tokenizer/pipeline.py` `_hash_split` found **36 `general_english` eval docs with exact canonical text hashes in general training** (median 3,424.5 bytes; max 69,116 bytes). Removing those 36 barely changes the reported regression (`-34.83%` -> `-34.82%`), but this is still train/eval content leakage. |
| 2 | Are near-duplicates shared across repositories? | **CONCERN** | `data/audit/cross_repo_overlap.parquet` reports `n_repos=0` for exact cross-repo overlap, but `src/msdocs_tokenizer/pipeline.py` lines 367-370 write near-duplicate pairs only within the Azure anchor. `research/EXPERIMENT_SPEC.md` lines 232-237 explicitly note cross-repository near-duplicate coverage as a gap. |
| 3 | Are corpora matched by cleaned bytes? | **PASS** | `data/audit/audit_summary.json`: `byte_match_ok=true`, `byte_match_spread=0`, and `corpora_content_bytes` all exactly `33,554,432`. `data/manifests/{azure,general,mixed}.corpus.json` also record `content_utf8_bytes=33,554,432`. |
| 4 | Are vocabulary sizes actually equal? | **PASS** | `artifacts/tokenizers/{general,azure,mixed}-bytebpe-16384.json`: each has `vocab_size_requested=16384`, `vocab_size_actual=16384`, `merge_count=16126`, `special_tokens_count_in_vocab=true`. |
| 5 | Is normalization identical? | **PASS** | `data/audit/audit_summary.json` normalization counts show `changed_by_nfc=0`, `malformed=0` for all corpora; tokenizer JSONs have identical ByteLevel pre-tokenizer/decoder and no tokenizer-embedded normalizer. Input normalization is shared through `src/msdocs_tokenizer/corpus.py` lines 59-64. |
| 6 | Did Markdown cleaning favor one corpus? | **CONCERN** | A single extractor is used (`src/msdocs_tokenizer/markdown_extract.py` lines 124-245), but no per-corpus cleaning-removal table is emitted. Because Azure/transfer docs are Markdown and WikiText is not, publishable claims need a cleaning-bias summary. |
| 7 | Is the result driven by front matter or repeated punctuation? | **PASS** | Principal holdout by content type remains strongly positive: `results/processed/bootstrap.json` `by_content_type.prose` point estimate `36.84%`, CI `[35.93,37.78]`; headings `37.51%`; tables `44.44%`. |
| 8 | Is it driven only by code fences? | **PASS** | Principal Azure holdout has 900 prose docs and prose-only reduction is `36.84%`; inline-code stratum is only 14 docs and not sufficient to explain the aggregate. |
| 9 | Does the gain remain on cross-service Azure? | **PASS** | `data/splits/azure_splits.parquet`: cross-service holdout is exactly 5 whole services (`data-factory`, `event-hubs`, `expressroute`, `frontdoor`, `virtual-network`) and 964 docs. `results/processed/bootstrap.json`: azure-vs-general point `36.768%`, CI `[35.827,37.742]`, win rate `1.0`. |
| 10 | Does it transfer beyond MicrosoftDocs? | **PASS** | `results/tables/reduction_azure_vs_general_16384.csv`: `external_technical` (Kubernetes) reduction `31.036%`, n=237 in `results/processed/eval_aggregate.csv`. |
| 11 | What is the general-English penalty? | **PASS** | `results/tables/reduction_azure_vs_general_16384.csv`: `general_english=-34.833%`; `results/processed/bootstrap.json`: CI `[-35.188,-34.482]`. Excluding the 36 exact leaked eval docs gives `-34.815%`, so the penalty is not materially changed by that leak. |
| 12 | Are production baselines being compared unfairly? | **PASS** | `research/EXPERIMENT_SPEC.md` lines 8-10 require Track B to stay observational; `results/reports/FINAL_REPORT.md` lines 50-51 labels tiktoken as separate/observational. |
| 13 | Are timing results contaminated by thermal drift or concurrency? | **CONCERN** | `results/tables/runtime_throughput.csv` exists, but `results/reports/FINAL_REPORT.md` lines 47-48 says runtime is pending, and `results/raw/runtime_observations.json` has no thermal/concurrency metadata. Runtime should not be used as evidence yet. |
| 14 | Are intervals paired by document? | **PASS** | `src/msdocs_tokenizer/stats.py` lines 32-62 resample the same document indices for both tokenizers. `src/msdocs_tokenizer/pipeline.py` lines 555-559 merges paired counts by `document_id`; primary pair coverage regenerated as 964 paired docs, 0 unpaired. |
| 15 | Can every number be regenerated from raw tables? | **PASS** | From `results/raw/eval_rows.parquet`: General primary micro `1000*3,948,834/10,398,369=379.755`; Azure micro `1000*2,496,925/10,398,369=240.127`; reduction `36.768%`. Spot doc `sha256:264ce8...` has 794 bytes, 272 general tokens, 178 Azure tokens. |
| 16 | Are licenses and attribution satisfied? | **PASS** | `licenses/SOURCE_LICENSES.csv`, `licenses/ATTRIBUTION.md`, and `licenses/RESTRICTIONS.md` exist. `data/manifests/sources.lock.json` records 7 CC-BY-4.0 sources and WikiText CC-BY-SA-3.0. See item 24 for artifact distribution limits. |
| 17 | Are any model-quality claims unsupported? | **PASS** | `research/EXPERIMENT_SPEC.md` lines 8-10 and `results/reports/FINAL_REPORT.md` lines 6, 67-71 limit claims to tokenization and label context/billing as estimates. I found no model quality, reasoning, or measured cost claim in `FINAL_REPORT.md`. |
| 18 | Did stars dominate source selection? | **PASS** | `research/EXPERIMENT_SPEC.md` lines 71-89 predefine evaluation categories; `data/manifests/sources.lock.json` source notes show role/category and deterministic selection, not GitHub-star filtering. |
| 19 | Is the corpus large enough for the vocabulary? | **PASS** | Each Track A tokenizer trained on 32 MiB (`33,554,432` bytes) and achieved actual vocab `16,384`; no underfilled 16K vocab. |
| 20 | How many vocabulary entries are unused? | **PASS** | Computed on frozen eval docs: general used 16,057/16,384 (327 unused, 2.00%); Azure used 15,694/16,384 (690 unused, 4.21%); mixed used 16,057/16,384 (327 unused, 2.00%). |
| 21 | Does Mixed provide nearly the same gain with less regression? | **PASS** | `results/tables/reduction_mixed_vs_general_16384.csv`: mixed primary `34.155%` vs Azure `36.768%`; mixed general-English regression `-4.423%` vs Azure `-34.833%`. |
| 22 | Does the conclusion survive removing code/config? | **PASS** | Principal prose-only stratum: `results/processed/bootstrap.json` `by_content_type.prose` point `36.843%`, CI `[35.930,37.784]`, n=900. |
| 23 | Does it survive removing document-length extremes? | **PASS** | Recomputed primary after removing bottom/top byte deciles: n=770, reduction `35.497%` (still large and positive). |
| 24 | May tokenizer artifacts be distributed? | **FAIL** | `licenses/RESTRICTIONS.md` lines 19-35: Azure-only tokenizer artifacts are GO with attribution, but WikiText-only and mixed-with-WikiText tokenizers are **VETO / LOCAL-USE-ONLY** pending legal review. `git status` shows `artifacts/tokenizers/general-bytebpe-16384.json` and `mixed-bytebpe-16384.json` staged/added. |
| 25 | Is raw licensed text accidentally committed? | **PASS** | `git ls-files data results artifacts research` shows manifests, aggregate results, tokenizer provenance, and figures, but not `data/raw/*.parquet`, `data/evaluation/eval_docs.parquet`, `data/splits/*.corpus.txt`, or audit parquet. `licenses/RESTRICTIONS.md` lines 5-18 correctly forbids raw text commits. |

## Blockers before expanding to the full matrix

1. **Fix general-English content leakage.** The current document-id hash split is disjoint, but exact duplicate WikiText content appears on both sides: 36 general-English eval docs have canonical text hashes in general training. Deduplicate or group by exact semantic hash before the train/eval split, then regenerate pilot metrics.
2. **Add/complete cross-repository near-duplicate leakage audit.** Current `near_duplicates.parquet` covers Azure anchor near-dups only; exact cross-repo overlap is zero, but near-dup train/eval overlap across Azure/general/transfer/external is not audited.
3. **Resolve artifact distribution policy before publishing or staging full-matrix artifacts.** General and mixed tokenizers are WikiText-derived and currently local-use-only per `licenses/RESTRICTIONS.md`; do not publish them without legal clearance or a replacement distributable general corpus.

## Non-blocking recommendations

- Fix `results/reports/FINAL_REPORT.md`: it says near-dup removal was “0 items in 0 clusters,” but `data/audit/audit_summary.json` says 161 pairs and 85 removed.
- Reconcile runtime reporting: either remove runtime tables from pilot claims or add serialized/no-concurrency/thermal metadata and update `FINAL_REPORT.md` so it no longer says runtime is pending.
- Emit source tables for cleaning-removal counts, vocabulary utilization, and length-decile sensitivity so these checks do not depend on ad hoc reviewer scripts.
- Extend bootstrap stratification beyond the principal repository if transfer claims will be emphasized.

**PILOT VERDICT: NO-GO** — the primary Azure cross-service result is strong and regenerable, but unresolved general-English exact train/eval leakage plus missing cross-repository near-duplicate audit and non-distributable WikiText-derived artifacts must be fixed before expanding the full matrix.

## Re-review (blocker resolution) — 2026-07-10

I independently re-ran the requested checks with `uv run python` against the current working tree.

1. **General-English train/eval exact leakage: RESOLVED.** Rebuilt WikiText processing from `data/raw/wikitext-103.raw.parquet` with `process_documents`, applied `corpus.exact_dedup`, then reran `pipeline._hash_split` with seed `20260709` and `eval_frac=0.15`. The rebuild produced 14,900 processed docs, 14,766 after exact dedup, 12,556 train docs, and 2,210 pre-filter general eval docs. Shared canonical-text hashes between rebuilt general train and rebuilt general eval: **0**. Shared canonical-text hashes between rebuilt general train and the frozen `data/evaluation/eval_docs.parquet` `general_english` rows: **0 of 2,204**. `data/audit/audit_summary.json` records `exact_dedup_general.removed_exact=134` (>0). The code path in `src/msdocs_tokenizer/pipeline.py` exact-dedups `general_all` before `_hash_split` and calls `_assert_no_content_leak(general_train, _general_eval, "general")`.

2. **Cross-repository near-duplicate eval audit: RESOLVED.** `data/audit/audit_summary.json` records `cross_corpus_near_dup_eval.removed_near_train=9` with per-set breakdown `azure_cross_service_holdout=1`, `azure_same_service_holdout=1`, `general_english=6`, `ms_data=1`. Code inspection of `src/msdocs_tokenizer/dedup.py::flag_eval_near_train` confirms it builds one `MinHashLSH` from the full supplied training pool and queries each eval item, flagging eval IDs with any training hit. Code inspection of `pipeline.py` confirms that training pool is `azure_train + general_train` and is passed into `_build_eval_docs` before frozen eval parquet emission. A toy identical-train/eval probe flagged only the identical eval document, supporting the LSH wiring.

3. **WikiText-derived artifact distribution policy: NOT-RESOLVED.** The strongest distribution-risk pieces are fixed: `git ls-files artifacts/ | grep 'tokenizer\.json'` returns no tracked `tokenizer.json` files; `results/reports/FINAL_REPORT.md` §11 documents Azure-only redistributability and General/Mixed LOCAL-USE-ONLY; tracked 8K/16K/32K provenance JSONs have Azure `distributable=true` and General/Mixed `distributable=false`. However, `git ls-files artifacts/` still tracks `artifacts/tokenizers/{azure,general,mixed}-bytebpe-2048.json`, and all three 2048 provenance JSONs lack both `distributable` and `distribution_note`. Because the claimed fix says each `artifacts/tokenizers/*.json` provenance has a `distributable` field and General/Mixed are explicitly LOCAL-USE-ONLY, this artifact-publication blocker is not fully resolved.

Additional re-checks:

- Primary result is unchanged in substance and regenerable from `results/raw/eval_rows.parquet`: for `azure_cross_service_holdout` at vocab 16,384, General has 3,946,661 tokens over 10,405,241 bytes (`379.295` tokens/1K bytes), Azure has 2,499,133 tokens over the same bytes (`240.180` tokens/1K bytes), giving a micro reduction of **36.677%**.
- `results/reports/FINAL_REPORT.md` no longer contains `0 near-dup items` and no longer says runtime is `pending` / `runtime is pending`; the remaining word `pending` is in the legal-review policy, not runtime reporting.

Remaining concern: tracked stale/secondary provenance artifacts are part of the publishable artifact surface. Either regenerate or remove the 2048 provenance JSONs so every tracked tokenizer provenance file carries the explicit distribution decision.

**PILOT VERDICT (re-review): NO-GO**

---

## Orchestrator resolution note (2026-07-10, after re-review)

Blocker 3 (flagged NOT-RESOLVED in the re-review) was caused by **stale 2048-vocab
provenance JSONs left over from a no-network smoke test**, which predated the
`distributable` field. Resolution:

- Removed all `artifacts/tokenizers/*-bytebpe-2048*` smoke leftovers (not part of the study).
- Confirmed all nine real provenance JSONs (8K/16K/32K × General/Azure/Mixed) carry
  `distributable` (Azure=true, General/Mixed=false) and a `distribution_note`.
- Added an automated gate `artifact_distribution_marked` to `msdocs-tok verify`
  (every provenance marks distributability AND no `tokenizer.json` is git-tracked).
- `git ls-files artifacts/` now shows only provenance `*.json`; no `tokenizer.json`.

`msdocs-tok verify --profile full` = **8/8 PASS**. All three blockers are resolved;
the primary result (36.68% on the Azure cross-service holdout) is unchanged.
