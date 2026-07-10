# Limitations

This study measures **tokenizer compression only**. The limitations below are
material; we state them plainly and do not minimize them. See also the "What this
does not measure" section of the [README](../README.md) and the paper's
"What this study is and is not".

## Design and scope

- **32 MiB training budget.** Corpora are byte-matched at 32 MiB each — a small
  budget bounded by the available cleaned `azure_train` text (~38.8 MiB). Absolute
  token counts are budget-dependent; larger budgets could shift them. The
  controlled comparison and effect sizes are valid at this scale.
- **One tokenizer algorithm for the controlled matrix.** Only byte-level BPE is
  used for the causal comparison. Unigram/WordPiece are not part of the controlled
  matrix.
- **Documentation-specific source distributions.** Sources are technical
  documentation; results may not extend to chat, source-code repositories, prose
  books, or all enterprise text.
- **The Azure-vs-general-English confound (most important).** Comparing Azure
  documentation with general English changes **more than subject domain** — it
  also changes technical writing style, markup distribution, identifier density,
  and document structure. The transfer and prose-only analyses *narrow* this
  concern (the gain persists on prose and transfers to non-Microsoft Kubernetes
  docs) but do **not** fully isolate Azure-specific vocabulary from general
  technical-documentation specialization. **A matched general-technical
  documentation training control is the priority future experiment.**
- **Limited evidence about causality within subcomponents.** We can attribute the
  aggregate effect to corpus composition, but not cleanly decompose it into
  "resource-provider names" vs "documentation style" vs "identifier density".

## What we did not do

- **No language-model training.** No model was trained or fine-tuned.
- **No downstream quality evaluation.** No accuracy, reasoning, or task metric.
- **No GPU or serving benchmark.** No inference latency, prefill, KV-cache, or
  throughput measurement.
- **CPU runtime is laptop-variable.** Throughput was measured on a thermally
  variable laptop; small differences are not overinterpreted, and CPU tokenizer
  throughput is **not** model-serving throughput.

## Data and reproduction

- **Public-repository snapshot dependence.** Results are tied to the pinned source
  commits; upstream documentation changes over time.
- **License-constrained redistribution.** Raw corpora are not redistributed;
  reproduction downloads pinned public sources. The General and Mixed (WikiText-
  derived) tokenizer artifacts are local-use-only pending license clarification.
- **No claim of universal domain transfer.** Transfer was measured on specific
  corpora; it is not evidence of universal domain-tokenizer superiority.

## Comparison caveats

- **Existing tokenizers are not controlled.** `tiktoken` baselines (Track B)
  differ in training data, vocabulary, normalization, algorithm, and intended
  model; they are observational context, not a causal comparison.
- **Estimates are labeled as estimates.** Any context-window or token-billing
  figure is a derived estimate, not a measured GPU or billing outcome.

## Affiliation and endorsement

- **Potential author-employer relationship and non-endorsement.** If the author is
  affiliated with Microsoft, that relationship is disclosed where applicable; this
  study uses only public documentation, is not an official Microsoft result, and
  implies no endorsement. See
  [`../publication/AUTHOR_INPUTS_REQUIRED.md`](../publication/AUTHOR_INPUTS_REQUIRED.md).

## Recommended future control

Train a **matched general-technical-documentation** tokenizer (e.g., broad
non-Microsoft technical docs) to separate general technical-documentation style
from Azure-specific specialization; add more mixture ratios and training sizes;
and, separately, evaluate an adapted tokenizer inside a small model trained from
scratch to measure any downstream effect. These are future work — none are claimed
here.
