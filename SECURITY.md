# Security Policy

This repository is a research artifact. It contains **no service, no network
endpoint, and no user data**. It processes only public documentation and runs
locally on CPU.

## Reporting a vulnerability

If you discover a security issue (for example, a dependency vulnerability, a
secret accidentally committed, or a supply-chain concern in the build), please
report it privately to `<AUTHOR EMAIL>` (see
`publication/AUTHOR_INPUTS_REQUIRED.md`) rather than opening a public issue.
Please include steps to reproduce and the affected files/commit.

We aim to acknowledge reports within a reasonable time and to address confirmed
issues promptly.

## Scope and hardening

- **Secrets:** the repository is scanned with `detect-secrets`; a baseline is at
  `.secrets.baseline`. The only high-entropy strings are SHA-256 provenance
  hashes and pinned git commit SHAs (see `publication/audits/SECRET_SCAN.md`).
- **Data:** raw corpora and the local source clone are git-ignored and never
  committed. Reproduction downloads pinned public sources.
- **Dependencies:** pinned via `uv.lock`. Review it before installing.

## Non-scope

There is no deployed system to attack. Findings about the *scientific* method
belong in a GitHub issue or the paper's review process, not this security policy.
