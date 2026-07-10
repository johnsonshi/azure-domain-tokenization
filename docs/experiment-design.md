# Experiment design

This study is a **controlled case study** of how the *training corpus* changes
byte-level BPE tokenizer **compression** on unseen technical documentation. It
measures tokenization only (see [limitations](limitations.md)). Every number
here is registered in [`../publication/claims.yaml`](../publication/claims.yaml)
and re-checked by `make verify-claims`; claim IDs are given in parentheses.

## Research question

At a fixed tokenizer algorithm, vocabulary size, training-data size, normalization
policy, and evaluation set, does training a byte-level BPE tokenizer on Azure
documentation reduce the number of tokens required to encode *unseen* technical
documentation, compared with training on byte-matched general English?

## Hypotheses

Frozen before the full results were inspected (see
[`../research/EXPERIMENT_SPEC.md`](../research/EXPERIMENT_SPEC.md)).

- **Primary (H1).** An Azure-trained byte-level BPE tokenizer produces fewer
  tokens per 1,000 UTF-8 bytes on the Azure cross-service holdout than a
  byte-matched General-English tokenizer at the same vocabulary size.
- **Secondary.** (H2) partial transfer to other Microsoft and external technical
  documentation; (H3) a 50/50 Mixed tokenizer retains most of the in-domain gain
  with a smaller general-English regression; (H4) the effect is stable across
  8K/16K/32K vocabularies; (H5) the gain persists on prose, not only code/markup;
  (H6) compression and CPU tokenizer throughput are distinct dimensions.
- **Null (H0).** After controlling for vocabulary size, implementation, training
  bytes, normalization, sampling, and leakage, the Azure- and General-trained
  tokenizers have no meaningful difference in token count on held-out
  documentation (point estimate ≤ 0 or CI compatible with no positive reduction).

## Variables

- **Independent variable (manipulated):** the training corpus — General, Azure,
  or Mixed (50/50).
- **Controlled variables (held identical):** byte-level BPE implementation,
  pre-tokenizer, decoder, Unicode NFC normalization, special-token set, requested
  vocabulary size, training-byte budget (33,554,432 bytes each, `CORPUS_BYTES`),
  deterministic sampling, and the evaluation document sets.
- **Dependent variables:** tokens per 1,000 UTF-8 bytes (primary), relative token
  reduction, characters/bytes per token, tokens per whitespace word, identifier
  fragmentation, vocabulary utilization, round-trip / `[UNK]` rate, and CPU
  throughput.

## Training-corpus construction

Three byte-matched corpora of **32 MiB** each:

- **General** — Wikipedia-derived English (WikiText-103-raw).
- **Azure** — 20 Azure documentation services from `MicrosoftDocs/azure-docs`
  (`azure_train` split; `AZURE_TRAIN_DOCS` = 3,799 documents after dedup/holdout).
- **Mixed** — a deterministic document-by-document 50/50 interleave of the two.

Corpora are matched on cleaned UTF-8 **bytes** (not document count) and are
sampled deterministically from a single global seed (`SEED` = 20260709). See
[methodology](methodology.md).

## Evaluation sets (nine)

1. `azure_cross_service_holdout` — **principal** set: whole Azure services never
   seen in training (`CROSS_SERVICE_HOLDOUT_SERVICES` = 5 services, 964 documents).
2. `azure_same_service_holdout` — held-out documents from services also in training,
   near-duplicate-isolated.
3. `ms_architecture` — MicrosoftDocs/architecture-center.
4. `ms_devops` — MicrosoftDocs/azure-devops-docs.
5. `ms_data` — MicrosoftDocs/sql-docs + fabric-docs.
6. `ms_broad_enterprise` — MicrosoftDocs/microsoft-365-docs.
7. `external_technical` — kubernetes/website (non-Microsoft technical docs).
8. `general_english` — held-out WikiText, disjoint from General training.
9. `synthetic` — diagnostic edge cases (resource providers, CLI, GUIDs, JSON/YAML/…).

## Endpoints

**Primary endpoint** — tokens per 1,000 UTF-8 bytes, reported both **micro** (over
all bytes) and **macro** (mean of per-document ratios):

```text
tokens_per_1000_bytes(T, D) = 1000 * total_tokens(T, D) / total_utf8_bytes(D)
```

**Primary effect size** — relative token reduction (positive = specialized uses
fewer tokens):

```text
relative_reduction(A vs G, D) = 100 * [tokens(G, D) - tokens(A, D)] / tokens(G, D)
```

**Secondary endpoints:** transfer across eval sets, vocabulary-size sensitivity,
content-type breakdown, fragmentation, vocabulary utilization, coverage
(round-trip / `[UNK]`), and CPU throughput.

## Statistical method

Token counts are deterministic; uncertainty comes from the sampled documents. We
use a **paired bootstrap over documents** (`BOOTSTRAP_RESAMPLES` = 10,000
resamples, the same documents paired across the two tokenizers), reporting 95%
confidence intervals for the relative token reduction, stratified by repository
and content type, and a document-level win rate. See
[`../src/msdocs_tokenizer/stats.py`](../src/msdocs_tokenizer/stats.py).

## Leakage controls

- **Group-aware split:** whole Azure **services** are routed to the cross-service
  holdout (service-disjoint from training). Within training services, whole
  near-duplicate clusters are held out as the same-service holdout.
- **Exact + near-duplicate removal:** exact duplicates (SHA-256) and MinHash
  near-duplicates are removed from Azure before splitting; the General corpus is
  exact-deduplicated **before** the train/eval split (`DEDUP_GENERAL_EXACT` = 134
  removed); evaluation items that are near-duplicates of any training document are
  removed (`CROSS_CORPUS_REMOVED` = 9).
- **Byte-match verification:** all three corpora are exactly 33,554,432 bytes
  (`BYTE_MATCH_OK` = true), so no tokenizer sees more training text.

## Frozen decisions and deviations

- Frozen spec: [`../research/EXPERIMENT_SPEC.md`](../research/EXPERIMENT_SPEC.md).
- Deviations: [`../research/DEVIATIONS.md`](../research/DEVIATIONS.md) — notably the
  training budget was reduced from the planned 256 MiB to **32 MiB** because the
  available `azure_train` cleaned text caps at ~38.8 MiB; the full nine-tokenizer
  matrix and all analyses are delivered at 32 MiB.

## Track A vs Track B

- **Track A (controlled):** General / Azure / Mixed × 8K/16K/32K byte-level BPE —
  identical except the training corpus. This is the causal comparison.
- **Track B (observational):** existing `tiktoken` tokenizers (`r50k_base`,
  `cl100k_base`, `o200k_base`). They differ in training data, vocabulary,
  normalization, algorithm, and intended model, so they are reported separately
  and are **not** a controlled comparison.

See also: [methodology](methodology.md) · [results](results.md) ·
[limitations](limitations.md) · [`../publication/CLAIM_LEDGER.md`](../publication/CLAIM_LEDGER.md).
