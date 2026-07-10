# DECISIONS

> Append-only decision log (plan.md §19). Each entry: timestamp, decision,
> alternatives, evidence, owner, revisit condition.

---

### 2026-07-09 · D-0001 · Python 3.12 via `uv`
- **Decision:** Manage the environment with `uv`; pin Python 3.12 (`.python-version`).
- **Alternatives:** system Python 3.9.6 (too old for modern `tokenizers`/`numpy 2`); conda.
- **Evidence:** `uv sync` installed tokenizers 0.21.4, tiktoken 0.9.0, numpy 2.5.1, pandas 2.3.3; 63 tests pass.
- **Owner:** orchestrator. **Revisit:** if a dependency needs a different minor.

### 2026-07-09 · D-0002 · Byte-level BPE (Hugging Face `tokenizers`) as the controlled algorithm
- **Decision:** Primary algorithm = byte-level BPE; NFC; no lowercasing/accent-stripping; fixed byte-level pre-tokenizer + decoder; min-frequency 2; full byte-level initial alphabet; special tokens `<|endoftext|>`, `<|pad|>` counting toward vocab.
- **Alternatives:** SentencePiece Unigram, WordPiece (both deferred to optional ablations).
- **Evidence:** plan.md §13; byte-level BPE gives complete UTF-8 coverage → zero `[UNK]` (verified: round-trip + zero-UNK tests pass).
- **Owner:** methodologist. **Revisit:** if methodologist records a justified change in EXPERIMENT_SPEC.

### 2026-07-09 · D-0003 · General-English control = wikitext-103-raw (Wikipedia-derived)
- **Decision:** General-English corpus = Hugging Face `Salesforce/wikitext`, config `wikitext-103-raw-v1`, fetched as versioned parquet (no rendered-page crawl).
- **Alternatives:** full Wikipedia dump (heavy to process), Project Gutenberg (archaic English, not Wikipedia-style), C4 (huge, license nuance).
- **Evidence:** plan.md §12 "Prefer Wikipedia-derived text"; wikitext is a standard, versioned, permissive (CC-BY-SA) English corpus not dominated by code.
- **Owner:** methodologist/corpus_engineer. **Revisit:** if licensing_reviewer flags CC-BY-SA share-alike as blocking even local use (it should not; raw text is git-ignored).

### 2026-07-09 · D-0004 · External technical control = kubernetes/website
- **Decision:** Non-Microsoft technical-docs control = `kubernetes/website` `content/en/docs` (CC-BY-4.0), eval-only.
- **Alternatives:** HashiCorp docs, Docker docs, Python docs.
- **Evidence:** plan.md §7 suggests Kubernetes; verified license CC-BY-4.0 and path `content/en/docs` via gh api.
- **Owner:** repo_scout. **Revisit:** if k8s docs prove too small/large for the eval budget.

### 2026-07-09 · D-0005 · Azure anchor service selection (20 diverse services)
- **Decision:** Train on 20 diverse `articles/<service>` subtrees of azure-docs (storage, networking, compute, data, integration, IoT, management) via git blobless + cone sparse-checkout.
- **Alternatives:** whole `articles/` (≈27 GB clone, wasteful), stars-based selection (plan.md §7 warns against).
- **Evidence:** azure-docs has 144 services; 20 gives enough bytes for 32 MiB pilot + a meaningful cross-service holdout (~3 services). azure-docs = CC-BY-4.0 (verified via gh api).
- **Owner:** repo_scout/corpus_engineer. **Revisit:** if cleaned azure_train bytes < target, add services.

### 2026-07-09 · D-0006 · Eval-only sources via GitHub API blob downloader
- **Decision:** Transfer + external eval sources are acquired by deterministic GitHub-API blob download (≤ max_docs), not full clone.
- **Alternatives:** sparse-checkout (still downloads whole subtree; wasteful for eval-only).
- **Evidence:** plan.md §9 permits an API blob downloader; keeps acquisition within disk/time budget.
- **Owner:** corpus_engineer. **Revisit:** if API rate limits bite (5000/hr; ~1000 blobs needed).

### 2026-07-09 · D-0007 · Group-aware split strategy
- **Decision:** Route whole services to `azure_cross_service_holdout`; within train services, hold out whole near-duplicate clusters as `azure_same_service_holdout`. Cross-service holdout is the principal Azure eval set.
- **Alternatives:** random doc-level split (leaks near-dupes + same-service style).
- **Evidence:** plan.md §11; leakage tests verify no service or near-dup cluster spans splits.
- **Owner:** corpus_engineer/red_team. **Revisit:** if a service is too large and starves train.

