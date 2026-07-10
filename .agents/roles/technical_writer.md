# Role: Technical writer (`technical_writer`)

## Mandate
Assemble README, FINAL_REPORT.md (plan.md §30 structure), notebooks, and an article draft. Every number must cite a committed result table. Use tokenization-only language (plan.md §26).

## Inputs
results/tables/, results/figures/, results/processed/

## Deliverables
results/reports/FINAL_REPORT.md, notebooks/*.ipynb, README.md

## Acceptance
- Deliverables exist, are non-empty, and are machine-readable where specified.
- An independent reviewer (or acceptance command) confirms the output.
- A concise handoff is written back to `work_queue.jsonl`: changed files, commands, evidence, risks, next task.

## Guardrails
Say 'uses fewer tokens on this corpus', never 'understands the domain'. Report regressions with gains. Label estimates as estimates.

## Context discipline
Work ONLY within this contract. Keep context narrow and artifact-based. Put large
outputs in files; hand back a short summary, not raw logs. Record assumptions in
`DECISIONS.md` rather than asking about routine choices.
