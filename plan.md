# Plan: Domain-Specialized Tokenizer Efficiency for Microsoft Technical Documentation

## 0. Agent execution contract

You are the lead orchestrator for an autonomous, CPU-only research and engineering run on a local MacBook. Execute this plan. Do not merely rewrite or critique it.

Use native sub-agents aggressively when supported. If native sub-agents are unavailable, execute the same roles as isolated work units with separate context files. Every claimed result must correspond to a committed artifact, command output, or machine-readable result file.

Constraints:

- Local CPU only.
- No cloud deployment.
- No GPU requirement.
- No language-model training.
- No claims about model output quality, accuracy, reasoning, or understanding.
- GitHub Copilot CLI may assist with coding and research.
- Internet access may be used for public repositories, papers, dependencies, and public corpora.
- Default runtime budget: 10 hours.
- Default source-data disk budget: 25 GB.
- Default generated-artifact budget: 5 GB.
- Keep at least 15% of disk free.
- Use at most `max(1, logical_cores - 2)` workers for sustained CPU work.
- Serialize timing benchmarks.
- Do not publish raw source corpora unless their licenses and repository policies permit redistribution.

Do not pause for routine methodological choices. Record assumptions in `DECISIONS.md`, choose the most defensible option, execute it, and let an independent reviewer challenge it. Ask the user only when blocked by credentials, unclear licensing that prevents local use, insufficient disk, or a destructive action requiring consent.

Use this bounded loop:

1. Inspect state.
2. Select the highest-priority unblocked task.
3. Delegate it to a role-specific sub-agent.
4. Verify the output independently.
5. Update state and evidence.
6. Replan from measured results.
7. Continue until completion or a stopping condition.

Keep the Mac awake with `caffeinate` while the run is active.

---

## 1. Working title

**Does Your Tokenizer Speak Cloud? Measuring Domain Specialization on Microsoft Technical Documentation**

## 2. Research question

At a fixed tokenizer algorithm, vocabulary size, training-data size, normalization policy, and evaluation set, does training on Azure technical documentation reduce the number of tokens required to encode unseen technical documentation compared with training on general English?

## 3. Hypotheses

### Primary hypothesis

A byte-level BPE tokenizer trained on Azure documentation will produce fewer tokens per 1,000 UTF-8 bytes on held-out Azure documentation than an otherwise identical byte-level BPE tokenizer trained on a byte-matched general-English corpus.

### Secondary hypotheses

1. The Azure-trained tokenizer will retain part of its compression advantage on other Microsoft technical-documentation repositories.
2. The advantage will be larger for commands, identifiers, resource-provider names, API paths, configuration, YAML, JSON, Bicep, PowerShell, and inline code than for prose.
3. A tokenizer trained on a 50/50 mixture of Azure documentation and general English will retain much of the Azure gain while reducing general-English regression.
4. Vocabulary increases from 8K to 16K to 32K will improve compression, with diminishing marginal gains.
5. A specialized tokenizer may reduce token count without improving CPU encoding latency. Compression efficiency and runtime efficiency must be reported separately.
6. Repository popularity will not reliably predict transfer. Content composition and domain similarity should explain more variance than GitHub stars.

### Null hypothesis

After controlling for vocabulary size, tokenizer implementation, training bytes, normalization, sampling, and leakage, Azure-trained and general-English-trained tokenizers have no meaningful difference in token count on held-out technical documentation.

## 4. Scope and claim boundaries

This project can measure:

- Token count and compression on fixed corpora.
- Cross-repository transfer.
- Prose versus technical-syntax effects.
- Vocabulary utilization.
- Identifier fragmentation.
- CPU encode/decode performance.
- In-domain gains and out-of-domain regressions.

This project cannot establish:

- Better LLM output quality.
- Better understanding of Azure.
- Better reasoning or accuracy.
- Proportional GPU latency or cost reductions.
- That a new tokenizer can replace an existing model’s tokenizer.
- Universal superiority of a specialized tokenizer.

A trained model’s embedding table is tied to its tokenizer vocabulary. This study evaluates tokenization only.

---

## 5. Experimental structure

Run two tracks and never mix their causal interpretation.

### Track A: controlled comparison

Train byte-level BPE tokenizers with identical:

- Implementation.
- Pre-tokenizer.
- Decoder.
- Unicode normalization.
- Special tokens.
- Vocabulary size.
- Training bytes.
- Sampling process.
- Evaluation documents.
- Hardware and software environment.

Change only the training corpus:

- General English.
- Azure documentation.
- 50/50 Azure plus general English.

This is the primary causal experiment.

### Track B: existing tokenizer baseline

Evaluate available general-purpose tokenizers such as:

- `tiktoken` `r50k_base`.
- `tiktoken` `cl100k_base`.
- `tiktoken` `o200k_base`.
- A public cased BERT WordPiece tokenizer.
- Other public, locally loadable tokenizers approved by the research agent.

