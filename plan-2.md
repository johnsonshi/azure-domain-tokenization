# Publication and arXiv Preparation Plan

## 0. Purpose

This plan directs a coding agent to convert the completed tokenizer experiment into two finished artifacts:

1. A clean, readable, reproducible public repository that presents the experiment as a research artifact.
2. A complete arXiv-ready paper package grounded only in verified repository evidence.

Execute the work. Do not merely review the repository, suggest improvements, or produce another plan.

Use sub-agents aggressively for independent research, repository auditing, documentation, statistical verification, citation checking, paper review, and LaTeX validation. Keep final authority with one orchestrator that owns the claim ledger, source of truth, and release gates.

The existing experiment is complete. Do not rerun or alter the scientific experiment unless a publication-blocking defect is discovered. Preserve the verified results and provenance.

---

## 1. Non-Negotiable Scientific Record

Treat the referenced machine-readable files as authoritative. Do not copy numbers from this section into final outputs without reconciling them programmatically against those files.

### Experiment profile

- Profile: `full`
- Training corpora: 32 MiB byte-matched General, Azure, and 50/50 Mixed
- Controlled matrix: General/Azure/Mixed × 8K/16K/32K byte-level BPE
- Primary slice: 16K
- Principal evaluation set: `azure_cross_service_holdout`
- Principal holdout size: 964 documents across five held-out Azure services
- Seed: `20260709`
- Leakage controls:
  - 134 exact duplicates removed from General before splitting
  - 9 cross-corpus near-duplicate evaluation items removed
- Automated verification gate: 8/8
- Independent review record: `research/PILOT_REVIEW.md`
- Source lock: `data/manifests/sources.lock.json`

### Verified primary result

On `azure_cross_service_holdout`, the Azure-trained 16K tokenizer uses 36.68% fewer tokens per 1,000 UTF-8 bytes than the byte-matched General tokenizer:

- Azure: 240.18 tokens per 1,000 UTF-8 bytes
- General: 379.30 tokens per 1,000 UTF-8 bytes
- Relative reduction: 36.68%
- 95% paired-bootstrap CI: [35.77%, 37.62%]
- Document win rate: 1.000

Authoritative files:

- `results/processed/eval_aggregate.csv`
- `results/processed/bootstrap.json`
- `results/tables/reduction_azure_vs_general_16384.csv`

### Verified general-English regression

On held-out general English, the Azure tokenizer is 34.75% less token-efficient than the General tokenizer:

- Relative result: -34.75%
- 95% CI: [-35.10%, -34.40%]

Authoritative file:

- `results/processed/bootstrap.json`
- Key: `by_eval_set.general_english`

### Verified mixed-tokenizer result

Relative to the General tokenizer:

- Mixed tokenizer on Azure principal holdout: +34.21%
- Azure tokenizer on Azure principal holdout: +36.68%
- Mixed tokenizer on general English: -4.39%
- Azure tokenizer on general English: -34.75%

This supports the claim that the 50/50 Mixed tokenizer retains most of the measured in-domain compression gain while sharply reducing the measured general-English penalty, within this experiment and corpus budget.

Authoritative file:

- `results/processed/eval_aggregate.csv`

### Verified transfer results

Azure versus General at 16K:

| Evaluation set | Relative token reduction |
|---|---:|
| Azure same-service holdout | +35.03% |
| Microsoft data documentation | +32.94% |
| Microsoft DevOps documentation | +31.76% |
| External technical documentation, Kubernetes | +31.18% |
| Microsoft architecture documentation | +26.03% |
| Microsoft broad-enterprise documentation | +25.89% |

All listed confidence intervals exclude zero.

Authoritative file:

- `results/processed/bootstrap.json`
- Key: `by_eval_set`

### Verified vocabulary-size result

Azure versus General on the principal holdout:

| Vocabulary size | Relative token reduction |
|---|---:|
| 8K | +36.46% |
| 16K | +36.68% |
| 32K | +35.41% |

Authoritative file:

- `results/tables/fig_relative_reduction_by_vocab.csv`

### Verified content-type result

On the principal holdout:

| Content type | Documents or units | Relative token reduction |
|---|---:|---:|
| Prose-dominant documents | 900 | +36.75% |
| Headings | As recorded in results | +37.49% |
| Tables | As recorded in results | +44.30% |
| Inline code | As recorded in results | +33.28% |

Prose 95% CI: [35.87%, 37.63%].

Authoritative file:

- `results/processed/bootstrap.json`
- Key: `by_content_type`

### Verified coverage result

Across 12 encoders × 9 evaluation sets:

- 59,160 evaluation rows
- 100% exact encode-to-decode reconstruction
- Zero `[UNK]` occurrences

Authoritative files:

- `results/raw/eval_rows.parquet`
- `results/reports/VERIFICATION.md`

### Verified runtime result

- Controlled Track A tokenizers: approximately 5.1 to 5.5 MB/s
- Track B `tiktoken` baselines: approximately 11 to 19 MB/s

This is CPU tokenizer throughput on the tested laptop, not model inference throughput. Small runtime differences are not to be overinterpreted because the machine is thermally variable.

Authoritative file:

- `results/tables/runtime_throughput.csv`

---

## 2. Claims the Repository and Paper May Make

Subject to exact reconciliation with result files, the final artifacts may state:

1. Under a fixed 32 MiB training budget, fixed byte-level BPE implementation, and matched 16K vocabulary size, Azure-documentation training reduced token count on an unseen cross-service Azure holdout by 36.68% relative to general-English training.
2. The measured reduction persisted across 8K, 16K, and 32K controlled vocabulary sizes.
3. The measured reduction persisted on prose-dominant content and was not solely explained by code fences or configuration syntax.
4. The Azure-trained tokenizer transferred partially to other Microsoft and external technical-documentation corpora.
5. Full specialization imposed a large general-English compression penalty.
6. A 50/50 Mixed tokenizer retained most of the Azure-domain compression gain with a much smaller general-English penalty.
7. Compression efficiency and CPU tokenizer throughput were distinct dimensions in this experiment.
8. Byte-level BPE provided exact round-trip coverage with zero unknown tokens across the evaluated data.