### 2026-07-09 · D-0008 · PowerShell-Docs license pending review
- **Decision:** Mark `MicrosoftDocs/PowerShell-Docs` license `UNKNOWN-PENDING-REVIEW`; use locally for eval only until licensing_reviewer confirms; do not redistribute its text.
- **Evidence:** gh api reports SPDX `NOASSERTION` (GitHub could not auto-detect).
- **Owner:** licensing_reviewer. **Revisit:** upon license confirmation.

### 2026-07-10 · D-0009 · Final transfer selection (5 repos, 4 strata)
- **Decision:** Transfer eval set = architecture-center (architecture), azure-devops-docs (DevOps), sql-docs + fabric-docs (data), microsoft-365-docs (broad enterprise). PowerShell-Docs dropped from the transfer set.
- **Alternatives:** include PowerShell-Docs (licensing later confirmed CC-BY-4.0/MIT, so allowed, but redundant with automation coverage).
- **Evidence:** repo_scout `inventory/SELECTION.md` verified paths + pinned commits; all selected repos are clean CC-BY-4.0 (no NOASSERTION). Gives 4-6 repos across the plan.md §7 strata.
- **Owner:** repo_scout. **Revisit:** if a repo's eval set is too small (<~50 docs).

### 2026-07-10 · D-0010 · Licensing VETO honored — no artifact/raw redistribution for WikiText-derived outputs
- **Decision:** Commit NO raw corpora (all git-ignored) and do NOT redistribute General or Mixed tokenizer artifacts (trained on WikiText, unclear license). Azure-only tokenizer artifacts are distributable with CC-BY attribution. We publish only scripts, manifests, hashes, and aggregate results.
- **Evidence:** licensing_reviewer `licenses/RESTRICTIONS.md` VETO; wikitext license unclear → local-use-only. `.gitignore` already withholds `artifacts/tokenizers/*/tokenizer.json` (only provenance metadata tracked), satisfying the VETO.
- **Owner:** licensing_reviewer (veto power). **Revisit:** on legal review of WikiText redistribution.

### 2026-07-10 · D-0011 · Commit pinning via sources.lock.json (not hard ref checkout)
- **Decision:** Acquire each source at current default-branch HEAD and record the exact commit SHA in `data/manifests/sources.lock.json`. That lock file is the canonical reproducibility pin.
- **Alternatives:** hard `--depth 1` fetch-by-SHA of repo_scout's commits (full-history blobless clone risk / fetch-by-sha fragility; slows the pilot).
- **Evidence:** plan.md §9 requires the lock file with exact SHA + timestamp; repo_scout reference commits are documented in inventory/SELECTION.md.
- **Owner:** corpus_engineer. **Revisit:** if exact historical reproduction is required later.

### 2026-07-10 · D-0012 · Methodologist code gaps addressed
- **Decision:** Implemented the four methodologist-flagged gaps: (1) true document-by-document Mixed interleaving; (2) stratified bootstrap by repository AND content_type at full 10,000 resamples; (3) transfer eval sets mapped to plan.md §14 categories via `eval_category`; (4) cross-repo overlap + exact/near-duplicate audit parquets under `data/audit/`.
- **Evidence:** `research/EXPERIMENT_SPEC.md` handoff; validated on the smoke profile.
- **Owner:** orchestrator. **Revisit:** red-team review of the pilot.

### 2026-07-10 · D-0013 · Plan arXiv IDs verified real
- **Decision:** Treat plan.md §6 arXiv IDs 2601.21665 (AdaptBPE), 2509.26124, 2605.17379 as real prior work.
- **Evidence:** independently fetched arxiv.org/abs/2601.21665 — genuine page (canonical URL + abstract "Subword tokenization methods, such as Byte-Pair Encoding..."). literature_researcher verified all three.
- **Owner:** literature_researcher. **Revisit:** n/a.

### 2026-07-10 · D-0014 · Documentation corrections after final verification
- **Decision:** Treat the final verified test count as 67 (superseding the 63-test count recorded in D-0001), and treat D-0008 (PowerShell pending) as superseded by D-0009 final transfer selection.
- **Alternatives:** Rewrite earlier entries (rejected; this log is append-only).
- **Evidence:** Final `uv run pytest -q -m "not network"` = 67 passed; D-0009 documents the final transfer repo set with PowerShell-Docs dropped.
- **Owner:** orchestrator. **Revisit:** only if final verification is rerun with a different tracked test suite.
