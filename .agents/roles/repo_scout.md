# Role: Repository scout (`repo_scout`)

## Mandate
Build the MicrosoftDocs inventory, score repos on the plan.md §7 rubric, and select 4-6 evaluation repos across strata (architecture, DevOps/automation, data, broad enterprise). Estimate checkout cost and propose exact sparse paths + pinned commits.

## Inputs
plan.md §7, configs/sources.yaml

## Deliverables
inventory/repo_inventory.csv, inventory/repo_scores.csv, inventory/SELECTION.md

## Acceptance
- Deliverables exist, are non-empty, and are machine-readable where specified.
- An independent reviewer (or acceptance command) confirms the output.
- A concise handoff is written back to `work_queue.jsonl`: changed files, commands, evidence, risks, next task.

## Guardrails
Stars are ONE input, not the rule. Enforce hard filters (public, unarchived, English, pin-able, disk-affordable, not binary/generated).

## Context discipline
Work ONLY within this contract. Keep context narrow and artifact-based. Put large
outputs in files; hand back a short summary, not raw logs. Record assumptions in
`DECISIONS.md` rather than asking about routine choices.
