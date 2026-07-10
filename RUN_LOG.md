# RUN LOG

> Concise chronology (plan.md §19). Detailed logs live under `results/raw/logs/`.

- **2026-07-10 00:29** — Phase 0 bootstrap committed: repo skeleton, `uv` env,
  CLI/library/tests, `doctor.sh`; 67 tests pass and doctor OK.
- **2026-07-10 00:34** — Added config-driven profiles, smoke profile, and fixed
  training-provenance paths.
- **2026-07-10 00:41** — Phase 1 complete: research, discovery, licensing,
  methodology, and pipeline hardening (true Mixed interleaving, stratified
  bootstrap, eval-category mapping, cross-repo audit parquets).
- **2026-07-10 01:15** — Phases 2-3 complete: pinned pilot corpus (azure-docs
  5,340 docs; 5 transfer repos; Kubernetes 250 docs; WikiText 14,900 docs) and
  three 16K byte-level BPE tokenizers with 100% round-trip / 0 UNK. Caught and
  fixed cross-service near-duplicate bridging leakage via union-find leakage
  groups and near-dup removal.
- **2026-07-10 01:27** — Phases 5-8 complete: full 9-tokenizer matrix
  (8K/16K/32K), vocab-size sensitivity, fragmentation, vocab utilization,
  paired bootstrap, and runtime benchmark (12 encoders × 9 eval sets = 59,160 rows).
- **2026-07-10 02:00** — Red-team NO-GO (20 PASS / 3 CONCERN / 2 FAIL); fixed
  all three blockers: general exact-dedup before train/eval split (134 removed,
  fixing 36 exact leaks), cross-corpus near-dup eval filter (9 removed), and
  artifact `distributable` flag.
- **2026-07-10 02:03** — Blocker 3 resolved: stale 2048-vocab smoke artifacts
  removed and `artifact_distribution_marked` verify gate added; verify 8/8.
- **2026-07-10 02:05** — Finalized report/article/notebooks/README and raw
  results with leakage-clean numbers.
- **2026-07-10 10:08** — Refreshed `STATE.md` to complete status; `verify_all` OK.
- **2026-07-10 10:22** — Documentation refresh reconciled stale tracking docs
  with the completed CPU-only tokenizer-efficiency study.