Use bounded language:

- “uses fewer tokens”
- “reduces token count”
- “compression efficiency”
- “on the evaluated corpus”
- “under the controlled setup”
- “measured CPU tokenizer throughput”
- “derived context-capacity estimate”

---

## 3. Claims the Repository and Paper Must Not Make

Do not claim or imply that:

- The tokenizer improves LLM quality, accuracy, reasoning, semantics, safety, or factuality.
- The tokenizer can be substituted into an already-trained model without model adaptation.
- A 36.68% token reduction produces a 36.68% inference-latency reduction.
- A 36.68% token reduction produces a 36.68% total-cost reduction.
- Token boundaries are more linguistically correct.
- The Azure tokenizer “understands Azure.”
- The result establishes universal superiority of domain-specific tokenizers.
- The result applies to chat, source-code repositories, all enterprise text, or all technical domains.
- The result is an official Microsoft result or represents Microsoft’s position.
- CPU tokenization throughput is model-serving throughput.
- Existing production tokenizers form a controlled causal comparison.
- A token-count estimate is a measured GPU or billing outcome.
- Microsoft Learn content may be redistributed beyond its applicable license terms.

The final paper must include a visible “What this study is and is not” subsection.

---

## 4. Operating Rules for the Agent

### 4.1 Preserve the experiment

Before modifying files:

1. Confirm the repository is under Git.
2. Record the current branch and commit.
3. Require a clean worktree or commit the current verified state.
4. Create a publication-preparation branch.
5. Tag or otherwise identify the verified experiment snapshot.
6. Never rewrite raw results in place.
7. Never silently regenerate results with changed dependencies or configuration.
8. Never delete source manifests, verification records, or audit artifacts.

Suggested branch:

```bash
git switch -c publication/arxiv-prep
```

Suggested snapshot tag, only if the user has not established a naming scheme:

```bash
git tag experiment-full-verified-20260709
```

Do not push, publish, create a release, or submit to arXiv without explicit user approval.

### 4.2 Use evidence, not memory

Build a programmatic claim registry:

- `publication/claims.yaml`
- `publication/claim_evidence.csv`

Each claim must include:

- Stable claim ID
- Human-readable text
- Claim type: primary, secondary, descriptive, limitation, or derived
- Exact source file
- Source column or JSON key
- Extraction command
- Expected value
- Tolerance
- Figure or table using it
- Paper section using it
- Verification status
- Reviewer

No numerical statement may appear in the README, result summary, abstract, paper, caption, social copy, or release notes unless it is in this registry and passes verification.

### 4.3 Sub-agent discipline

Use separate sub-agents for:

- Repository information architecture
- Reproducibility audit
- Data and licensing audit
- Result reconciliation
- Figure and table design
- Literature search
- Citation verification
- Scientific writing
- Methods review
- Statistical review
- Red-team review
- LaTeX and arXiv packaging
- Accessibility and readability review

A sub-agent that authors a section must not be its only reviewer.

Agents may propose changes. The orchestrator must accept only changes consistent with the evidence and scope.

### 4.4 Context management

Maintain:

- `publication/STATE.md`
- `publication/DECISIONS.md`
- `publication/CLAIM_LEDGER.md`
- `publication/OPEN_ISSUES.md`
- `publication/REVIEW_LOG.md`
- `publication/work_queue.jsonl`

Keep `STATE.md` concise enough that a new coding agent can resume without reading the full conversation.

Store detailed research and review output in files, not agent chat messages.

---

# PART I: MAKE THE REPOSITORY SHAREABLE

## 5. Repository Audit

Create `publication/audits/REPOSITORY_AUDIT.md`.

Inspect:

- Root-level clutter
- Naming consistency
- Dead scripts
- Duplicate documentation
- Notebook outputs
- Large files
- Untracked generated files
- Stale intermediate artifacts
- Hard-coded local paths
- Secrets or credentials
- Usernames and machine-specific paths
- Private URLs
- Internal-only terminology
- Data-license risks
- Broken relative links
- Missing provenance
- Results with no source table
- Figures with no generation path
- Commands that no longer work
- Environment assumptions
- Package lock consistency
- Git history containing accidental corpora or secrets
- Case-sensitive path problems
- README accuracy
- Accessibility of charts
- Reproduction cost and runtime disclosure

Run secret scanning with an available local tool. Do not upload repository contents to a third-party scanner.

Generate:

- `publication/audits/LARGE_FILES.md`
- `publication/audits/SECRET_SCAN.md`
- `publication/audits/LINK_CHECK.md`
- `publication/audits/REPRODUCIBILITY_AUDIT.md`
- `publication/audits/LICENSE_AUDIT.md`

Publication-blocking findings must be resolved or explicitly documented.

---

## 6. Target Repository Information Architecture

Prefer this public-facing shape unless the existing repository has a better established structure:

```text
.
├── README.md
├── LICENSE
├── CITATION.cff
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
├── plan.md
├── plan-2.md
├── pyproject.toml
├── uv.lock
├── Makefile
├── configs/
├── data/
│   ├── README.md
│   ├── manifests/
│   └── audit/
├── docs/
│   ├── experiment-design.md
│   ├── methodology.md
│   ├── datasets-and-licenses.md
│   ├── reproducibility.md
│   ├── results.md
│   ├── limitations.md
│   ├── repository-map.md
│   └── artifact-evaluation.md
├── notebooks/
│   ├── README.md
│   └── ...
├── paper/
│   ├── README.md
│   ├── main.tex
│   ├── references.bib
│   ├── sections/
│   ├── figures/
│   ├── tables/
│   ├── appendix/
│   └── arxiv/
├── research/
├── results/
│   ├── README.md
│   ├── raw/
│   ├── processed/
│   ├── tables/
│   ├── figures/
│   └── reports/
├── scripts/
├── src/
├── tests/
└── publication/
```