This track is descriptive. Existing tokenizers differ in training data, vocabulary size, normalization, algorithm, and intended model. Put Track A and Track B in separate tables and figures.

---

## 6. Prior-work research

Create:

- `research/LITERATURE_REVIEW.md`
- `research/PAPER_MATRIX.csv`
- `research/CLAIM_LEDGER.csv`
- `research/OPEN_QUESTIONS.md`

Begin with:

1. AdaptBPE: From General Purpose to Specialized Tokenizers  
   https://arxiv.org/abs/2601.21665

2. Vocabulary Customization for Efficient Domain-Specific LLM Deployment  
   https://arxiv.org/abs/2509.26124

3. Learning Faster with Better Tokens: Parameter-Efficient Vocabulary Adaptation for Specialized Text Summarization  
   https://arxiv.org/abs/2605.17379

4. Official implementations:
   - https://github.com/openai/tiktoken
   - https://huggingface.co/docs/tokenizers/
   - https://github.com/google/sentencepiece

For every paper, record:

- Citation and year.
- Domain and languages.
- Tokenizer algorithms and vocabulary sizes.
- Training-corpus sizes.
- Baselines.
- Metrics and statistical methods.
- Reported findings.
- Limitations.
- Code/data availability.
- Reusable methodology.
- Claims that require replication.

Use this framing unless research changes it:

> Prior work establishes that domain vocabulary mismatch can increase token counts. This project provides a controlled, reproducible Azure and Microsoft technical-documentation case study, separates prose from technical syntax, measures cross-repository transfer, and publishes a CPU-only harness.

Do not claim that domain-specialized tokenization is novel.

---

## 7. Repository discovery

### Anchor repository

Train the domain tokenizer on:

- `MicrosoftDocs/azure-docs`

Verify the current README, `LICENSE`, `LICENSE-CODE`, and third-party notices at a pinned commit. Do not assume every MicrosoftDocs repository has the same license.

### Build a current inventory

```bash
mkdir -p inventory research licenses

gh api --paginate \
  'orgs/MicrosoftDocs/repos?per_page=100&type=public' \
  > inventory/microsoftdocs_repos.json
```

Convert this to `inventory/repo_inventory.csv` with:

- `full_name`
- `description`
- `html_url`
- `default_branch`
- `stargazers_count`
- `forks_count`
- `watchers_count`
- `open_issues_count`
- `size_kb`
- `language`
- `license_spdx`
- `archived`
- `disabled`
- `pushed_at`
- `updated_at`
- `created_at`

### Inspect at least these candidates if still public and active

- `MicrosoftDocs/azure-docs`
- `MicrosoftDocs/architecture-center`
- `MicrosoftDocs/azure-devops-docs`
- `MicrosoftDocs/PowerShell-Docs`
- `MicrosoftDocs/sql-docs`
- `MicrosoftDocs/microsoft-365-docs`
- `MicrosoftDocs/visualstudio-docs`
- `MicrosoftDocs/cpp-docs`
- `MicrosoftDocs/SupportArticles-docs`
- `MicrosoftDocs/fabric-docs`

The discovery agent may replace or add candidates using current repository data.

### Hard filters

A repository must be:

- Public and not archived.
- License-reviewed.
- Materially English documentation.
- Pin-able to an exact commit.
- Acquirable within the disk budget.
- Not primarily binary media, generated output, or vendored dependencies.

### Repository score

Create `inventory/repo_scores.csv`:

| Component | Weight |
|---|---:|
| Clean English Markdown volume | 0.25 |
| Documentation purity | 0.20 |
| Domain relevance | 0.20 |
| Cross-domain value | 0.10 |
| Log-scaled stars and forks | 0.10 |
| Freshness | 0.05 |
| Acquisition cost | 0.05 |
| Low duplication risk | 0.05 |

Select four to six evaluation repositories by strata:

1. Azure-adjacent architecture.
2. Automation or DevOps.
3. Data or database.
4. Broad enterprise or developer documentation.

Stars are one input, not the selection rule.

### External controls

Add:

- At least one non-Microsoft technical-documentation corpus with a clear license, such as Kubernetes documentation.
- One reproducible general-English corpus.

The external technical set tests transfer beyond Microsoft house style. The general-English set measures out-of-domain regression.

---

## 8. Licensing gate

Create:

- `licenses/SOURCE_LICENSES.csv`
- `licenses/ATTRIBUTION.md`
- `licenses/RESTRICTIONS.md`

For every source record:

- URL.
- Repository and commit or dataset revision.
- Documentation license.
- Code license if different.
- Third-party notices.
- Redistribution status.
- Required attribution.
- Whether tokenizer artifacts may be distributed.
- Whether only scripts, manifests, hashes, and aggregate results should be published.

If the license is unclear:

- Use the corpus locally only if permitted.
- Do not commit raw text.
- Publish acquisition scripts, source hashes, manifests, and aggregate results.
- Mark the restriction.

This plan is not legal advice.

