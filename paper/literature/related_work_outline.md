# Related-work outline

## Paragraph 1: Subword tokenization foundations

Cite: `sennrich2016bpe`, `schuster2012wordpiece`, `kudo2018subword`, `kudo2018sentencepiece`, `radford2019gpt2`, `devlin2019bert`.

Differentiation: these works define the tokenizer families and open-vocabulary motivation; this paper does not introduce a new tokenizer algorithm.

## Paragraph 2: Byte-level BPE and implementation baselines

Cite: `radford2019gpt2`, `openai2026tiktoken`, `huggingface2026tokenizers`.

Differentiation: these sources motivate robust byte-level/prod tokenizer baselines, while the controlled comparison in this paper varies training corpus under a matched byte-level BPE setup.

## Paragraph 3: Domain-specific tokenizers trained on domain corpora

Cite: `beltagy2019scibert`, `chalkidis2020legalbert`, `bommarito2025kl3m`, `dagan2024tokenizer`, `feng2020codebert`.

Differentiation: prior domain work includes scientific, legal, financial, governmental, biomedical, and code settings; this paper focuses on cloud/technical documentation and isolates compression rather than model quality.

## Paragraph 4: Vocabulary adaptation for existing models

Cite: `sachidananda2021adaptive`, `balde2024adaptivebpe`, `herold2025vocabulary`, `liyanage2026adaptbpe`, `balde2026learning`.

Differentiation: those methods adapt or augment existing tokenizers and often evaluate downstream tasks; this paper trains tokenizers from scratch under byte-matched corpora and reports intrinsic compression only.

## Paragraph 5: Pre-tokenization and scaling choices

Cite: `kudo2018sentencepiece`, `dagan2024tokenizer`, `reddy2025diminishing`.

Differentiation: prior work shows pre-tokenization, tokenizer size, and training-data size matter; this paper fixes byte-level BPE design choices to study corpus composition and vocabulary-size sensitivity.

## Paragraph 6: Fertility, compression, and fairness metrics

Cite: `petrov2023unfairness`, `nayeem2025strr`, `ali2024tokenizerchoice`, `rust2021tokenizer`.

Differentiation: these works show token counts matter but are incomplete proxies; this paper reports compression as the outcome and explicitly avoids downstream quality/fairness claims.

## Paragraph 7: Leakage and evaluation controls

Cite: `lee2022dedup`.

Differentiation: deduplication literature motivates train/eval separation; this paper applies leakage controls to tokenizer-compression evaluation rather than language-model evaluation.

## Suggested bridge sentence into contribution

"Taken together, prior work establishes that tokenizer inventories are corpus-sensitive and can affect efficiency and downstream systems; our contribution is a controlled, byte-matched, leakage-controlled case study measuring how that sensitivity manifests as compression on technical documentation, including the tradeoff between full specialization and mixed-domain training."
