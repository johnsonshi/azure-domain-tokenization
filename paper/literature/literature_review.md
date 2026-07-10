# Literature review: domain-specialized byte-level BPE compression for technical documentation

Access date for verification: 2026-07-10. This review uses primary sources: arXiv abstract pages for all plan-candidate preprints, ACL/PMLR/NeurIPS/proceedings pages where available, DOI metadata for WordPiece, and official software repositories for `tokenizers` and `tiktoken`. It deliberately frames the current paper as a controlled tokenizer-compression case study, not as an invention of domain-specialized tokenization or evidence about downstream LLM quality.

## Position of this study

This paper sits primarily in two methodological categories: **training a tokenizer from scratch on domain data** and **measuring fertility/compression**. The experiment trains byte-level BPE tokenizers under a fixed CPU-only, byte-matched corpus budget and evaluates token counts on held-out technical documentation. It does not adapt a pretrained language model, resize embeddings, continue pretraining, measure generation quality, or benchmark model serving latency.

The gap it fills is therefore empirical and methodological: a controlled, byte-matched, leakage-controlled corpus-composition case study for cloud/technical documentation, including a mixed-domain tradeoff, with compression-only claims.

## (a) Training a tokenizer from scratch on domain data

BPE subword tokenization entered neural NLP through Sennrich et al. \cite{sennrich2016bpe}, who used frequency-driven subword units to reduce rare-word and unknown-word failures in neural machine translation. The important methodological connection is not their BLEU result but the corpus dependence of the learned merge inventory: frequent strings in the tokenizer-training corpus become cheaper to encode.

Domain-specific model families show that specialized corpora and vocabularies are well established. SciBERT \cite{beltagy2019scibert} used scientific publications and released variants around scientific-domain pretraining and vocabulary; LEGAL-BERT \cite{chalkidis2020legalbert} explored original, continued-pretraining, and from-scratch legal BERT strategies; KL3M tokenizers \cite{bommarito2025kl3m} report professional-domain BPE and character-level tokenizers for legal, financial, and governmental text. Code-oriented work by Dagan et al. \cite{dagan2024tokenizer} is especially relevant because technical documentation contains prose mixed with code, identifiers, paths, command lines, markdown, JSON, and YAML.

The present study is narrower than these works. It isolates compression under byte-level BPE, rather than conflating tokenizer choice with representation learning, pretraining data scale, or downstream task quality.

## (b) Extending or replacing vocabulary in an existing model

A separate line of work keeps an existing pretrained model or tokenizer family and changes its vocabulary. Sachidananda et al. \cite{sachidananda2021adaptive} adapt RoBERTa tokenizers by selecting domain-specific subword sequences from distributional divergence. Balde et al. \cite{balde2024adaptivebpe} show that naively appending tokens to a BPE vocabulary can be suboptimal because added tokens receive low priority; their AdaptBPE changes initialization to prefer longest matches in the added target vocabulary. Herold et al. \cite{herold2025vocabulary} augment an existing tokenizer with a no-worse tokenization guarantee. Liyanage and Yvon \cite{liyanage2026adaptbpe} replace low-utility BPE tokens while keeping target vocabulary size fixed. Balde et al. \cite{balde2026learning} combine replacement and expansion for legal and medical summarization.

These papers demonstrate that vocabulary adaptation is not new. They also mark a boundary: once a pretrained model is used, token changes interact with embedding initialization, parameter growth, and adaptation training. This paper avoids those confounds by measuring tokenization compression only.

## (c) Changing pre-tokenization

Pre-tokenization can dominate what a tokenizer can learn. SentencePiece \cite{kudo2018sentencepiece} trains subword models directly from raw sentences, avoiding a required whitespace-tokenized input. WordPiece grew out of data-driven segmentation for Japanese and Korean voice search \cite{schuster2012wordpiece} and was later central to BERT-style models \cite{devlin2019bert}. Kudo's subword regularization \cite{kudo2018subword} treats segmentation ambiguity as train-time noise through sampled segmentations and a Unigram LM tokenizer.

For code and technical text, pre-tokenization choices are not cosmetic. Dagan et al. \cite{dagan2024tokenizer} report that tokenizer size, pre-tokenization regular expression, and training data affect code-model generation speed, effective context, memory, and downstream performance. Reddy et al. \cite{reddy2025diminishing} further attribute some tokenizer training-data saturation to constraints introduced by pre-tokenization. Our study chooses byte-level BPE to avoid unknown tokens and preserve exact reconstruction, but it does not claim the chosen pre-tokenization is universally optimal.

