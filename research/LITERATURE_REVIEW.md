# Literature review: domain-specialized tokenizer efficiency

## Scope and verification status

This review supports a CPU-only study of domain-specialized tokenizer efficiency for Azure/Microsoft documentation.

It is deliberately framed as a controlled, reproducible case study, not as a claim that domain-specialized tokenization is novel.

The plan-cited arXiv IDs were checked on 2026-07-10 using `https://arxiv.org/abs/<id>` and the arXiv API.

All three plan-cited works resolved:

- Liyanage and Yvon, "AdaptBPE: From General Purpose to Specialized Tokenizers," arXiv:2601.21665, EACL 2026.
- Herold et al., "Vocabulary Customization for Efficient Domain-Specific LLM Deployment," arXiv:2509.26124, NEURIPS 2025 CCFM Workshop.
- Balde et al., "Learning Faster with Better Tokens: Parameter-Efficient Vocabulary Adaptation for Specialized Text Summarization," arXiv:2605.17379, ACL 2026.

Because these papers are future relative to many tokenizer surveys but resolved in arXiv at the current project date, they are treated as verified but still as claims needing independent replication.

No unverified plan-cited paper details are invented.

Official implementation references were also checked:

- OpenAI `tiktoken`: https://github.com/openai/tiktoken
- Hugging Face Tokenizers docs: https://huggingface.co/docs/tokenizers/index
- Google SentencePiece: https://github.com/google/sentencepiece

## Research question positioning

The project asks a narrow efficiency question: how much token-count and CPU-runtime behavior changes when a tokenizer is specialized to Azure/Microsoft documentation rather than kept general-purpose.

The prior work already establishes that subword tokenizers are data-dependent, vocabulary-limited, and sensitive to language or domain distribution.

Therefore, our contribution should be described as experimental control, reproducibility, and a domain-specific measurement case study.

It should not be described as inventing domain-specialized tokenization.

## Background: fixed vocabularies and open-vocabulary text

Modern neural language systems usually map raw text into integer token IDs using a fixed vocabulary.

The fixed vocabulary is a computational convenience, but natural language, code, product names, API identifiers, and document paths are open-ended.

Sennrich, Haddow, and Birch (2016) introduced BPE subword units for neural machine translation to reduce rare-word and unknown-word failures.

Their key idea was to encode rare and unseen words as sequences of learned subword units, allowing open-vocabulary translation with a fixed vocabulary.

The same core tradeoff appears in our project: a tokenizer trained on broad text can encode arbitrary Azure documentation, but it may do so with unnecessarily many tokens.

## Byte Pair Encoding (BPE)

BPE begins from small units and repeatedly merges frequent adjacent pairs.

In compression, the goal is byte-level compression; in NLP, the learned merge table becomes a subword vocabulary.

BPE tends to allocate whole or large subword tokens to frequent strings in the tokenizer-training corpus.

This means BPE is inherently corpus-adaptive: frequent domain terms can become compact tokens if the domain corpus is present during tokenizer training.

Sennrich et al. reported improved WMT15 English-German and English-Russian BLEU with BPE subwords compared with a back-off dictionary baseline.

For our study, the relevant takeaway is not BLEU; it is that BPE vocabulary contents depend on corpus frequency and affect sequence length.

## Byte-level BPE

Byte-level BPE removes most text-normalization and unknown-character problems by operating over bytes before BPE merges.

GPT-2 used byte-level BPE with a 50,257-token vocabulary and the WebText corpus.

OpenAI `tiktoken` implements fast BPE tokenization for OpenAI models and notes that, in practice, BPE compresses text so each token corresponds to roughly four bytes on average.

`tiktoken` also reports 3-6x speed compared with a comparable open-source tokenizer in its README benchmark.

For this project, byte-level BPE is a natural baseline because it is robust on arbitrary Azure strings, code snippets, IDs, markdown, and URLs.

However, byte-level robustness does not imply optimal compression for a specialized corpus.

## WordPiece

WordPiece is a subword tokenization approach associated with Google's Japanese and Korean voice-search work and later with BERT-family models.