Do not reorganize merely for appearance. Preserve paths used by reproducibility commands or update them atomically with tests.

If the original experiment plan is overwritten by this publication plan, recover it from Git and store it as:

- `docs/experiment-plan.md`

Preserve its history.

---

## 7. Root README Requirements

Rewrite `README.md` for a technical reader encountering the project for the first time.

Required structure:

1. Project title
2. One-paragraph description
3. Scope statement
4. Primary result
5. Mixed-tokenizer tradeoff
6. Compact results table
7. One main figure
8. “What this measures”
9. “What this does not measure”
10. Experimental design diagram
11. Repository map
12. Quick reproduction
13. Full reproduction
14. Data acquisition and licensing
15. Result verification
16. Paper
17. Citation
18. Limitations
19. License and attribution
20. Author and affiliation disclaimer

The README must state:

- The primary comparison is controlled.
- Track B production tokenizers are observational baselines.
- The corpora were byte-matched.
- The primary result uses the 16K slice.
- The principal holdout is cross-service.
- The project measures tokenizer behavior only.
- Raw licensed source corpora are not necessarily included.
- Reproduction may require downloading pinned public sources.
- Exact commands and expected resource usage.

Use one primary figure above the fold. Avoid flooding the README with every chart.

---

## 8. Required Documentation Files

### `docs/experiment-design.md`

Include:

- Research question
- Hypotheses
- Controlled variables
- Independent variable
- Dependent variables
- Training-corpus construction
- Evaluation sets
- Primary endpoint
- Secondary endpoints
- Statistical method
- Leakage controls
- Frozen decisions
- Deviations
- Track A versus Track B distinction

### `docs/methodology.md`

Include enough detail to reproduce:

- Source selection
- Commit pinning
- License review
- Markdown extraction
- Normalization
- Segmentation
- Exact deduplication
- Near-duplicate filtering
- Train/evaluation split
- Corpus byte matching
- Byte-level BPE configuration
- Vocabulary sizes
- Seed
- Training commands
- Evaluation commands
- Bootstrap procedure
- Runtime procedure
- Machine metadata
- Verification gate

### `docs/datasets-and-licenses.md`

For every source:

- Name
- Repository or dataset URL
- Pinned commit or revision
- Role: training or evaluation
- Selection method
- Cleaned byte count
- Document count
- License
- Attribution
- Redistribution status
- Acquisition command
- Exclusions
- Known limitations

Do not reproduce substantial licensed text. Use manifests, checksums, and acquisition scripts.

### `docs/reproducibility.md`

Provide:

- Supported environment
- Exact installation
- Pilot reproduction
- Full reproduction
- Analysis-only reproduction
- Paper-only reproduction
- Expected time
- Expected disk
- Expected memory
- Determinism notes
- Known nondeterminism
- How to verify the published numbers
- How to resume interrupted stages
- Expected output checksums when stable

### `docs/results.md`

Present:

- Primary result
- General-English regression
- Mixed tradeoff
- Transfer
- Vocabulary sensitivity
- Content-type analysis
- Coverage
- Runtime
- Negative or null results
- Caveats

Every number must be generated from the claim registry.

### `docs/limitations.md`

At minimum discuss:

- 32 MiB training budget
- One tokenizer algorithm for the controlled matrix
- Documentation-specific source distributions
- Azure versus general-English corpus mismatch beyond subject matter
- Possible effects of authoring style, markup, identifiers, and repeated terminology
- Limited evidence about causality within subcomponents
- No language-model training
- No downstream quality evaluation
- No GPU or serving benchmark
- Laptop runtime variability
- Public-repository snapshot dependence
- License-constrained redistribution
- No claim of universal domain transfer
- Existing tokenizers not controlled
- Potential author-employer relationship and non-endorsement

### `docs/artifact-evaluation.md`

Provide a reviewer-oriented checklist:

- What can be reproduced without downloading corpora
- What requires downloading corpora
- Expected commands
- Expected results
- Approximate runtime
- Approximate storage
- How to inspect raw rows
- How to regenerate tables and figures
- How to run verification

---

## 9. Results Organization

Create `results/README.md` explaining:

- Which files are authoritative
- Which are raw, processed, tables, figures, and reports
- How each layer is regenerated
- Which files should be version-controlled
- Schema definitions
- Units
- Sign conventions
- Micro versus macro aggregation
- Confidence-interval method
- Stable identifiers for evaluation sets and tokenizers

Add:

- `results/DATA_DICTIONARY.md`
- Schema checks for CSV, JSON, and Parquet outputs

Remove or relocate stale exploratory results only after proving they are not referenced. Preserve them under an explicitly labeled archive when uncertain.

---

## 10. Figures and Tables for Public Presentation

Create publication-quality figures from committed source tables. Never edit data labels manually in an image editor.

Required figures:

1. Primary Azure cross-service reduction with 95% CI
2. Azure gain versus general-English regression for General, Azure, and Mixed tokenizers
3. Transfer across evaluation sets
4. Vocabulary-size sensitivity
5. Content-type breakdown
6. Compression versus CPU throughput
7. Optional experiment-design diagram
8. Optional vocabulary-utilization or fragmentation figure if supported by verified results

Required tables:

1. Experimental matrix
2. Dataset and evaluation-set summary
3. Primary and mixed-tokenizer results
4. Transfer results
5. Vocabulary-size results
6. Runtime results
7. Coverage and verification results
8. Limitations or scope matrix

