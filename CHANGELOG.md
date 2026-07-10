# Changelog

All notable changes to this repository are documented here. This project is a
research artifact; "releases" correspond to verified experiment snapshots and
publication milestones.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased] — publication preparation

### Added
- Programmatic claim registry (`publication/claims.yaml`, `scripts/verify_claims.py`)
  reconciling every public number against authoritative result files (43 claims).
- Publication figures (`scripts/make_figures.py`): 6 colorblind-safe figures with
  committed source tables, PNG (README) + vector PDF (paper).
- Repository audits (`publication/audits/`): repository, large-files, links,
  license, reproducibility, secret scan, and blocker resolutions.
- Community + metadata files: `LICENSE` (MIT, original code), `CITATION.cff`,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, this changelog.
- Public documentation set under `docs/` and results guide under `results/`.
- License records for `fabric-docs` and `microsoft-365-docs`; top-level `LICENSE`.

### Changed
- Corpus manifests now store repo-relative paths (portability).
- `verify` emits a deterministic report (no wall-clock timestamp).
- `uv.lock` is now tracked (was excluded by a global gitignore).

### Preserved (not changed)
- The verified experiment: results, source pins, tokenizer provenance. Snapshot
  tag `experiment-full-verified-20260709`.

## [experiment-full-verified-20260709] — verified experiment

### Added
- Full controlled matrix: General/Azure/Mixed × 8K/16K/32K byte-level BPE (9
  tokenizers), 32 MiB byte-matched corpora, leakage controls.
- Evaluation across 9 held-out sets (59,160 rows), paired-bootstrap statistics,
  fragmentation + vocabulary utilization, CPU runtime benchmark.
- Automated verification gate (8/8) and two-pass red-team review
  (`research/PILOT_REVIEW.md`).

### Result
- Primary: Azure vs General at 16K uses 36.68% fewer tokens per 1,000 UTF-8 bytes
  on the Azure cross-service holdout (95% CI [35.77%, 37.62%]).
