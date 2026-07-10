# Frozen experimental specification

Status: **pre-registered / frozen before inspecting full results**  
Frozen by role: `methodologist`  
Date: 2026-07-10  
Scope: CPU-only tokenization-efficiency study. This specification governs confirmatory claims for Track A. Any post-freeze change must be appended to `research/DEVIATIONS.md`.

## 1. Claim boundary

This study measures tokenization only. Allowed interpretations are of the form: **"tokenizer X uses fewer tokens on corpus Y"**. The study must not claim better understanding, reasoning, model quality, production drop-in replaceability, GPU latency reduction, or measured cost savings. Context-window and billing calculations are estimates and must be labeled as estimates. In-domain gains must be reported with out-of-domain regressions. Track B existing-tokenizer results are observational only and must not be mixed with Track A controlled comparisons.

## 2. Primary confirmatory hypothesis

At a fixed byte-level BPE algorithm, pre-tokenizer, decoder, Unicode normalization, special-token set, requested vocabulary size, training-byte budget, sampling process, and evaluation document set, an Azure-documentation-trained tokenizer will produce fewer tokens per 1,000 UTF-8 bytes on the Azure cross-service holdout than an otherwise identical byte-matched general-English tokenizer.

Operational comparison: `azure-bytebpe-{vocab}` versus `general-bytebpe-{vocab}` on `azure_cross_service_holdout`, with the principal vocabulary size being 16,384 for the pilot and all three required vocabulary sizes for the full run.

Expected direction: Azure-trained < General-trained tokens per 1,000 UTF-8 bytes, equivalently positive `relative_token_reduction_pct`.

Falsification / null for the primary hypothesis: the Azure-trained tokenizer does not reduce token count on the principal Azure cross-service holdout at fixed vocabulary, i.e. the point estimate of `relative_token_reduction_pct` is <= 0 or the 95% paired-bootstrap confidence interval is compatible with no positive reduction. Inconclusive and negative findings must be reported.

## 3. Endpoints and formulas

Implementations referenced here are in `src/msdocs_tokenizer/metrics.py` and aggregation in `src/msdocs_tokenizer/evaluate.py`.

### 3.1 Primary endpoint

For tokenizer `T` and evaluation corpus `D`:

```text
tokens_per_1000_utf8_bytes(T, D)
  = 1000 * total_tokens(T, D) / total_utf8_bytes(D)
```

Code reference: `metrics.tokens_per_1000_utf8_bytes(total_tokens, total_utf8_bytes)`.

Report both:

- **Micro**: `1000 * sum(document token_count) / sum(document utf8_bytes)` over all non-empty evaluated bytes. Code reference: `evaluate.aggregate(...)["tokens_per_1000_utf8_bytes_micro"]`.
- **Macro**: mean of per-document ratios `1000 * token_count_i / utf8_bytes_i`, excluding zero-byte denominators. Code reference: `evaluate.aggregate(...)["tokens_per_1000_utf8_bytes_macro"]` using `metrics.macro_mean`.

Lower is better. Micro is the primary corpus-level endpoint; macro is a required companion endpoint to expose document weighting effects.

### 3.2 Primary effect size

```text
relative_token_reduction(A versus G, D)
  = 100 * (tokens(G, D) - tokens(A, D)) / tokens(G, D)
```

where `A` is the Azure-trained tokenizer and `G` is the matched general-English tokenizer at the same requested vocabulary size. Code reference: `metrics.relative_token_reduction(tokens_general, tokens_specialized)` and `evaluate.paired_reduction_table(...)`.

Positive values mean the Azure-trained tokenizer uses fewer tokens. The confirmatory effect size is computed from micro token ratios on `azure_cross_service_holdout`; paired-bootstrap intervals use paired per-document token counts as implemented in `stats.paired_bootstrap_relative_reduction`.

## 4. Required tokenizer matrix

Track A controlled matrix:

| Training corpus | 8,192 | 16,384 | 32,768 |
|---|---:|---:|---:|
| General English | required | required | required |
| Azure docs | required | required | required |
| Mixed 50/50 Azure + General | required | required | required |

