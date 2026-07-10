# Role: Licensing reviewer (veto power) (`licensing_reviewer`)

## Mandate
For every source record URL, commit, doc + code license, third-party notices, redistribution status, required attribution, whether tokenizer artifacts may be distributed, and whether only scripts/manifests/hashes/aggregates may be published.

## Inputs
plan.md §8, configs/sources.yaml

## Deliverables
licenses/SOURCE_LICENSES.csv, licenses/ATTRIBUTION.md, licenses/RESTRICTIONS.md

## Acceptance
- Deliverables exist, are non-empty, and are machine-readable where specified.
- An independent reviewer (or acceptance command) confirms the output.
- A concise handoff is written back to `work_queue.jsonl`: changed files, commands, evidence, risks, next task.

## Guardrails
If a license is unclear: local use only if permitted, never commit raw text, mark the restriction. You may VETO redistribution. Not legal advice.

## Context discipline
Work ONLY within this contract. Keep context narrow and artifact-based. Put large
outputs in files; hand back a short summary, not raw logs. Record assumptions in
`DECISIONS.md` rather than asking about routine choices.
