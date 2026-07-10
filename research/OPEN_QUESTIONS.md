# Open methodological questions and risks

## Corpus construction

- What exact Microsoft/Azure documentation sources are in scope: learn.microsoft.com pages, GitHub markdown, REST API docs, samples, CLI docs, SDK docs, or all of them?
- Are code blocks, YAML, JSON, Bicep, ARM templates, CLI commands, URLs, and tables retained exactly, normalized, or stratified?
- How are redirects, duplicated pages, generated reference pages, localized pages, and versioned docs deduplicated?
- What train/validation/test split prevents the tokenizer from being evaluated on the same pages used to train it?
- Can the corpus or enough metadata be redistributed for reproducibility under licensing constraints?

## Tokenizer design

- Are we training from scratch, adapting an existing tokenizer, augmenting with extra tokens, or replacing low-utility tokens at fixed vocabulary size?
- Which algorithms are in scope: byte-level BPE, standard BPE, WordPiece, Unigram/SentencePiece, or only one implementation family?
- What vocabulary sizes should be compared, and which experiments keep vocab size fixed versus scaling it?
- What normalization rules are allowed for technical documentation without destroying paths, flags, casing, or identifiers?
- Should pre-tokenization split on markdown/code punctuation, or should byte-level processing preserve all structure?

## Baselines

- Which production/general tokenizers are legally and technically appropriate baselines: GPT-2 byte-level BPE, OpenAI/tiktoken encodings, SentencePiece defaults, Hugging Face tokenizers, or model-specific tokenizers?
- If an implementation is much faster, is that an algorithmic result or a systems-implementation result?
- Should baselines be compared by token count only, runtime only, or both?
- How do we handle tokenizers that are not reversible or that normalize whitespace/casing differently?

## Metrics

- Primary intrinsic metrics should likely include total tokens, tokens per byte, bytes per token, tokens per whitespace word, and relative token reduction.
- Runtime metrics should include CPU encode wall time, bytes/sec, docs/sec, and possibly peak memory.
- Do we need training-time measurements for tokenizer construction, or only encode-time metrics?
- Should results be weighted by bytes, documents, pages, or product area?
- How should very large generated reference pages be prevented from dominating aggregate metrics?

## Statistical design

- Use paired document-level comparisons because every tokenizer encodes the same document set.
- Bootstrap confidence intervals over documents for token-count reduction and encode throughput.
- Consider stratified bootstrap by document type or product area.
- Report effect sizes, not only p-values.
- Decide whether to pre-register minimum meaningful effect sizes for token reduction and CPU throughput.

## Claim boundaries

- Token-count reductions do not prove downstream model quality improvements.
- Token-count reductions do not prove LLM latency improvements unless the target inference stack is measured.
- CPU tokenizer throughput does not imply GPU or server-side inference throughput.
- Azure/Microsoft documentation results do not automatically generalize to legal, biomedical, code-only, or multilingual corpora.
- Domain-token examples do not prove corpus-level benefit without held-out metrics.

## Reproducibility risks

- Documentation changes over time; snapshots and content hashes are needed.
- Web scraping may introduce nondeterminism through redirects, templates, navigation text, or localized content.
- Tokenizer training can be nondeterministic unless seeds, thread counts, versions, and corpus order are fixed.
- Different libraries may count bytes, Unicode normalization, or special tokens differently.
- Special-token policies can silently change totals if BOS/EOS/metadata tokens are included inconsistently.

## Interpretation risks

- A tokenizer can reduce average token count while worsening rare but important identifiers.
- A domain tokenizer can overfit the training snapshot and compress stale product names.
- A tokenizer may allocate tokens to boilerplate navigation or repeated legal text rather than useful Azure concepts.
- A smaller token count may not help if downstream models need embedding resizing or retraining.
- Fertility and parity are diagnostics, not full substitutes for downstream evaluation.

## Recommended decisions before experiments

1. Freeze a corpus snapshot and document inclusion/exclusion rules.
2. Define train/test splits by page or repository path before training tokenizers.
3. Pick a primary baseline tokenizer and one secondary baseline.
4. Pick a primary vocabulary size and decide whether fixed-size replacement is in scope.
5. Decide whether the paper's main claim is token-count reduction, CPU throughput, or both.
6. Predefine document strata for reporting: prose, markdown-heavy pages, code blocks, JSON/YAML, CLI/reference, and URL/API-heavy pages.
7. Record all tokenizer settings in machine-readable metadata.
8. Keep downstream-model claims out of scope unless a separate model evaluation workstream is added.
