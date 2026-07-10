# Methodology

Enough detail to reproduce the experiment. Commands use the `uv` environment and
the `msdocs-tok` CLI / `Makefile`. Numbers are registered in
[`../publication/claims.yaml`](../publication/claims.yaml) (`make verify-claims`).

## 1. Source selection and commit pinning

Eight public sources were selected across strata (Azure anchor, Microsoft transfer
repositories, one external technical control, one general-English control) and
pinned by exact commit/revision in
[`../data/manifests/sources.lock.json`](../data/manifests/sources.lock.json). See
[datasets-and-licenses](datasets-and-licenses.md) for the per-source table.
Selection avoided stars-driven bias and enforced hard filters (public, English,
pin-able, affordable, not primarily binary/generated).

## 2. License review

Every source's license was reviewed before use
([`../licenses/SOURCE_LICENSES.csv`](../licenses/SOURCE_LICENSES.csv),
[`../licenses/ATTRIBUTION.md`](../licenses/ATTRIBUTION.md),
[`../licenses/RESTRICTIONS.md`](../licenses/RESTRICTIONS.md)). Raw corpora are not
redistributed; only scripts, manifests, hashes, and aggregate results are
published.

## 3. Acquisition

- **Azure anchor:** blobless git clone + cone sparse-checkout of 20 service
  directories.
- **Transfer + external:** deterministic GitHub-API blob download of a bounded
  number of Markdown files per repository.
- **General English:** the WikiText-103-raw parquet from the Hugging Face Hub.

Command: `make acquire-full` (writes `data/manifests/sources.lock.json`).

## 4. Cleaning and segmentation

For each document
([`../src/msdocs_tokenizer/markdown_extract.py`](../src/msdocs_tokenizer/markdown_extract.py),
[`normalize.py`](../src/msdocs_tokenizer/normalize.py)):

1. Decode UTF-8 strictly; quarantine malformed input.
2. Apply Unicode **NFC** normalization. Do **not** lowercase or strip accents;
   preserve case, punctuation, code whitespace, Unicode, emoji, versions.
3. Remove YAML front matter, HTML comments, and known docs-build directives.
4. Segment into reader-visible units and classify each into a content type
   (prose, heading, table, inline_code, code, cli, json, yaml, powershell, bicep,
   url_path, mixed) with a rule-based classifier that records its rule.

The primary training/evaluation representation is the reader-visible "semantic
full" text.

## 5. Deduplication

- **Exact:** SHA-256 over normalized text; exact duplicates removed within and
  across repositories.
- **Near-duplicate:** MinHash (character n-gram shingles) clustering; one
  representative kept per cluster. This removes Azure's auto-generated
  per-service pages that would otherwise bridge services across the split.
- The General corpus is exact-deduplicated **before** the train/eval split
  (`DEDUP_GENERAL_EXACT` = 134 removed), and any evaluation item that is a
  near-duplicate of a training document is removed (`CROSS_CORPUS_REMOVED` = 9).

## 6. Train/evaluation split (group-aware)

Whole Azure **services** are routed to the cross-service holdout; within training
services, whole near-duplicate clusters form the same-service holdout
([`splitting.py`](../src/msdocs_tokenizer/splitting.py)). No document, service, or
near-duplicate cluster straddles the train/eval boundary.

## 7. Corpus byte-matching

Documents are sampled deterministically (a pure function of the seed, source
commit, document id, and target byte budget) to exactly **33,554,432** UTF-8
bytes per corpus (`CORPUS_BYTES`; `BYTE_MATCH_OK` = true). The Mixed corpus is a
deterministic document-by-document 50/50 interleave of Azure and General.
See [`sampling.py`](../src/msdocs_tokenizer/sampling.py).

## 8. Tokenizer training

Byte-level BPE via Hugging Face `tokenizers`
([`train.py`](../src/msdocs_tokenizer/train.py)), with a fixed configuration held
identical across the controlled matrix:

- Byte-level pre-tokenizer (`add_prefix_space=false`, regex) and matching decoder.
- Full byte-level initial alphabet → complete UTF-8 coverage, no ordinary-text `[UNK]`.
- Unicode NFC; no lowercasing; no accent stripping.
- Special tokens `<|endoftext|>`, `<|pad|>` (count toward the vocabulary).
- Minimum merge frequency 2.
- **Vocabulary sizes:** 8,192 / 16,384 / 32,768 (primary slice 16K).
- **Seed:** `SEED` = 20260709.

Nine controlled tokenizers = General/Azure/Mixed × 8K/16K/32K. Provenance
(config hash, artifact hash, byte counts, merge count, versions, machine,
`distributable` flag) is written to
[`../artifacts/tokenizers/*.json`](../artifacts/tokenizers). Command: `make train-all`.

## 9. Evaluation

Each tokenizer encodes every document in each evaluation set
([`evaluate.py`](../src/msdocs_tokenizer/evaluate.py)). For every
(tokenizer, document) we record UTF-8 bytes, Unicode chars, whitespace words,
token count, exact round-trip success, and `[UNK]` count → one row in
[`../results/raw/eval_rows.parquet`](../results/raw/eval_rows.parquet)
(`COVERAGE_ROWS` = 59,160; `COVERAGE_UNK` = 0; round-trip = true).
Command: `make evaluate-all`.

### Metrics

```text
tokens_per_1000_bytes(T, D) = 1000 * total_tokens(T, D) / total_utf8_bytes(D)
relative_reduction(A vs G, D) = 100 * [tokens(G, D) - tokens(A, D)] / tokens(G, D)
```

Sign convention: **positive** relative reduction means the specialized tokenizer
uses **fewer** tokens. We report both micro (over all bytes) and macro (mean of
per-document ratios) aggregation ([`metrics.py`](../src/msdocs_tokenizer/metrics.py)).

## 10. Statistics

Paired bootstrap over documents (`BOOTSTRAP_RESAMPLES` = 10,000; documents paired
across tokenizers; 95% CI), stratified by eval set, content type, and repository,
plus a document win rate ([`stats.py`](../src/msdocs_tokenizer/stats.py)).
Command: `make analyze`.

## 11. Runtime benchmark

CPU tokenizer throughput is measured **separately** from compression: fixed thread
count, warm-up, ≥5 measured rounds, randomized tokenizer order per round,
identical documents/batches, batch sizes {1,8,32,128}, short/medium/long buckets,
serialized ([`runtime_bench.py`](../src/msdocs_tokenizer/runtime_bench.py)).
Reported as MB/s median (`RUNTIME_TRACKA_*`, `RUNTIME_TRACKB_*`). This is CPU
tokenizer throughput on a thermally variable laptop, **not** model serving.

## 12. Hardware and software

Apple M3 Pro, 12 cores, 36 GB RAM, macOS; Python 3.12 via `uv` (`tokenizers`,
`tiktoken`, `numpy`, `pandas`, pinned in [`../uv.lock`](../uv.lock)). Machine
metadata is captured in each tokenizer's provenance JSON.

## 13. Verification gate

`make verify` (`msdocs-tok verify --profile full`) re-checks byte-match, leakage
controls, round-trip/`[UNK]`, totals reconciliation, provenance completeness,
artifact-distribution policy, and source pinning — **8/8** — without retraining.
`make verify-claims` reconciles every published number against its source file.

See also: [experiment-design](experiment-design.md) · [reproducibility](reproducibility.md) ·
[results](results.md).
