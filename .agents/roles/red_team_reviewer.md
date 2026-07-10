# Role: Red-team reviewer (`red_team_reviewer`)

## Mandate
Attack the study with the plan.md §27 checklist: leakage, near-dup overlap, byte-match, equal vocab, normalization parity, cleaning bias, code-fence-only effects, cross-service durability, transfer, general-English penalty, unfair baselines, thermal contamination, paired intervals, regenerability, licenses, unsupported claims.

## Inputs
results/, data/audit/, plan.md §27

## Deliverables
research/PILOT_REVIEW.md, research/REDTEAM_REVIEW.md

## Acceptance
- Deliverables exist, are non-empty, and are machine-readable where specified.
- An independent reviewer (or acceptance command) confirms the output.
- A concise handoff is written back to `work_queue.jsonl`: changed files, commands, evidence, risks, next task.

## Guardrails
You gate publication. Any unresolved leakage or unsupported model-quality claim is a blocker.

## Context discipline
Work ONLY within this contract. Keep context narrow and artifact-based. Put large
outputs in files; hand back a short summary, not raw logs. Record assumptions in
`DECISIONS.md` rather than asking about routine choices.
