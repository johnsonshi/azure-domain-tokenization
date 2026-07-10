# Response to review

Consolidated responses to the Phase F independent reviews (plan-2.md §20–21).
Reviews: `STATISTICAL_REVIEW.md`, `METHOD_REVIEW.md`, `CLAIM_REVIEW.md`.

## Statistical review — PASS (no changes required)

The reviewer independently recomputed every headline statistic from the raw
per-document rows (`results/raw/eval_rows.parquet`), including a from-scratch
paired bootstrap. All matched within tolerance: primary reduction 36.6773%
(General 379.30, Azure 240.18 tokens/1k bytes), independent 95% CI
[35.7679%, 37.6182%], win rate 1.000; transfer, vocabulary, content-type,
coverage, round-trip/UNK, and runtime all matched. No action needed.

## Methodological red team — PASS WITH RECOMMENDATIONS (no blockers)

6 PASS / 4 CONCERN / 0 FAIL. The concerns are non-blocking and already disclosed:

- **Azure-vs-general confound** — already the headline limitation (§Limitations,
  the "What this study is and is not" box, and the Introduction); the transfer and
  prose-only analyses are presented as narrowing, not eliminating, it.
- **Missing matched general-technical baseline** — already the priority item in
  Future Work.
- **Dedup sensitivity** — the near-duplicate threshold is declared; leakage
  controls verified (`audit_summary.json` `leakage_violations` empty).
- **Multiplicity of secondary comparisons** — **addressed**: the Methodology
  statistics paragraph now states that the primary hypothesis is the single
  confirmatory comparison and the transfer/vocab/content-type/repository
  breakdowns are secondary, exploratory, and not corrected for multiple
  comparisons (read descriptively).

## Claim / writing red team — FAIL → addressed (2 blockers + 1 nit fixed)

1. **Citation mismatch** (`02_related_work.tex`): the sentence implied BioBERT
   trains a biomedical tokenizer, but BioBERT reuses the general BERT tokenizer.
   **Fixed**: reworded to "Prior work builds domain-specific vocabularies or
   tokenizers for scientific, legal, legal/financial, and code corpora … Notably,
   some domain-adapted models instead reuse a general-domain tokenizer
   \citep{lee2019biobert}, which is precisely the vocabulary-mismatch setting this
   line of work motivates." The BioBERT citation now supports an accurate claim.

2. **Numeric registry overclaim** (`main.tex`, `appendix/verification.tex`): the
   text said "every number" is registered, but experimental constants (batch
   sizes, service counts, etc.) are not registry claims. **Fixed**: reworded to
   "Every empirical result value … (effect sizes, confidence intervals, coverage
   counts, and runtime summaries) is registered … ; experimental constants (seed,
   budgets, batch sizes, vocabulary sizes) are recorded in the repository configs."

3. **Unbounded language** (`07_analysis.tex`, non-blocking): "substantially less" /
   "much larger fraction" **replaced** with bounded wording ("fewer tokens … for
   example, roughly half as many tokens per resource-provider identifier in the
   repository's fragmentation table … a larger fraction of its vocabulary").

After the edits: paper recompiles cleanly (0 undefined citations/references),
`scripts/paper_check.py` = 6/6, `make verify-claims` = 44/44, and a forbidden-claim
scan of the sections is clean.