Figure requirements:

- Source table committed
- Script or Make target committed
- Units in axis labels
- CI method in caption
- Colorblind-safe palette
- Legible in grayscale where practical
- No 3D plots
- No misleading truncated axis without explicit reason
- No dual axis unless unavoidable
- Accessible alt text
- Consistent terminology
- PDF vector output for paper
- PNG output for README
- Deterministic filenames

---

## 11. Notebook Cleanup

Notebooks are explanatory artifacts, not the only execution path.

For every notebook:

- Add title, purpose, inputs, outputs, and expected runtime.
- Remove stale outputs and debugging cells.
- Remove absolute paths.
- Remove secrets and machine identifiers.
- Ensure cells execute top to bottom.
- Move reusable logic into `src/`.
- Make notebook execution optional for core reproduction.
- Pin randomness.
- Avoid hidden state.
- Add links to authoritative result files.
- Mark exploratory analysis as exploratory.
- Add a notebook README with execution order.

Run an automated notebook execution check on lightweight or analysis-only notebooks.

Do not rerun expensive training merely to clean notebooks.

---

## 12. Reproducibility Interface

Provide stable commands:

```bash
make setup
make doctor
make verify
make analyze
make figures
make report
make paper
make paper-check
make arxiv-package
```

Where practical:

- `make verify` checks the existing full artifacts without retraining.
- `make analyze` regenerates processed results from raw results.
- `make figures` regenerates public and paper figures.
- `make report` regenerates Markdown result summaries.
- `make paper` compiles the manuscript.
- `make paper-check` runs citation, reference, link, claim, and LaTeX checks.
- `make arxiv-package` creates a clean source archive but does not submit it.

Provide `scripts/verify_claims.py` that checks every registered numeric claim.

The release gate must fail when:

- A claim differs from its source.
- A figure source table is stale.
- A table contains an unregistered number.
- A citation key is unresolved.
- A required license record is missing.
- A LaTeX build fails.
- A repository link is broken.
- A raw corpus is accidentally staged.

---

## 13. Repository Metadata and Community Files

Create or validate:

- `LICENSE` for original repository code and writing
- `CITATION.cff`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `.gitignore`
- `.gitattributes`

Do not choose an open-source license for third-party corpus content. Clearly separate:

- Original code license
- Original paper and documentation license
- Third-party documentation licenses
- Generated tokenizer artifact redistribution status
- Raw corpus redistribution status

Do not invent the author’s legal name, ORCID, affiliation, email, employer approval, or coauthors. Use explicit placeholders and create `publication/AUTHOR_INPUTS_REQUIRED.md`.

If the author is employed by Microsoft:

- State the relationship accurately if included.
- Do not claim Microsoft sponsorship or endorsement without evidence.
- Prompt the author to check applicable employer publication-review requirements.
- Keep this as a human approval gate.

---

## 14. Public-Artifact Quality Gate

Before beginning the paper, require all of the following:

- Root README is understandable without prior context.
- Primary result reconciles programmatically.
- Mixed-tokenizer result reconciles programmatically.
- All public figures regenerate.
- All public tables regenerate.
- No secret scan blockers.
- No raw corpora accidentally tracked.
- License and attribution records complete.
- Relative links pass.
- Analysis-only reproduction passes.
- `make verify` passes.
- Result terminology is consistent.
- Limitations are visible.
- Repository snapshot is tagged or otherwise recorded.
- Independent artifact reviewer signs `publication/reviews/ARTIFACT_REVIEW.md`.

Only then start the manuscript phase.

---

# PART II: WRITE THE arXiv PAPER

## 15. Paper Objective

Write a refereeable empirical paper about controlled tokenizer compression on technical documentation.

The paper’s central contribution should be framed as:

> A controlled case study measuring how training-corpus specialization changes byte-level BPE compression across unseen Azure, Microsoft, external technical, and general-English documentation, including the tradeoff between full specialization and mixed-domain training.

Do not frame the contribution as inventing domain-specific tokenization.

Potential titles to evaluate:

1. **Does Your Tokenizer Speak Cloud? Measuring Domain Specialization on Technical Documentation**
2. **The Token Cost of Technical Vocabulary: A Controlled Study on Azure Documentation**
3. **Domain-Specialized Tokenization for Cloud Documentation: Compression Gains and General-Domain Tradeoffs**
4. **Training Corpus Matters: Byte-Level BPE Efficiency on Cloud and Technical Documentation**
5. **Specialize or Mix? Tokenizer Compression Tradeoffs on Azure and General English**

The literature and writing agents should recommend one title based on precision, discoverability, and avoidance of marketing language.

---

## 16. Literature Research

Create:

- `paper/literature/literature_review.md`
- `paper/literature/paper_matrix.csv`
- `paper/literature/related_work_outline.md`
- `paper/literature/citation_verification.csv`
- `paper/literature/search_log.md`

Use primary sources. Prefer papers and official implementation documentation.

Start with these candidate references, verify their current versions, metadata, claims, and relevance before citing:

1. **Efficient Domain Adaptation of Language Models via Adaptive Tokenization**  
   arXiv:2109.07460  
   https://arxiv.org/abs/2109.07460

2. **Adaptive BPE Tokenization for Enhanced Vocabulary Adaptation in Finetuning Pretrained Language Models**  
   arXiv:2410.03258  
   https://arxiv.org/abs/2410.03258

3. **How Much is Enough? The Diminishing Returns of Tokenization Training Data**  
   arXiv:2502.20273  
   https://arxiv.org/abs/2502.20273

4. **KL3M Tokenizers: A Family of Domain-Specific and Character-Level Tokenizers for Legal, Financial, and Preprocessing Applications**  
   arXiv:2503.17247  
   https://arxiv.org/abs/2503.17247