Total required controlled tokenizers: 9.

Pilot matrix: the three 16,384-token tokenizers first: `general-bytebpe-16384`, `azure-bytebpe-16384`, and `mixed-bytebpe-16384`. The pilot must validate round-trip, schema, leakage audits, and metric implementation before the full 8K/16K/32K matrix.

Special tokens count toward the requested vocabulary size, matching `train.tokenizer_config_dict(...)["special_tokens_count_in_vocab"] = True`.

## 5. Evaluation sets

Evaluation manifests are frozen before full-result inspection. The principal set is **`azure_cross_service_holdout`**.

The nine required evaluation categories from `plan.md` §14 are operationalized as follows:

| # | Required category | Operational eval-set name(s) in code/config | Confirmatory status |
|---:|---|---|---|
| 1 | Azure same-service holdout | `azure_same_service_holdout` | Secondary confirmatory |
| 2 | Azure cross-service holdout | `azure_cross_service_holdout` | **Principal confirmatory** |
| 3 | Microsoft architecture documentation | `transfer:MicrosoftDocs/architecture-center` | Secondary / transfer |
| 4 | Microsoft DevOps or automation documentation | `transfer:MicrosoftDocs/azure-devops-docs`; `transfer:MicrosoftDocs/PowerShell-Docs` | Secondary / transfer |
| 5 | Microsoft data documentation | `transfer:MicrosoftDocs/sql-docs` | Secondary / transfer |
| 6 | Broad Microsoft enterprise/developer documentation | covered by the union of transfer MicrosoftDocs repositories in this run | Exploratory unless separately pre-labeled |
| 7 | External technical documentation | `external_technical` from `kubernetes/website` | Secondary / transfer |
| 8 | General English | `general_english` from held-out `Salesforce/wikitext` / `wikitext-103-raw` | Required regression measurement |
| 9 | Synthetic edge cases | `synthetic` | Diagnostic only, never primary evidence |

If the code emits one `transfer:{repo}` eval set per repository, those repo-level sets must be mapped back to the required categories above in reports.

## 6. Controlled and manipulated variables

### 6.1 Controlled variables for Track A

The following must remain identical across General, Azure, and Mixed tokenizers within a requested vocabulary size:

- Algorithm: Hugging Face `tokenizers` byte-level BPE.
- Pre-tokenizer: `ByteLevel(add_prefix_space=False, use_regex=True)`.
- Decoder: `ByteLevel`.
- Unicode normalization: NFC.
- Case/accent policy: no lowercasing and no accent stripping.
- Special tokens: exactly `("<|endoftext|>", "<|pad|>")`.
- Requested vocabulary size and special-token accounting.
- Minimum frequency: 2.
- Full byte-level initial alphabet.
- Training bytes: byte-matched by cleaned UTF-8 bytes within 0.1% (`config.BYTE_MATCH_TOLERANCE = 0.001`).
- Sampling: deterministic from configured seed and document identity.
- Evaluation documents: identical documents paired across tokenizers.
- CPU-only environment and package versions recorded in tokenizer provenance.

The NFC/no-lowercase choice is defensible because Microsoft technical documentation contains case-sensitive identifiers, CLI flags, resource-provider names, paths, code, product names, and Unicode text. NFC removes canonically equivalent representation noise without erasing case, accents, punctuation, code whitespace, emoji, versions, or placeholders.

### 6.2 Single manipulated variable

The single manipulated variable in Track A is **training corpus**:

1. `general`: general English, implemented as Wikipedia-derived `Salesforce/wikitext` / `wikitext-103-raw`.
2. `azure`: semantic-full text from Azure documentation training split.
3. `mixed`: 50% Azure bytes and 50% general-English bytes.

The general-English choice is defensible because `wikitext-103-raw` is a standard, versioned, Wikipedia-derived English corpus, not primarily source code or technical documentation, and it provides enough volume for byte-matched CPU-local tokenizer training. Because it is Wikipedia-derived, reports must describe it as an estimate of general-English regression, not as all out-of-domain English.