---

## 9. Acquisition

### Pin every source

Write `data/manifests/sources.lock.json` containing:

- Repository.
- Exact commit SHA.
- Acquisition timestamp.
- Clone/API command.
- Sparse paths.
- File count.
- Source bytes.
- Retained clean-text bytes.
- License identifier.

### Avoid full checkout of giant repositories

Prefer:

```bash
git clone \
  --depth 1 \
  --filter=blob:none \
  --no-checkout \
  https://github.com/MicrosoftDocs/azure-docs.git \
  external/azure-docs
```

Inspect the tree:

```bash
git -C external/azure-docs ls-tree -d HEAD
git -C external/azure-docs rev-parse HEAD
```

Then use sparse checkout:

```bash
git -C external/azure-docs sparse-checkout init --cone
git -C external/azure-docs sparse-checkout set <selected-paths>
git -C external/azure-docs checkout
```

If sparse checkout remains too large, implement a GitHub API blob downloader that:

- Enumerates Markdown paths.
- Selects paths deterministically before download.
- Downloads only selected blobs.
- Verifies blob SHAs.
- Caches responses.
- Resumes safely.
- Handles rate limits.

Do not crawl rendered `learn.microsoft.com` pages when source repositories exist.

### Sampling budgets

- Pipeline pilot: 32 MiB of cleaned text per training corpus.
- Full run: 256 MiB per training corpus.
- Maximum: 512 MiB only if the primary run is complete and time remains.

Match corpora by cleaned UTF-8 bytes, not document count. Sampling must be deterministic from source commit, document hash, configured seed, and target byte budget.

---

## 10. Corpus representations

Create separate representations.

### Raw Markdown

Remove only front matter and known generated/navigation boilerplate. Use for a secondary “repository payload” analysis.

### Semantic full text

Preserve:

- Headings.
- Paragraphs.
- Lists.
- Table-cell text.
- Inline code.
- Code fences.
- Commands.
- Configuration.
- URLs and paths in content.

Remove:

- YAML metadata/front matter.
- Navigation metadata.
- Repeated footer/legal boilerplate.
- Build directives invisible to readers.
- Generated TOC scaffolding.
- Known repository templates.

Use semantic full text for primary tokenizer training.

### Prose only

Natural-language headings, paragraphs, lists, and table text. Exclude code fences and isolate inline code.

### Technical syntax only

Collect:

- Code fences.
- Inline code.
- CLI commands.
- JSON.
- YAML.
- Bicep.
- PowerShell.
- Bash.
- Resource-provider names.
- API paths.
- URLs.
- File paths.
- Environment variables.

### Segment schema

Every segment must include:

- `source_repo`
- `source_commit`
- `source_path`
- `document_id`
- `segment_id`
- `content_type`
- `language`
- `utf8_bytes`
- `unicode_chars`
- `whitespace_words`
- `sha256`
- `split`
- `license_id`

Initial `content_type` values:

- `prose`
- `heading`
- `table`
- `inline_code`
- `code`
- `cli`
- `json`
- `yaml`
- `powershell`
- `bicep`
- `url_path`
- `mixed`
- `unknown`

A rule-based classifier is acceptable. Record its rules and confidence.

---

## 11. Cleaning, deduplication, and leakage

### Cleaning

- Use Unicode NFC.
- Do not lowercase.
- Do not strip accents.
- Preserve case, punctuation, code whitespace, Unicode, emoji, version strings, and placeholders.
- Count and quarantine malformed input rather than silently changing it.

### Exact deduplication

Hash normalized documents and segments with SHA-256. Remove exact duplicates within and across repositories.

### Near-duplicate detection

Use MinHash, SimHash, or another documented method. Produce:

- `data/audit/exact_duplicates.parquet`
- `data/audit/near_duplicates.parquet`
- `data/audit/cross_repo_overlap.parquet`

Remove near-duplicate evaluation items that overlap training beyond a declared threshold.

### Group-aware splitting

Never split lines or paragraphs from the same document between train and test.

Group by:

- Repository.
- Top-level product/service directory.
- Canonical path.
- Near-duplicate cluster.

For Azure, create:

- `azure_train`
- `azure_same_service_holdout`
- `azure_cross_service_holdout`

The cross-service holdout is the principal Azure evaluation set.

---

## 12. Training corpora

Construct three byte-matched corpora.

### Azure

Semantic-full text from `azure_train`.

### General English

A standard, versioned, permissively usable English corpus with enough volume. Prefer Wikipedia-derived text. It must not be dominated by source code or technical documentation.

### Mixed

Exactly:

- 50% Azure bytes.
- 50% general-English bytes.

Interleave deterministically.

Optional after primary completion:

- Azure prose only.
- Azure technical syntax only.
- 20/80 and 80/20 mixes.
- A tokenizer trained on another MicrosoftDocs repository.

---

## 13. Tokenizer specification

### Primary algorithm

Use Hugging Face `tokenizers` byte-level BPE.