5. **Vocabulary Customization for Efficient Domain-Specific LLM Deployment**  
   arXiv:2509.26124  
   https://arxiv.org/abs/2509.26124

6. **AdaptBPE: From General Purpose to Specialized Tokenizers**  
   arXiv:2601.21665  
   https://arxiv.org/abs/2601.21665

7. **Learning Faster with Better Tokens: Parameter-Efficient Vocabulary Adaptation for Specialized Text Summarization**  
   arXiv:2605.17379  
   https://arxiv.org/abs/2605.17379

8. **Beyond Fertility: Analyzing STRR as a Metric for Multilingual Tokenization Evaluation**  
   arXiv:2510.09947  
   https://arxiv.org/abs/2510.09947

9. **Equity with Efficiency: An Empirical Study of Tokenizers for Multilingual Large Language Models**  
   arXiv:2606.15044  
   https://arxiv.org/abs/2606.15044

10. Original or foundational sources for:
    - Byte Pair Encoding in neural machine translation
    - WordPiece where relevant
    - SentencePiece where relevant
    - Byte-level BPE and GPT-2 tokenization
    - Hugging Face `tokenizers`
    - OpenAI `tiktoken`

Search for additional work on:

- Tokenizer fertility
- Compression metrics
- Vocabulary allocation
- Domain adaptation
- Technical or code tokenization
- Legal, biomedical, financial, scientific, and multilingual tokenizers
- Training-corpus size
- Vocabulary-size scaling
- Tokenization fairness
- Tokenization and inference cost
- Vocabulary replacement or extension
- Documentation corpora
- Leakage and deduplication in tokenizer evaluation

For every candidate citation:

- Read at least the abstract and relevant methods/results sections.
- Record the exact claim supported.
- Record version and access date.
- Export accurate BibTeX from the primary source.
- Check author names and title.
- Avoid citing a paper for a claim it does not make.
- Do not fabricate DOI, venue, page count, or code availability.
- Distinguish peer-reviewed publications from preprints.
- Prefer the published version when available and equivalent.
- Keep direct quotations minimal.
- Run a final citation audit.

The related-work section must explicitly distinguish:

- Training a tokenizer from scratch on domain data
- Extending or replacing vocabulary in an existing model
- Changing pre-tokenization
- Multilingual equity work
- Measuring fertility or compression
- Measuring downstream model performance

This study belongs primarily to the first and fifth categories.

---

## 17. Paper Package Structure

Create:

```text
paper/
├── README.md
├── main.tex
├── references.bib
├── latexmkrc
├── Makefile
├── sections/
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_research_questions.tex
│   ├── 04_data.tex
│   ├── 05_methodology.tex
│   ├── 06_results.tex
│   ├── 07_analysis.tex
│   ├── 08_limitations.tex
│   ├── 09_ethics_and_licenses.tex
│   ├── 10_future_work.tex
│   └── 11_conclusion.tex
├── figures/
├── tables/
├── appendix/
│   ├── experiment_matrix.tex
│   ├── dataset_details.tex
│   ├── additional_results.tex
│   ├── runtime_details.tex
│   ├── verification.tex
│   └── reproducibility.tex
├── metadata/
│   ├── title.txt
│   ├── abstract.txt
│   ├── authors.example.yaml
│   └── categories.md
└── arxiv/
    ├── MANIFEST.md
    ├── submission-checklist.md
    └── build/
```

Use an arXiv-compatible LaTeX setup. Prefer a simple, portable article class unless a target venue template has been explicitly selected.

---

## 18. Required Paper Sections

### Abstract

The abstract must include:

1. The problem: general-purpose tokenizers may allocate vocabulary inefficiently for specialized technical documentation.
2. The controlled setup: byte-level BPE, byte-matched 32 MiB corpora, General/Azure/Mixed, 8K/16K/32K.
3. The primary result: 36.68% fewer tokens on the cross-service Azure holdout for Azure versus General at 16K, with CI.
4. The tradeoff: 34.75% general-English regression for Azure.
5. The practical finding: Mixed retains 34.21% Azure reduction with only 4.39% general-English regression.
6. Transfer: measured improvements on other technical-documentation sets.
7. Scope: tokenizer compression only, with no model-quality or serving claim.
8. Release: code, manifests, and reproducible result artifacts, subject to actual repository contents.

Do not include unsupported claims about inference speed or cost.

### Introduction

Explain:

- Why tokenizer vocabulary allocation affects sequence length.
- Why technical documentation is a useful domain.
- Why Azure documentation is a useful controlled case.
- Why in-domain gain must be reported with out-of-domain regression.
- Why a mixed tokenizer is practically relevant.
- Why existing production-tokenizer comparisons alone cannot isolate training-corpus effects.
- The gap addressed by this controlled study.
- The contributions as a concise numbered list.

Potential contribution list:

1. A controlled corpus-composition study with matched byte budgets and tokenizer configurations.
2. Cross-service and cross-repository held-out evaluation with leakage controls.
3. Analysis of the specialization versus generality tradeoff through a 50/50 mixed tokenizer.
4. Content-type, vocabulary-size, coverage, transfer, and CPU-runtime analysis.
5. A reproducible artifact with source locks, raw per-document results, and claim verification.

### Related Work

Cover:

- Subword tokenization
- Domain-specific tokenizers
- Vocabulary adaptation
- Tokenizer fertility and compression metrics
- Training data and vocabulary size
- Technical/code-domain tokenization
- Downstream adaptation studies

Do not turn related work into a list of abstracts. Organize it around methodological differences and the gap this paper fills.

### Research Questions and Hypotheses

State explicit questions:

- RQ1: Does Azure-domain training reduce token count on unseen Azure services relative to general-English training under matched conditions?
- RQ2: What general-English regression accompanies full specialization?
- RQ3: Does a 50/50 mixed corpus preserve most in-domain gain while limiting regression?
- RQ4: Does specialization transfer to other technical-documentation domains?
- RQ5: Is the effect stable across 8K, 16K, and 32K vocabularies?
- RQ6: Does the effect persist in prose, rather than being explained only by code and markup?
- RQ7: How do compression and CPU tokenizer throughput relate?

State the null and alternative hypotheses as defined by the original experiment record.

### Data

Describe:

- Public source repositories
- Source pins
- License handling
- Training corpora
- Evaluation corpora
- Service-level holdouts
- General-English corpus
- Kubernetes external control
- Microsoft transfer sets
- Document counts
- Byte budgets
- Content classification
- Exclusions
- Exact and near-duplicate filtering

Include a corpus table generated from manifests.

Do not reproduce source-document text beyond minimal examples and applicable license terms.

### Methodology

Describe precisely:

- Byte-level BPE implementation
- Fixed configuration
- Vocabulary sizes
- Special tokens
- Unicode normalization
- Corpus sampling
- Byte matching
- Mixed-corpus construction
- Training procedure
- Track A controlled tokenizers
- Track B observational baselines
- Primary metric: tokens per 1,000 UTF-8 bytes
- Relative token reduction
- Micro and macro aggregation
- Paired bootstrap
- Win rate
- Content-type analysis
- Round-trip and unknown-token checks
- Runtime benchmark
- Hardware and software
- Verification pipeline

Include formulas for:

```text
tokens_per_1000_bytes(T, D)
  = 1000 × total_tokens(T, D) / total_utf8_bytes(D)
```

and:

```text
relative_reduction(A vs G, D)
  = 100 × [tokens(G, D) - tokens(A, D)] / tokens(G, D)
```

Define the sign convention clearly.

### Results

Lead with the primary result, then report:

1. Primary Azure cross-service result
2. General-English regression
3. Mixed-tokenizer tradeoff
4. Transfer
5. Vocabulary-size stability
6. Content-type analysis
7. Round-trip and unknown-token coverage
8. CPU runtime

Use exact CIs and denominators.

Do not mix methods, speculation, and results in the same paragraph.

### Analysis and Discussion

Discuss:

- Why the result is consistent with vocabulary allocation to domain terms and documentation patterns.
- Why the prose result weakens the claim that gains are only from code fences.
- Why transfer to Kubernetes suggests broader technical-documentation overlap.
- Why Azure versus general English does not fully isolate Azure-specific terms from technical-documentation style.
- Why the Mixed tokenizer is the central tradeoff result.
- Why the stable 8K/16K/32K reduction suggests corpus composition mattered more than the tested vocabulary range.
- Why faster compression does not imply faster CPU tokenization.
- Why no downstream model claims are possible.

Mark causal interpretation limits explicitly.

### What This Study Is and Is Not

Include a dedicated subsection or boxed table.

#### This study is

- A tokenizer-training and compression benchmark
- A controlled comparison of corpus composition
- A held-out technical-documentation evaluation
- A study of domain/general tradeoffs
- A CPU-only reproducible artifact

#### This study is not

- An LLM quality evaluation
- A model adaptation method
- A serving benchmark
- A GPU benchmark
- A billing study
- An endorsement of replacing production tokenizers
- A claim that fewer tokens always means a better system

### Limitations

Use the repository limitation document as the basis. Do not minimize limitations.

The most important unresolved design limitation to state:

> Comparing Azure documentation with general English changes more than subject domain. It also changes technical style, markup distribution, identifier density, and document structure. Transfer and prose-only analyses narrow this concern but do not fully isolate Azure-specific vocabulary from general technical-documentation specialization.

Recommend a future general-technical training control.

### Ethics, Licensing, and Broader Impact

Discuss:

- Public documentation sources
- Licenses and attribution
- No user data
- No private Microsoft content
- Redistribution boundaries
- Reproducibility without republishing restricted corpora
- Potential token-based cost inequities across domains
- Risk of overclaiming compression as model quality
- Employment and non-endorsement disclosure, if applicable
- Environmental scope: CPU-only experiment, with no model training

Do not invent an IRB statement.

### Future Work

Prioritize:

1. Train a matched general-technical-documentation tokenizer to separate technical style from Azure specialization.
2. Test more corpus mixture ratios.
3. Test more training-data sizes.
4. Evaluate other tokenizer algorithms under matched controls.
5. Measure vocabulary utilization and token-category allocation more deeply.
6. Integrate an adapted tokenizer into a small model trained from scratch to measure downstream effects.
7. Test real prefill, KV-cache, latency, and throughput effects with a compatible model.
8. Evaluate code-heavy and multilingual technical documentation.
9. Perform temporal holdout evaluation.
10. Test vocabulary replacement or adaptation methods rather than full retraining.

Clearly label GPU/model work as future work.

### Conclusion

The conclusion must contain:

- Controlled primary result
- General-English penalty
- Mixed-tokenizer tradeoff
- Transfer result
- Narrow scope
- No model-quality claim

Do not repeat every number.

---

## 19. Tables and Figures in the Paper

### Main-paper figures

Target four to six:

1. Primary result with CI
2. Specialization-generalization tradeoff
3. Cross-domain transfer
4. Vocabulary-size sensitivity
5. Content-type breakdown
6. Compression versus CPU throughput, only if readable

### Main-paper tables

Target three to five:

1. Experimental design
2. Corpus/evaluation summary
3. Main results
4. Transfer and vocabulary ablation
5. Verification and runtime summary

Move full matrices and secondary breakdowns to the appendix.

Every caption must state:

- What is measured
- Unit
- Comparison direction
- Aggregation
- CI method where relevant
- Whether higher or lower is better

---