## 7. Leakage controls

Required leakage controls:

- Decode raw inputs as UTF-8; malformed inputs are counted/quarantined, not silently repaired.
- Normalize with NFC before hashing and tokenization.
- Remove exact duplicate normalized semantic-full documents by SHA-256. Code reference: `dedup.exact_hash` / `corpus.exact_dedup`.
- Detect near duplicates using MinHash + LSH over character 5-gram shingles, 128 permutations, with threshold `0.8` from `configs/experiment.yaml`. Code reference: `dedup.find_near_duplicates` and `corpus.near_dedup_clusters`.
- Use group-aware Azure splitting by top-level service plus near-duplicate cluster. No service may span Azure train and Azure cross-service holdout; no near-duplicate cluster may span Azure train and any Azure holdout. Code reference: `splitting.assign_azure_splits` and `splitting.verify_no_cross_split_leakage`.
- Ensure no exact SHA-256 Azure train/eval duplicate remains. Code reference: `pipeline._assert_no_train_eval_leak`.
- Keep general-English train and eval disjoint by deterministic document hash split (`general_english_eval = 0.15` in config; `pipeline._hash_split`).
- Freeze evaluation documents before full-result inspection.

Required audit artifacts include exact duplicate, near-duplicate, cross-overlap, split, and audit-summary outputs. If an implemented audit covers only a subset, the missing coverage must be listed as a code/methodology gap before publication.

## 8. Exclusion and blocking rules

Exclude from training/evaluation:

- Empty or whitespace-only documents after normalization/extraction.
- Malformed UTF-8 or documents containing invalid surrogate content; these are counted/quarantined.
- Generated/navigation/front-matter boilerplate according to the cleaning implementation.
- Exact duplicates after normalized semantic-full SHA-256 hashing.
- Evaluation items with near-duplicate overlap with training beyond the declared threshold.
- Documents whose license status prevents local use in this study.

Publication blockers:

- Any unexplained encode/decode round-trip failure on non-empty evaluation text.
- Any unexplained nonzero `[UNK]` count for the controlled byte-level BPE tokenizers.
- Any detected train/eval leakage affecting the principal comparison.
- Training-corpus byte mismatch above 0.1% for a controlled comparison.
- Missing evaluation manifest or provenance needed to regenerate the primary endpoint.

The current evaluation code blocks non-empty round-trip or UNK failures in `pipeline.run_evaluate`.

## 9. Statistical method

Token counts are deterministic; uncertainty is over sampled documents.

Confirmatory intervals use paired bootstrap over documents:

- Resampling unit: document, not line or segment.
- Pairing: the same document index is resampled across tokenizers.
- Final resamples: 10,000 (`configs/experiment.yaml: bootstrap_resamples`).
- Interval: percentile 95% CI.
- Statistic: relative token reduction percentage, `100 * (sum(G) - sum(A)) / sum(G)` on each resample.
- Required stratification/reporting: repository and content type; keep segments from the same document grouped.
- Report mean and median paired token-count difference plus win/tie/loss rates.

Code references: `stats.paired_bootstrap_relative_reduction` and `stats.stratified_bootstrap`.

Multiplicity: the primary Azure-vs-General comparison on `azure_cross_service_holdout` is the only principal confirmatory test. Same-service holdout, transfer sets, general-English regression, Mixed-vs-General, Azure-vs-Mixed, content-type effects, repository effects, length deciles, synthetic cases, vocabulary curves, and Track B comparisons must be labeled secondary or exploratory unless a later frozen amendment defines a correction procedure. If making multiple confirmatory claims, apply and disclose a multiple-comparison correction.

## 10. Hypotheses, expected directions, and falsification criteria