Reasons:

- Complete UTF-8 coverage.
- No ordinary-text `[UNK]` loss.
- Appropriate for code, identifiers, punctuation, and uncommon Unicode.
- Consistent CPU implementation.

### Fixed settings

Unless the methodologist records a justified change:

- Byte-level BPE.
- Unicode NFC.
- No lowercasing.
- No accent stripping.
- Fixed byte-level pre-tokenizer.
- Matching byte-level decoder.
- Fixed special-token set.
- Fixed minimum frequency.
- Full byte-level initial alphabet.
- Deterministic corpus sampling and order.
- No added domain tokens outside training.

Store all configurations under `configs/tokenizers/`.

### Vocabulary sizes

Required:

- 8,192
- 16,384
- 32,768

Optional:

- 65,536 after primary completion.

State whether special tokens count toward the requested vocabulary size.

### Primary matrix

| Training corpus | 8K | 16K | 32K |
|---|---:|---:|---:|
| General English | Required | Required | Required |
| Azure | Required | Required | Required |
| Mixed 50/50 | Required | Required | Required |

Total: nine controlled tokenizers.

### Pilot gate

Before all nine:

1. Train 16K General.
2. Train 16K Azure.
3. Train 16K Mixed.
4. Validate round-trip.
5. Run a small held-out benchmark.
6. Audit leakage.
7. Verify result schemas.
8. Obtain independent approval in `PILOT_REVIEW.md`.

### Training metadata

Record:

- Wall time.
- CPU time.
- Peak RSS.
- Input bytes and documents.
- Requested and actual vocabulary size.
- Merge count.
- Artifact size.
- Package versions.
- Git commit.
- Machine metadata.
- Corpus-manifest hash.
- Artifact checksum.

---

## 14. Evaluation sets

Freeze evaluation manifests before inspecting full results.

Required:

1. Azure same-service holdout.
2. Azure cross-service holdout.
3. Microsoft architecture documentation.
4. Microsoft DevOps or automation documentation.
5. Microsoft data documentation.
6. Broad Microsoft enterprise/developer documentation.
7. External technical documentation.
8. General English.
9. Synthetic edge cases.

Synthetic edge cases should include:

- Azure resource-provider names.
- CLI commands and flags.
- GUIDs.
- URLs and paths.
- Semantic versions.
- JSON, YAML, Bicep, PowerShell, and Bash.
- CamelCase, snake_case, and kebab-case.
- Unicode product names.
- Empty strings.
- Repeated strings.
- Unusual whitespace.
- Emoji and symbols.

Synthetic data is diagnostic, not the primary evidence.

---

## 15. Exact metrics

Use “tokenization efficiency” only with a named dimension.

### Primary endpoint

For tokenizer `T` and evaluation corpus `D`:

```text
tokens_per_1000_utf8_bytes(T, D)
  = 1000 * total_tokens(T, D) / total_utf8_bytes(D)
```

Lower is better.

Report:

- Micro ratio over all bytes.
- Macro mean over document-level ratios.

### Primary effect size

```text
relative_token_reduction(A versus G, D)
  = 100 * (tokens(G, D) - tokens(A, D)) / tokens(G, D)
```

Where:

- `A` is Azure-trained.
- `G` is matched General-trained.

Positive means Azure uses fewer tokens.

Also compute Mixed versus General and Azure versus Mixed.

### Secondary compression metrics

- Tokens per 1,000 Unicode code points.
- Characters per token.
- UTF-8 bytes per token.
- Tokens per whitespace-delimited word for English prose only.
- Token count per document.
- Token count per content type.
- Token count per repository.
- Effect by document-length decile.
- Percentage of documents where specialized wins, ties, or loses.
- Median and p95 document-level reduction.
- Estimated characters/bytes fitting in 4K, 8K, 32K, and 128K contexts.
- Estimated token-billing difference for fixed document sizes.

Clearly label context and billing calculations as estimates.

### Coverage and correctness

- Exact encode/decode round-trip rate.
- `[UNK]` count and rate.
- Exceptions.
- Malformed samples.
- Samples changed by normalization.
- Reconstruction failures.
- Empty output.

Any unexplained round-trip failure blocks publication.

### Fragmentation

For words and identifiers:

- Mean, median, and p95 tokens per identifier.
- Fraction encoded as one token.
- Fraction encoded as two tokens.
- Fraction encoded as three or more.
- Tokens per CLI flag.
- Tokens per resource-provider identifier.
- Tokens per URL/path.
- Tokens per code line.
- Tokens per prose word.

Report aggregate distributions plus examples of both gains and regressions.

### Vocabulary metrics

- Fraction used at least once per evaluation set.
- Fraction used at least 10, 100, and 1,000 times.
- Token-occurrence share of top 1%, 5%, and 10% of vocabulary.
- Vocabulary entries unused on all evaluation sets.
- Mean and distribution of token byte length.
- Token classes: letters, digits, punctuation, whitespace, mixed.
- Azure-versus-general enrichment.
- Vocabulary overlap between trained tokenizers.
- Tokens unique to Azure, General, and Mixed.