## 20. Statistical and Result Review

The statistics sub-agent must independently:

- Recompute the primary result from raw rows.
- Recompute the bootstrap interval.
- Verify the win rate.
- Verify mixed and general-English results.
- Verify all transfer values.
- Verify vocabulary-size values.
- Verify content-type values.
- Verify row counts and round-trip rate.
- Verify runtime summaries.
- Check micro versus macro terminology.
- Check sign conventions.
- Check that CIs are paired at the document level.
- Check that no excluded near-duplicate rows entered final results.

Record in:

- `publication/reviews/STATISTICAL_REVIEW.md`

The paper must not progress to final release until this review passes.

---

## 21. Scientific Red Team

Create at least two independent reviews.

### Reviewer A: Methodological red team

Check:

- Leakage
- Corpus mismatch
- Byte matching
- Split construction
- Deduplication
- Generalization claims
- Control adequacy
- Track A/Track B separation
- Missing baselines
- Statistical assumptions
- Reproducibility

### Reviewer B: Claim and writing red team

Check:

- Unsupported causal language
- Model-quality implication
- Cost or latency implication
- Microsoft-endorsement implication
- Abstract overclaiming
- Citation mismatch
- Missing counterevidence
- Inconsistent numbers
- Selective reporting
- Limitations visibility

Outputs:

- `publication/reviews/METHOD_REVIEW.md`
- `publication/reviews/CLAIM_REVIEW.md`
- `publication/reviews/RESPONSE_TO_REVIEW.md`

Resolve blockers or mark them explicitly for the user.

---

## 22. arXiv-Specific Preparation

Research the current official arXiv instructions before packaging. Start from:

- https://info.arxiv.org/help/submit/index.html
- https://info.arxiv.org/help/submit_tex.html

At the time this plan was written, arXiv stated that TeX/LaTeX is its preferred portable format, requires submitted figures to be included rather than externally linked, restricts filename characters, treats filenames as case-sensitive, and expects bibliography support files such as `.bib` or `.bbl` as applicable. Reverify current requirements before final packaging.

The agent must:

- Use portable LaTeX.
- Avoid proprietary fonts.
- Avoid local absolute paths.
- Include all figures.
- Include required style and bibliography files.
- Match filename case exactly.
- Use filename characters accepted by arXiv.
- Remove build caches and unrelated files.
- Build in a clean temporary directory.
- Test with an arXiv-compatible TeX environment if available.
- Include `.bbl` when needed.
- Confirm references resolve.
- Confirm hyperlinks work.
- Confirm no figures are omitted.
- Confirm PDF fonts are embedded and readable.
- Confirm metadata title and abstract match the manuscript.
- Confirm author placeholders remain obvious until the user supplies details.
- Produce an upload archive and manifest.
- Do not submit automatically.

Create:

- `paper/arxiv/submission-checklist.md`
- `paper/arxiv/MANIFEST.md`
- `paper/arxiv/arxiv-source.tar.gz`
- `paper/arxiv/compiled-paper.pdf`
- `paper/arxiv/build-log.txt`

Do not include downloaded source corpora in the arXiv package.

---

## 23. Author and Submission Inputs Requiring Human Approval

Create `publication/AUTHOR_INPUTS_REQUIRED.md` with:

- Legal author name
- Preferred publication name
- Email
- ORCID
- Affiliation
- Whether Microsoft affiliation should be listed
- Required employer publication review
- Coauthors and contribution approval
- Acknowledgments
- Funding
- Conflicts of interest
- Primary arXiv category
- Cross-list categories
- Paper license
- Repository URL
- Release DOI, if any
- Final title
- Final abstract
- Whether generated tokenizers may be distributed
- Whether the user wants anonymous or named pre-review copies

Recommended category for investigation:

- Primary: `cs.CL`

Possible cross-lists to investigate, not assume:

- `cs.AI`
- `cs.LG`
- `cs.CE`

The agent may recommend categories but must not invent endorsement eligibility or submit.

---

## 24. Writing and Citation Quality Rules

- Use plain technical language.
- Define every metric before using it.
- Keep terminology stable.
- Avoid “dramatic,” “substantial,” “significant,” or “efficient” without a metric or statistical meaning.
- Use “statistically distinguishable from zero” rather than “significant” when that is what is meant.
- State sample sizes.
- Report uncertainty.
- Report regressions beside gains.
- Separate result from interpretation.
- Cite primary sources.
- Do not cite search snippets.
- Do not fabricate citations.
- Do not cite a paper without checking it.
- Do not paraphrase abstracts as related work without methodological synthesis.
- Do not reuse text from other papers.
- Run a text-overlap or plagiarism sanity check locally where possible.
- Keep quotations minimal.
- Make the paper understandable without the repository, while using the repository for full reproduction.

---

## 25. Build and Validation Commands

Implement stable commands such as:

```bash
make publication-audit
make publication-docs
make verify-claims
make figures
make paper
make paper-check
make arxiv-package
make publication-verify
```

`make publication-verify` should check:

- Existing experiment verify gate
- Claim registry
- Public Markdown links
- Documentation completeness
- Figure freshness
- Table freshness
- Citation resolution
- BibTeX validity
- LaTeX compilation
- arXiv filename compliance
- arXiv package manifest
- License records
- Absence of raw corpora from package
- Absence of secrets
- Required review sign-offs

Produce:

- `publication/FINAL_VERIFICATION.md`

---

## 26. Execution Phases

### Phase A: Preserve and audit

1. Snapshot verified state.
2. Create publication branch.
3. Build state and claim ledgers.
4. Audit repository, licenses, secrets, links, and reproducibility.
5. Resolve publication blockers.

Gate:

- Verified experiment untouched
- Audit complete
- No unresolved secret or license blocker

### Phase B: Repository information architecture

