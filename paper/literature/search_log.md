# Literature search log

Access date: 2026-07-10.

## Continuity sources read

- `research/LITERATURE_REVIEW.md`: used to preserve prior experiment-phase framing and claim boundaries.
- `research/PAPER_MATRIX.csv`: used to avoid losing prior verified context, but citations were rechecked for this paper package.
- `plan-2.md` sections 15-16: used for candidate arXiv IDs and title candidates.

## Required arXiv candidate verification

For each plan-candidate ID, `web_fetch` was run on `https://arxiv.org/abs/<id>` and arXiv API metadata was used to capture authors, year, version, comments, and abstracts.

- `arXiv:2109.07460`: resolved. Actual title: "Efficient Domain Adaptation of Language Models via Adaptive Tokenization". Also verified ACL Anthology published version `2021.sustainlp-1.16`.
- `arXiv:2410.03258`: resolved. Actual title: "Adaptive BPE Tokenization for Enhanced Vocabulary Adaptation in Finetuning Pretrained Language Models". Also verified ACL Anthology `2024.findings-emnlp.863`.
- `arXiv:2502.20273`: resolved. Actual title: "How Much is Enough? The Diminishing Returns of Tokenization Training Data". Current version v4.
- `arXiv:2503.17247`: resolved. Actual title: "KL3M Tokenizers: A Family of Domain-Specific and Character-Level Tokenizers for Legal, Financial, and Preprocessing Applications".
- `arXiv:2509.26124`: resolved. Actual title: "Vocabulary Customization for Efficient Domain-Specific LLM Deployment".
- `arXiv:2601.21665`: resolved. Actual title: "AdaptBPE: From General Purpose to Specialized Tokenizers".
- `arXiv:2605.17379`: resolved. Actual title: "Learning Faster with Better Tokens: Parameter-Efficient Vocabulary Adaptation for Specialized Text Summarization".
- `arXiv:2510.09947`: resolved. Actual title: "Beyond Fertility: Analyzing STRR as a Metric for Multilingual Tokenization Evaluation". Current version v2.
- `arXiv:2606.15044`: resolved. Actual title: "Equity with Efficiency: An Empirical Study of Tokenizers for Multilingual Large Language Models".

No required plan-candidate ID failed to resolve. Titles matched `plan-2.md`; several user-provided parenthetical titles were shortened forms and should not be used as formal titles.

## Foundational queries and fetches

- Fetched ACL Anthology `P16-1162`: BPE for NMT, Sennrich et al. 2016.
- Fetched ACL Anthology `P18-1007`: subword regularization and Unigram LM, Kudo 2018.
- Fetched ACL Anthology `D18-2012`: SentencePiece, Kudo and Richardson 2018.
- Searched: "Schuster Nakajima Japanese and Korean voice search WordPiece 2012 primary source". DOI metadata for `10.1109/ICASSP.2012.6289079` verified title/authors/pages. IEEE page was reachable but did not expose useful abstract text through `web_fetch`.
- Fetched arXiv `1810.04805`: BERT as a WordPiece-era fixed-vocabulary pretrained model reference.
- Fetched OpenAI GPT-2 technical report PDF URL; used only for GPT-2/byte-level BPE background.
- Fetched official `https://github.com/huggingface/tokenizers`: verified BPE/WordPiece/Unigram support and Rust performance framing.
- Fetched official `https://github.com/openai/tiktoken`: verified fast BPE tokenizer framing, 3-6x benchmark statement, and README claims about reversible/lossless arbitrary-text BPE.

## Additional related-work search/fetches

- Fetched arXiv/ACL/PMLR pages for `rust2021tokenizer`, `petrov2023unfairness`, `ali2024tokenizerchoice`, `dagan2024tokenizer`, `lee2022dedup`, `beltagy2019scibert`, `lee2019biobert`, `chalkidis2020legalbert`, and `feng2020codebert`.
- Searched: "NeurIPS 2023 Language Model Tokenizers Introduce Unfairness Between Languages proceedings". The official NeurIPS URL was identified, but `web_fetch` simplified output exposed minimal metadata; arXiv primary page was retained for accurate claims.
- Search for tokenizer fertility/compression metrics surfaced common definitions, but claims were tied to fetched primary sources (`nayeem2025strr`, `petrov2023unfairness`, `ali2024tokenizerchoice`, `openai2026tiktoken`) rather than snippets.

## Exclusions and cautions

- Did not cite search snippets as evidence.
- Did not cite downstream performance works as evidence for this paper's tokenizer compression outcome.
- Did not include unverified venue claims beyond source comments/pages.
- Did not infer exact corpus sizes or vocabulary sizes when abstracts/pages did not expose them.
- Did not include inaccessible/paywalled WordPiece details beyond DOI-verified bibliographic metadata and conservative historical framing.