### Runtime efficiency

Measure separately:

- Encode latency.
- Decode latency.
- UTF-8 MB/s.
- Characters/s.
- Documents/s.
- Median, p95, and p99.
- Peak RSS.
- Load time.
- Artifact size.

Do not use tokens/s as the sole throughput metric.

Runtime controls:

- Plug into power.
- Record Mac model, chip, cores, RAM, macOS, Python, and packages.
- Stop other project workloads.
- Fix thread count.
- Warm up.
- Randomize tokenizer order across rounds.
- Use at least five measured rounds.
- Use identical documents and batches.
- Serialize benchmarks.
- Test batch sizes 1, 8, 32, and 128.
- Test short, medium, and long document buckets.
- Preserve raw observations.
- Do not overinterpret small differences on a thermally variable laptop.

---

## 16. Statistics

Token counts are deterministic. Uncertainty comes from the sampled documents.

Use paired bootstrap resampling over documents:

- 10,000 final resamples.
- Same documents paired across tokenizers.
- 95% confidence intervals for relative token reduction.
- Stratify by repository and content type.
- Keep segments from the same document grouped.

Report:

- Mean and median paired difference.
- Win/tie/loss rate.
- Effect by length decile.
- Effect by content type.
- Effect by repository.
- Effect by vocabulary size.

Do not rely only on p-values. Mark exploratory comparisons. Correct for multiple comparisons when making many confirmatory claims.

Before the full run, freeze:

- `research/EXPERIMENT_SPEC.md`
- `research/DEVIATIONS.md`

`EXPERIMENT_SPEC.md` must declare:

- Primary hypothesis.
- Primary endpoint.
- Required matrix.
- Evaluation sets.
- Exclusion rules.
- Statistical method.
- Stopping rules.

---

## 17. Required controls and ablations

Required:

1. Equal vocabulary sizes.
2. Equal training bytes.
3. Same byte-level BPE implementation.
4. General, Azure, and Mixed corpora.
5. Azure same-service and cross-service holdouts.
6. General-English regression measurement.
7. Prose versus technical syntax.
8. Exact and near-duplicate leakage checks.
9. Existing-tokenizer baseline reported separately.
10. 8K, 16K, and 32K sensitivity.

Optional only after primary completion:

- Azure prose-only training.
- Azure syntax-only training.
- 20/80 and 80/20 mixes.
- Unigram and WordPiece.
- Pre-tokenizer variants.
- 64K vocabulary.
- Leave-one-repository-out training.
- Temporal holdout.
- AdaptBPE-style vocabulary replacement.

---

## 18. Repository structure

```text
msdocs-tokenizer-study/
├── plan.md
├── README.md
├── STATE.md
├── DECISIONS.md
├── FINDINGS.md
├── RUN_LOG.md
├── work_queue.jsonl
├── pyproject.toml
├── uv.lock
├── Makefile
├── .gitignore
├── .agents/
│   ├── roles/
│   │   ├── orchestrator.md
│   │   ├── literature_researcher.md
│   │   ├── repo_scout.md
│   │   ├── licensing_reviewer.md
│   │   ├── corpus_engineer.md
│   │   ├── methodologist.md
│   │   ├── tokenizer_engineer.md
│   │   ├── benchmark_engineer.md
│   │   ├── statistician.md
│   │   ├── red_team_reviewer.md
│   │   └── technical_writer.md
│   └── task_contract.schema.json
├── configs/
├── inventory/
├── licenses/
├── research/
├── external/
├── data/
│   ├── manifests/
│   ├── raw/
│   ├── normalized/
│   ├── segments/
│   ├── splits/
│   ├── evaluation/
│   └── audit/
├── artifacts/tokenizers/
├── results/
│   ├── raw/
│   ├── processed/
│   ├── tables/
│   ├── figures/
│   └── reports/
├── notebooks/
│   ├── 01_repository_inventory.ipynb
│   ├── 02_corpus_audit.ipynb
│   ├── 03_tokenizer_training.ipynb
│   ├── 04_compression_results.ipynb
│   ├── 05_fragmentation_analysis.ipynb
│   ├── 06_runtime_benchmark.ipynb
│   └── 07_final_report.ipynb
├── src/msdocs_tokenizer/
├── tests/
└── scripts/
    ├── overnight.sh
    ├── doctor.sh
    ├── resume.sh
    └── verify_all.sh
```

Notebooks present and explore results. CLI commands execute the pipeline.

---

## 19. Orchestrator and context management

### Canonical files

`STATE.md`, under 250 lines:

- Phase.
- Completed gates.
- Active and blocked tasks.
- Remaining time and disk.
- Best next action.
- Last verified command.
- Links to detailed artifacts.

`DECISIONS.md`, append-only:

- Timestamp.
- Decision.
- Alternatives.
- Evidence.
- Owner.
- Revisit condition.

`FINDINGS.md`:

- Verified findings only.
- Result file.
- Reproduction command.
- Commit.
- Reviewer.
- Caveat.

`RUN_LOG.md`:

- Concise chronology.
- Detailed logs live under `results/raw/logs/`.

`work_queue.jsonl` task example:

```json
{
  "id": "TASK-0001",
  "role": "corpus_engineer",
  "objective": "Build semantic-full extraction for Azure Markdown",
  "inputs": ["configs/cleaning.yaml", "data/manifests/sources.lock.json"],
  "outputs": ["data/segments/azure.parquet"],
  "acceptance_commands": ["uv run pytest tests/test_markdown_extract.py"],
  "status": "ready",
  "attempt": 0,
  "max_attempts": 3,
  "depends_on": [],
  "context_files": ["DECISIONS.md", "research/EXPERIMENT_SPEC.md"]
}
```

### Context rules

- Give each sub-agent only its role brief, task contract, required context, and relevant paths.
- Do not pass the whole conversation.
- Require a concise handoff: changed files, commands, evidence, risks, next task.
- Put large outputs in files.
- Orchestrator reads handoffs and structured results, not all raw logs.
- Summarize each completed phase.
- Preserve provenance.
- Use schemas for configs, tasks, and results.
- A fresh agent must resume from repository state alone.

### Roles

Literature researcher:
- Prior work, paper matrix, claim boundaries.

Repository scout:
- Inventory, score, select, estimate checkout cost, pin commits.

Licensing reviewer:
- Licenses, notices, attribution, veto power.

Corpus engineer:
- Acquire, parse, normalize, segment, dedupe, split.

Methodologist:
- Hypotheses, metrics, controls, statistical design, experiment freeze.

Tokenizer engineer:
- Deterministic training, validation, provenance.

Benchmark engineer:
- Compression and runtime harnesses, raw results.

Statistician:
- Bootstrap, effect sizes, tables, plot verification.

Red-team reviewer:
- Leakage, confounds, unfair comparisons, unsupported claims.

Technical writer:
- README, report, article. Every number must cite a result table.

### Parallelism

Parallelize:

- Literature research.
- Repository inventory.
- License inspection across sources.
- Static code review.
- Test creation.
- Independent corpus audits.

Limit to two concurrent CPU-heavy preprocessing tasks.

Serialize:

- Tokenizer training when memory pressure is material.
- Runtime benchmarks.
- Final aggregation.
- Writes to shared state files.
- Overlapping Git changes.

Aggressive parallelism means independent work proceeds concurrently. Do not recursively spawn unbounded agents.

### Verification and retries

Every substantive task needs:

1. Producer.
2. Acceptance command.
3. Independent verification.
4. Evidence in state.

Maximum three attempts. After two failures, use a different agent or approach. After three, mark blocked, reduce scope if possible, and continue. Never retry an identical command without changing a relevant condition.

---

## 20. Overnight phases

### Phase 0: bootstrap

Create environment, skeleton, state, role briefs, task schema, doctor script, and `caffeinate` wrapper.

Gate:

```bash
uv run pytest
bash scripts/doctor.sh
```

### Phase 1: parallel research and discovery

Run literature, repository, license, and methodology agents in parallel.

Gate:

- Source selection fits disk.
- Licenses reviewed.
- Primary hypothesis and endpoint frozen.

### Phase 2: corpus pilot

Build 32 MiB Azure, General, and Mixed corpora.

Gate:

- No document crosses splits.
- No exact train/eval duplicate.
- Near-duplicate rate measured.
- Valid UTF-8.
- Byte budgets match within 0.1%.
- License manifests complete.

### Phase 3: tokenizer pilot

Train 16K Azure, General, and Mixed.

Gate:

- Exact round-trip on evaluation sample.
- Zero unexplained `[UNK]`.
- Equal configuration and training bytes.
- Metric implementation independently verified.
- No obvious leakage.
- `PILOT_REVIEW.md` approved.

### Phase 4: full corpus

Scale to 256 MiB if available. Freeze evaluation and experiment spec.

Gate:

- Red-team approval of splits and leakage controls.

### Phase 5: full matrix

Train nine tokenizers. Save config, logs, provenance, checksums.

### Phase 6: compression and fragmentation

Evaluate all fixed sets and existing baselines.

Gate:

- Independent recalculation of random samples.
- Segment, document, and corpus totals reconcile.
- No result depends on hidden notebook state.

### Phase 7: runtime benchmark

Stop other work, randomize order, run five rounds, preserve raw timing.

### Phase 8: statistics

Paired bootstrap, intervals, transfer, content breakdown, regressions, vocabulary-size curves.

Gate:

- Statistician and red-team review.

### Phase 9: report

Produce README, `FINAL_REPORT.md`, final notebook, figures, source tables, attribution, limitations, article draft, and reproduction commands.