1. Reorganize conservatively.
2. Rewrite README.
3. Add public documentation.
4. Add result dictionary and repository map.
5. Clean notebooks.
6. Stabilize Make targets.
7. Add community and citation metadata.

Gate:

- New reader can locate methods, data, results, limitations, and reproduction
- All links pass
- `make verify` still passes

### Phase C: Public figures and claim verification

1. Create source tables.
2. Generate figures.
3. Register all public claims.
4. Verify every number.
5. Conduct artifact review.

Gate:

- Artifact reviewer signs off
- Every displayed number traces to evidence

### Phase D: Literature review

1. Search primary literature.
2. Build paper matrix.
3. Verify citations.
4. Define the paper’s contribution relative to prior work.
5. Freeze related-work outline.

Gate:

- No fabricated or unverified citations
- Contribution statement is narrow and supportable

### Phase E: Manuscript draft

Draft in this order:

1. Methods
2. Data
3. Results
4. Limitations
5. Analysis
6. Related work
7. Introduction
8. Future work
9. Conclusion
10. Abstract

This order reduces the risk of writing claims before evidence.

Gate:

- Complete paper compiles
- Every numeric claim passes registry verification

### Phase F: Independent review

1. Statistical review
2. Methodological red team
3. Claim and writing red team
4. Citation review
5. Reproducibility review
6. Resolve or disclose issues

Gate:

- No unresolved publication blocker

### Phase G: arXiv package

1. Verify current arXiv requirements.
2. Clean LaTeX source.
3. Build in clean environment.
4. Create source archive.
5. Create metadata files.
6. Produce submission checklist.
7. Stop before submission.

Gate:

- `make publication-verify` passes
- User approval still required for author metadata and submission

---

## 27. Stop Conditions

Stop and request user input only for:

- Author identity
- Affiliation
- Coauthor approval
- Employer publication approval
- Choice of paper license
- Final title preference when alternatives remain
- arXiv category or endorsement uncertainty
- A license issue that prevents publication
- A scientific defect that changes a verified conclusion
- A destructive repository-history rewrite
- Actual GitHub publication, release, DOI minting, or arXiv submission

Do not stop for:

- Routine documentation structure
- Figure layout
- Citation-manager choice
- LaTeX refactoring
- README wording
- Internal agent delegation
- Non-destructive cleanup

---

## 28. Final Deliverables

### Shareable repository

- Clean root README
- Organized docs
- Repository map
- Data and license documentation
- Reproducibility guide
- Results guide and data dictionary
- Limitations
- Citation metadata
- Community files
- Clean notebooks
- Stable Make targets
- Claim registry
- Publication-quality figures
- Verification report
- Artifact review

### Paper

- Complete LaTeX manuscript
- Verified BibTeX
- Main figures and tables
- Appendices
- Reproducibility statement
- Ethics and licensing statement
- “What this is and is not”
- Limitations
- Future work
- Compiled PDF
- Clean arXiv source package
- Submission checklist
- Human-input checklist

### Optional, after required work

- `docs/blog-post.md`
- `docs/linkedin-post.md`
- `docs/video-outline.md`
- GitHub release notes

Do not let optional communication artifacts delay the paper or repository gates.

---

## 29. Initial Prompt for the Coding Agent

```text
Read `plan-2.md` completely and treat it as the authoritative publication-preparation specification.

Execute it. Do not summarize it or replace it with another plan.

The scientific experiment is complete and verified. Preserve the verified snapshot and make the repository readable, reproducible, license-aware, and suitable for public review. Build a programmatic claim registry so every number in the README, documentation, figures, tables, and paper is reconciled against authoritative result files.

Use sub-agents aggressively for independent repository audit, reproducibility, licensing, result verification, literature research, citation checking, scientific writing, statistical review, methodological red teaming, and LaTeX/arXiv packaging. Keep sub-agent contexts narrow and artifact-based. Require independent review for anything that makes scientific claims.

Complete Part I and pass the public-artifact quality gate before drafting the paper. Then complete Part II as an arXiv-ready LaTeX manuscript and source package. Research current arXiv requirements and relevant primary literature. Never fabricate citations, author metadata, affiliations, approvals, results, or missing methodological details.

Do not rerun or alter the experiment unless a publication-blocking scientific defect is discovered. Do not claim model-quality, inference-latency, GPU-throughput, or realized-cost effects. Do not publish raw corpora unless their licenses and the repository policy clearly permit it. Do not push, create a public release, mint a DOI, or submit to arXiv without explicit user approval.

Maintain `publication/STATE.md`, `publication/DECISIONS.md`, `publication/CLAIM_LEDGER.md`, `publication/OPEN_ISSUES.md`, `publication/REVIEW_LOG.md`, and `publication/work_queue.jsonl` so another agent can resume from repository state alone.

Begin now with Phase A: preserve the current verified snapshot, inspect the repository, construct the claim registry from the authoritative result files, and run the publication audits. Continue through all non-blocked phases without waiting for routine approval.
```

---

## 30. Definition of Done

The work is complete when:

- The verified scientific snapshot is preserved.
- A new reader can understand the repository from the README.
- Methods, datasets, licenses, results, limitations, and reproduction are documented.
- No raw licensed corpus or secret is accidentally published.
- Every public number is machine-verified.
- Every figure and table regenerates.
- The paper compiles from clean source.
- Every citation is verified against a primary source.
- The paper reports both gains and regressions.
- The paper clearly distinguishes controlled and observational comparisons.
- The paper contains no model-quality or serving-performance overclaim.
- Independent statistical, methodological, claim, artifact, and citation reviews are complete.
- The arXiv source archive passes local packaging checks.
- Human-only author, affiliation, license, category, employer-review, and submission decisions are listed.
- No public push, release, DOI creation, or arXiv submission has occurred without user approval.