## (d) Multilingual equity

Multilingual tokenizer work makes token length an access and equity issue. Rust et al. \cite{rust2021tokenizer} show that monolingual tokenizers can matter for downstream performance under controlled multilingual/monolingual data comparisons. Petrov et al. \cite{petrov2023unfairness} show that translated versions of the same text can have large tokenized-length disparities, affecting cost, latency, and context capacity. Nayeem et al. \cite{nayeem2025strr} argue that fertility can hide vocabulary allocation and propose STRR as a complementary metric. Lee et al. \cite{lee2026equity} evaluate efficiency-equity tradeoffs for Southeast Asian languages with controlled model training.

These studies are adjacent. They justify caring about token counts, but the present experiment is English-centric technical documentation and should not make multilingual fairness claims.

## (e) Measuring fertility/compression

Fertility is commonly used as average tokens per word; related intrinsic measures include tokens per byte, bytes per token, characters per token, total token count, and relative token reduction versus a baseline. `tiktoken`'s README \cite{openai2026tiktoken} frames BPE as reversible/lossless, arbitrary-text capable, and compressive; Nayeem et al. \cite{nayeem2025strr} explicitly identify fertility as a compression-efficiency metric while warning about its blind spots. Petrov et al. \cite{petrov2023unfairness} and Ali et al. \cite{ali2024tokenizerchoice} reinforce that token length is meaningful but incomplete.

This paper's main claims belong here: fewer tokens per UTF-8 byte and relative token-count reductions under controlled train/eval splits. The paper should avoid saying the tokenizer is more semantically correct or that compression automatically improves model quality.

## (f) Measuring downstream model performance

Many cited works include downstream tasks: Sennrich et al. report MT BLEU \cite{sennrich2016bpe}; Kudo reports NMT improvements \cite{kudo2018subword}; Rust et al. evaluate monolingual tasks \cite{rust2021tokenizer}; Ali et al. train 24 LLMs and show tokenizer choice can affect performance and cost \cite{ali2024tokenizerchoice}; Dagan et al. evaluate code generation \cite{dagan2024tokenizer}; Sachidananda, Balde, Herold, Liyanage, and Balde et al. 2026 evaluate model adaptation or deployment tasks \cite{sachidananda2021adaptive,balde2024adaptivebpe,herold2025vocabulary,liyanage2026adaptbpe,balde2026learning}.

Those results should be cited only to situate the broader field. They are not evidence that the current tokenizer improves LLM accuracy, reasoning, summarization, retrieval, or safety.

## (g) Training-data and vocabulary-size scaling

Reddy et al. \cite{reddy2025diminishing} directly study tokenizer training-data size across BPE, UnigramLM, and WordPiece, reporting diminishing returns at much larger scales than this experiment. Dagan et al. \cite{dagan2024tokenizer} vary tokenizer size and pre-tokenization for code. Liyanage and Yvon \cite{liyanage2026adaptbpe} adapt token inventories for a fixed target vocabulary size, while Herold et al. \cite{herold2025vocabulary} expands an existing vocabulary.

The current study's 32 MiB byte-matched corpora and 8K/16K/32K controlled matrix should be presented as a controlled case-study scale, not a universal scaling law.

## (h) Leakage and deduplication in tokenizer evaluation

Lee et al. \cite{lee2022dedup} show that near-duplicate examples and train-test overlap can distort language-model training and evaluation. Although tokenizer compression is not language modeling, leakage can still inflate compression estimates if evaluation documents or near duplicates appear in tokenizer-training data. Therefore, exact-duplicate removal, cross-corpus near-duplicate filtering, source locks, and explicit held-out service splits are central methodological contributions of the current study.

## Claim boundaries for the manuscript

Safe claims:

- A domain-trained byte-level BPE tokenizer uses fewer tokens on held-out Azure/technical documentation under this controlled setup.
- Mixed-domain tokenizer training measures the tradeoff between in-domain compression and general-English regression.
- Tokenizer compression and CPU tokenizer throughput are distinct measured quantities.

Unsafe claims:

- Better LLM quality, factuality, reasoning, retrieval, summarization, or safety.
- Measured GPU inference latency or billing savings.
- Universal superiority of domain-specific tokenizers.
- Multilingual fairness.
- Novel invention of domain tokenization.