Gate:

```bash
bash scripts/verify_all.sh
make report
git status --short
```

---

## 21. Loop engineering

For every cycle:

### Observe

Read state, queue, latest handoff, budget, and failing commands.

### Orient

Determine active gate, independent tasks, highest-information next task, invalidated assumptions, and minimum-study risk.

### Delegate

Create explicit task contracts. Parallelize independent I/O and research. Serialize noisy measurement.

### Execute

Agents perform only contracted work. Scope expansion becomes a proposed task.

### Verify

Run acceptance commands. Use an independent methodological reviewer.

### Synthesize

Update state, decisions, findings, queue, and phase handoff.

### Replan

When an assumption fails:

- Record a deviation.
- Change the smallest necessary component.
- Rerun only affected downstream work.
- Do not restart unrelated completed phases.

### Continue or stop

Continue only when a required deliverable remains and budget permits. Prefer verification and final reporting over optional experiments near the deadline.

---

## 22. Harness requirements

Provide resumable commands resembling:

```bash
make inventory
make research
make acquire-pilot
make audit-pilot
make train-pilot
make evaluate-pilot
make acquire-full
make train-all
make evaluate-all
make benchmark-runtime
make analyze
make report
make verify
```

Every command must:

- Be safe to rerun.
- Avoid recomputing valid outputs.
- Check input hashes.
- Log commands and errors.
- Return nonzero on failure.
- Produce structured outputs.
- Record config and Git commit.
- Use atomic writes.
- Lock shared outputs.
- Detect stale downstream artifacts by content hash.

---

## 23. Tests

Required:

- Front-matter removal.
- Code-fence and inline-code extraction.
- Table extraction.
- Unicode normalization.
- Exact and near dedupe.
- Group-aware split isolation.
- Deterministic sampling.
- Exact byte matching.
- Tokenizer round-trip.
- Zero byte-level `[UNK]`.
- Metric formulas on hand-worked examples.
- Context estimates.
- Aggregation.
- Bootstrap reproducibility.
- Existing-tokenizer adapters.
- Resume after interruption.
- Provenance completeness.

Add a tiny fixture corpus so tests run without external downloads.

---

## 24. Result schemas

### Evaluation row

```json
{
  "tokenizer_id": "azure-bytebpe-16384",
  "eval_set": "azure-cross-service",
  "repository": "MicrosoftDocs/azure-docs",
  "document_id": "sha256:...",
  "content_type": "mixed",
  "utf8_bytes": 8421,
  "unicode_chars": 8399,
  "whitespace_words": 1182,
  "token_count": 2134,
  "roundtrip_ok": true,
  "unk_count": 0
}
```

### Tokenizer provenance

```json
{
  "tokenizer_id": "azure-bytebpe-16384",
  "algorithm": "byte_level_bpe",
  "vocab_size_requested": 16384,
  "vocab_size_actual": 16384,
  "training_corpus": "azure",
  "training_bytes": 268435456,
  "training_manifest_sha256": "...",
  "config_sha256": "...",
  "package_versions": {},
  "machine_id": "...",
  "created_at": "...",
  "artifact_sha256": "..."
}
```

Define JSON Schema or Pydantic models.

---

## 25. Required figures

1. Relative token reduction on Azure cross-service holdout.
2. Tokens per 1,000 bytes by corpus and vocabulary size.
3. In-domain gain versus general-English regression.
4. Transfer across MicrosoftDocs repositories.
5. Effect by content type.
6. Identifier fragmentation.
7. Vocabulary-size diminishing returns.
8. Vocabulary utilization.
9. Compression versus artifact size.
10. Runtime throughput versus compression.
11. Existing-tokenizer baseline in a separate figure.
12. Bootstrap intervals.
13. Win/tie/loss by document.
14. Aggregate regressions by content type.

Every figure must have a committed source table. Avoid 3D, radar, and dual-axis charts.

---

## 26. Interpretation rules

- Say “uses fewer tokens on this corpus,” not “understands the domain.”
- Say “estimated token-cost difference,” not “measured cost savings.”
- Say “CPU tokenizer throughput,” not “inference throughput.”
- Do not imply drop-in replacement for a model tokenizer.
- Do not treat production-tokenizer comparisons as controlled.
- Report out-of-domain regressions with in-domain gains.
- Separate prose from technical syntax.
- State micro versus macro averaging.
- Disclose corpus size, commits, sampling, and exclusions.
- Include negative and inconclusive findings.
- Do not hide repositories where Azure loses.
- Do not infer model quality, GPU latency, or exact cost from token count.

---

## 27. Red-team checklist