| ID | Hypothesis | Expected direction | Falsifies / null-compatible result |
|---|---|---|---|
| H1 primary | Azure-trained uses fewer tokens than byte-matched General on Azure cross-service holdout at fixed vocab. | `relative_token_reduction_pct(Azure vs General) > 0`; lower Azure tokens/1K bytes. | Point estimate <= 0, or 95% CI compatible with no positive reduction. |
| H2 transfer | Azure-trained retains part of its compression advantage on other Microsoft technical-doc repositories. | Positive Azure-vs-General reduction on most transfer MicrosoftDocs sets. | Most transfer sets show <= 0 reduction or large regressions. |
| H3 technical syntax | Azure advantage is larger for commands, identifiers, resource-provider names, API paths, config, YAML, JSON, Bicep, PowerShell, and inline code than for prose. | Technical content types have larger positive reduction than prose content types. | Technical content types do not exceed prose or show regressions. |
| H4 Mixed trade-off | Mixed retains much of Azure's in-domain gain while reducing general-English regression. | Mixed-vs-General positive on Azure holdout; Mixed has smaller general-English penalty than Azure. | Mixed loses most Azure gain or does not reduce general-English regression. |
| H5 vocab scaling | 8K -> 16K -> 32K improves compression with diminishing marginal gains. | tokens/1K bytes decreases as vocab increases; 16K->32K gain smaller than 8K->16K. | No monotonic improvement or no diminishing pattern. |
| H6 runtime | Specialized tokenization may reduce token count without improving CPU encode latency. | Compression and runtime may diverge; report separately. | Any claim that token reduction alone proves CPU or inference speedup is invalid. |
| H7 popularity | Repository popularity does not reliably predict transfer. | Transfer aligns better with content composition/domain similarity than stars. | Popularity alone explains transfer as well as or better than content factors. |
| H8 general-English regression | In-domain gains may come with out-of-domain regression. | Azure may use more tokens on `general_english`; report with gains. | No regression is possible to report as a finding, but hiding a regression violates the spec. |

## 11. Stopping rules and minimum viable study

### 11.1 Full target

Complete the nine-tokenizer matrix, all required evaluation categories, compression/fragmentation/runtime/statistical analyses, source tables, and final report if budget permits.

### 11.2 Minimum viable study

If constrained, the minimum viable study is:

- 32 MiB each of Azure, General, and Mixed training corpora.
- Three matched 16K byte-level BPE tokenizers.
- Azure cross-service holdout.
- Two other MicrosoftDocs repositories.
- One external technical corpus.
- One general-English evaluation set.
- Compression metrics.
- Prose versus syntax fragmentation.
- Round-trip tests.
- Paired bootstrap.
- Final report.

Never remove leakage controls, general-English regression measurement, Azure cross-service holdout, license review, round-trip validation, or raw results.

### 11.3 Scope-removal order

Remove optional scope in this order:

1. 64K vocabulary.
2. Optional algorithms.
3. Optional mix ratios.
4. Runtime batch expansion.
5. 8K vocabulary.
6. Extra evaluation repositories.
7. 32K vocabulary only if necessary.

Stop starting new work when required gates pass, fewer than 45 minutes remain, free disk drops below 15%, three tasks share the same external blocker, or optional expansion threatens report completion. Use remaining time for verification and reporting.

## 12. Implementation-alignment notes to verify before publication

This specification intentionally freezes the intended method. Current code mostly matches the controlled tokenizer, endpoint, and bootstrap formulas, but the following must be verified or fixed before final confirmatory publication:

- `pipeline.run_analyze` currently bootstraps the principal comparison and content-type strata, but does not yet implement combined repository + content-type stratified reporting for all required comparisons.
- Content-type stratified bootstrap in the pipeline uses `min(n_resamples, 5000)`, while the final pre-registered method requires 10,000 final resamples for confirmatory intervals.
- `stats.stratified_bootstrap` runs separate within-stratum intervals; it does not implement a weighted stratified bootstrap estimator over repository + content-type strata.
- Evaluation sets are emitted as dynamic `transfer:{repo}` names and must be mapped to the nine required categories in reporting.
- Cross-repository near-duplicate overlap and general-English exact-dedup coverage should be audited explicitly if not already emitted by downstream artifacts.