Schuster and Nakajima (2012) used data-driven segmentation for languages with no whitespace-delimited words and complex script behavior.

BERT-style WordPiece vocabularies are typically fixed after pretraining.

SciBERT is especially relevant because it studied scientific-domain pretraining and released variants using both the original BERT vocabulary and a domain-specific SCIVOCAB.

SciBERT demonstrates that training a domain vocabulary is an established strategy in specialized NLP.

BioBERT is a useful boundary case: it adapted BERT to biomedical text mainly through continued pretraining while retaining BERT's original WordPiece vocabulary for compatibility.

This contrast helps us avoid overstating tokenization: domain adaptation can help even without changing the tokenizer, and tokenizer specialization is only one design axis.

## Unigram LM and SentencePiece

Kudo (2018) introduced subword regularization and a unigram-language-model tokenizer that samples multiple segmentations during training.

The paper frames segmentation ambiguity as useful noise that can improve robustness, especially in low-resource and out-of-domain machine translation.

Kudo and Richardson (2018) introduced SentencePiece as a language-independent tokenizer/detokenizer that trains directly from raw sentences.

SentencePiece implements both BPE and Unigram and avoids assuming whitespace-pretokenized input.

The official SentencePiece repository describes it as fast, lightweight, unsupervised, and designed for fixed-vocabulary neural text generation systems.

For our study, SentencePiece is a candidate implementation path or conceptual reference, but our CPU-only evaluation should isolate algorithmic choices from implementation speed where possible.

## Fertility and compression metrics

Tokenizer fertility is commonly used to mean the average number of tokens per word, or more generally the number of subword tokens needed to encode a unit of text.

Related compression metrics include tokens per byte, bytes per token, characters per token, tokens per whitespace-delimited word, and sequence length relative to a baseline tokenizer.

Rust et al. (2021) studied multilingual and monolingual tokenizers and found that specialized monolingual tokenizers can improve downstream performance when compared under controlled data conditions.

Petrov et al. (2023) showed that tokenization alone can create multilingual unfairness: translated versions of the same text can differ in tokenized length by up to 15x, and even byte/character approaches can differ by more than 4x for some language pairs.

Ali et al. (2024) cautioned that fertility and parity are not always predictive of downstream LLM performance, despite being useful intrinsic diagnostics.

The boundary for our study is therefore clear: tokens-per-byte and tokens-per-word are valid efficiency outcomes, but we should not claim they guarantee model quality improvements.

## Domain and vocabulary adaptation

Domain vocabulary mismatch occurs when frequent in-domain strings are rare or absent in the tokenizer-training corpus.

In Azure documentation, examples include service names, SKU names, CLI flags, resource IDs, namespaces, API paths, error codes, markdown tables, YAML, JSON, and command snippets.

Prior work already studies adapting vocabularies to target domains.

Sachidananda et al. (2021) is explicitly titled "Efficient Domain Adaptation of Language Models via Adaptive Tokenization" and appears in ACL Anthology.

Nayak et al. (2020) focused on BERT tokenization and subword representation challenges for out-of-vocabulary words under domain adaptation.

Dagan et al. (2024) trained specialized BPE tokenizers for code and found that tokenizer size, pre-tokenization regex, and training data can significantly affect generation speed, effective context size, memory usage, downstream performance, and tokenizer-switching decisions.

The 2025-2026 plan-cited works go further into post-training or parameter-efficient vocabulary adaptation, including token replacement, extension, and domain-specific token selection.

This body of work proves the high-level idea is not novel.

## Domain examples relevant to our framing

SciBERT trained on scientific publications and introduced SCIVOCAB variants.

LEGAL-BERT investigated legal-domain BERT adaptation strategies, including from-scratch pretraining on legal corpora.

CodeBERT and Dagan et al. are relevant to code-like corpora because Azure documentation contains command lines, configuration files, API names, and identifiers.

BioBERT shows a domain-adaptive pretraining path that does not require tokenizer replacement.

Together these examples motivate our choice to evaluate tokenization efficiency separately from downstream model quality.

## How this project differs / what is novel vs not

Not novel:

- Subword tokenization.
- BPE, byte-level BPE, WordPiece, Unigram, or SentencePiece.
- Training tokenizers on domain corpora.
- Vocabulary extension, replacement, or adaptation.
- Reporting fertility or token compression metrics.
- Observing that domain vocabulary mismatch can increase token counts.

Potentially novel or useful in our project:

- A controlled, reproducible Azure/Microsoft-docs case study.
- CPU-only measurements that separate tokenizer training, encoding throughput, and corpus compression.
- A documented corpus construction pipeline for Microsoft documentation text, markdown, code blocks, CLI snippets, URLs, and identifiers.
- Side-by-side evaluation against general-purpose tokenizers used in current LLM tooling.
- A transparent claim ledger that maps every external claim to an intrinsic measurement or explicit boundary.

The safest project claim is: "Prior work shows tokenizers are corpus-sensitive; we measure how that sensitivity manifests for Azure/Microsoft documentation under a reproducible CPU-only protocol."

## Reusable methodology

The literature suggests a reusable methodology with the following steps.

1. Define corpus boundaries and licensing/redistribution constraints.

2. Preserve domain artifacts such as markdown, code blocks, paths, URLs, command-line flags, JSON, YAML, ARM/Bicep snippets, and API identifiers.

3. Train or adapt tokenizers using fixed algorithms, vocabulary sizes, normalization, pre-tokenization, and random seeds.

4. Compare against general-purpose baselines such as GPT-2 byte-level BPE, OpenAI/tiktoken encodings, SentencePiece baselines, and Hugging Face tokenizers where appropriate.

5. Report intrinsic compression metrics: total tokens, tokens per byte, bytes per token, tokens per whitespace word, and token-count reduction relative to each baseline.

6. Report runtime metrics on CPU: training wall time, encode wall time, documents per second, bytes per second, and peak memory if available.

7. Stratify results by document type: prose, markdown tables, code blocks, CLI examples, JSON/YAML, URLs, API paths, and mixed documents.

8. Include statistical uncertainty: bootstrap confidence intervals over documents, paired tests across tokenizers, and effect sizes for token-count differences.

9. Inspect token inventories for domain strings, but treat qualitative examples as explanatory, not primary evidence.

10. Bound claims about downstream model quality unless the project actually trains or evaluates language models.

## Claim boundaries for our study

We can claim token-count efficiency if measured directly.

We can claim CPU tokenizer throughput if measured directly on the project hardware.

We can claim corpus-specific vocabulary overlap if computed from held-out Azure/Microsoft docs.

We should not claim inference latency gains for an LLM unless an LLM inference experiment is run.

We should not claim accuracy, factuality, summarization quality, or retrieval quality improvements from tokenizer changes alone.

We should not claim fairness across languages unless multilingual corpora and language-aware controls are added.

We should not claim generality beyond Azure/Microsoft documentation without evaluating other technical-documentation corpora.

## Recommended baselines

Use at least one byte-level BPE baseline, because Azure documentation contains arbitrary bytes, code, paths, and identifiers.

Use a widely used production tokenizer such as OpenAI/tiktoken when licensing and reproducibility permit.

Use a train-from-scratch domain tokenizer at matched vocabulary sizes.

If vocabulary adaptation is implemented, compare it against both expansion-only and fixed-size replacement where feasible.

Keep vocab size constant when testing whether domain token selection alone improves compression.

Vary vocab size only in a separate scaling experiment.

## Key risks from prior work

Intrinsic metrics may not predict downstream model quality.

Fertility can improve while semantic modeling remains unchanged or worsens.

Tokenizer changes can require embedding resizing or retraining if used inside a pretrained LLM.

Implementation speed can confound algorithmic compression.

Domain corpora can leak benchmark or evaluation documents if train/test splits are not documented.

Rare but safety-critical identifiers may remain fragmented even if average compression improves.

## Bottom line

Prior work strongly supports the hypothesis that tokenizer efficiency depends on the tokenizer-training corpus and vocabulary design.

The same prior work also prevents novelty overclaiming.

Our project should be presented as a careful measurement study for Azure/Microsoft documentation, with explicit boundaries around compression, CPU runtime, and reproducibility.