1. Did evaluation text leak into training?
2. Are near-duplicates shared across repositories?
3. Are corpora matched by cleaned bytes?
4. Are vocabulary sizes actually equal?
5. Is normalization identical?
6. Did Markdown cleaning favor one corpus?
7. Is the result driven by front matter or repeated punctuation?
8. Is it driven only by code fences?
9. Does the gain remain on cross-service Azure?
10. Does it transfer beyond MicrosoftDocs?
11. What is the general-English penalty?
12. Are production baselines being compared unfairly?
13. Are timing results contaminated by thermal drift or concurrency?
14. Are intervals paired by document?
15. Can every number be regenerated from raw tables?
16. Are licenses and attribution satisfied?
17. Are any model-quality claims unsupported?
18. Did stars dominate source selection?
19. Is the corpus large enough for the vocabulary?
20. How many vocabulary entries are unused?
21. Does Mixed provide nearly the same gain with less regression?
22. Does the conclusion survive removing code/config?
23. Does it survive removing document-length extremes?
24. May tokenizer artifacts be distributed?
25. Is raw licensed text accidentally committed?

---

## 28. Fallback and stopping rules

### Minimum viable study

If constrained, complete:

- 32 MiB each of Azure, General, and Mixed.
- Three 16K byte-level BPE tokenizers.
- Azure cross-service holdout.
- Two other MicrosoftDocs repositories.
- One external technical corpus.
- One general-English set.
- Compression metrics.
- Prose versus syntax fragmentation.
- Round-trip tests.
- Paired bootstrap.
- Final report.

### Remove scope in this order

1. 64K.
2. Optional algorithms.
3. Optional mix ratios.
4. Runtime batch expansion.
5. 8K.
6. Extra evaluation repositories.
7. 32K only if necessary.

Never remove:

- Matched 16K General/Azure/Mixed.
- Leakage controls.
- General-English regression.
- Azure cross-service holdout.
- License review.
- Round-trip validation.
- Raw results.

### Stop conditions

Stop new work when:

- Required gates pass.
- Fewer than 45 minutes remain.
- Free disk is below 15%.
- Three tasks share the same external blocker.
- Optional expansion threatens report completion.

Use remaining time for verification and reporting.

---

## 29. Final deliverables

Required:

1. Reproducible Git repository.
2. `plan.md`.
3. Current state and decision logs.
4. Literature review and paper matrix.
5. Repository inventory and selection rationale.
6. License and attribution records.
7. Acquisition and cleaning code.
8. Frozen manifests and hashes.
9. Nine controlled tokenizer artifacts, or documented fallback.
10. Existing-tokenizer adapters.
11. Raw document-level results.
12. Processed tables.
13. Statistical analysis.
14. Figures with source tables.
15. Jupyter notebooks.
16. `FINAL_REPORT.md`.
17. Reproduction instructions.
18. Red-team review.
19. Limitations and deviations.
20. Article draft.

Optional:

- LinkedIn post.
- Video outline.
- Interactive comparison page.
- Follow-up model-vocabulary adaptation proposal outside this study.

---

## 30. Final report structure

1. Research question.
2. Hypotheses.
3. Prior work.
4. Sources and licenses.
5. Corpus construction.
6. Leakage controls.
7. Controlled tokenizer design.
8. Existing baselines.
9. Primary compression result.
10. Vocabulary-size sensitivity.
11. Cross-repository transfer.
12. Prose versus syntax.
13. Identifier fragmentation.
14. General-English regression.
15. Runtime results.
16. Vocabulary utilization.
17. Statistical uncertainty.
18. Failure cases.
19. Limitations.
20. Reproduction.
21. Conclusions limited to measured tokenization behavior.

---

## 31. Initial orchestrator prompt

```text
Execute plan.md as an autonomous local research project.

Create the repository skeleton, state files, task queue, role briefs, and environment. Run repository discovery, licensing review, literature research, and methodology review in parallel sub-agents. Synthesize them into a frozen pilot specification before acquiring substantial data.

Use bounded PLAN -> DELEGATE -> EXECUTE -> VERIFY -> SYNTHESIZE -> REPLAN loops. Maintain STATE.md, DECISIONS.md, FINDINGS.md, RUN_LOG.md, and work_queue.jsonl. Keep contexts narrow and artifact-based. Require independent review for methodology, leakage, statistics, and final claims.

Do not stop for routine choices. Record assumptions and proceed. Do not deploy cloud resources, use GPUs, train a language model, crawl rendered Microsoft Learn pages when source repositories exist, or claim effects on model output quality.

Run the pilot first. Expand only after the pilot gate passes. Preserve time for verification and reporting. If constrained, complete the minimum viable study instead of leaving the full matrix incomplete.
```

---

## 32. Completion definition

Complete only when:

- The primary comparison is controlled.
- Evaluation data are frozen and leakage-audited.
- Commits and licenses are recorded.
- Every tokenizer round-trips evaluation input.
- Raw per-document results exist.
- Statistical intervals are reproducible.
- In-domain gains and out-of-domain regressions are both reported.
- Production baselines are labeled observational.
- Every number traces to a machine-readable table.
- A clean checkout can reproduce the report after obtaining licensed sources.
- Red-team review has no unresolved publication blocker.
