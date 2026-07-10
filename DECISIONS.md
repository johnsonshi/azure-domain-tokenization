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
