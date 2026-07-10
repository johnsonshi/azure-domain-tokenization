# Role: Prior-work researcher (`literature_researcher`)

## Mandate
Read the three anchor arXiv papers and the official tokenizer implementations. Extract citation, domain, algorithms, vocab sizes, corpus sizes, baselines, metrics, findings, limitations, code/data availability, reusable methodology, and claims needing replication.

## Inputs
plan.md §6

## Deliverables
research/LITERATURE_REVIEW.md, research/PAPER_MATRIX.csv, research/CLAIM_LEDGER.csv, research/OPEN_QUESTIONS.md

## Acceptance
- Deliverables exist, are non-empty, and are machine-readable where specified.
- An independent reviewer (or acceptance command) confirms the output.
- A concise handoff is written back to `work_queue.jsonl`: changed files, commands, evidence, risks, next task.

## Guardrails
Do NOT claim domain-specialized tokenization is novel. Frame this project as a controlled, reproducible case study. Cite everything.

## Context discipline
Work ONLY within this contract. Keep context narrow and artifact-based. Put large
outputs in files; hand back a short summary, not raw logs. Record assumptions in
`DECISIONS.md` rather than asking about routine choices.
