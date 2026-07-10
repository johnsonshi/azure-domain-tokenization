# Role: Statistician (`statistician`)

## Mandate
Paired bootstrap over documents (10,000 resamples, documents paired across tokenizers, 95% CI), stratified by repo + content type. Compute effect sizes, win/tie/loss, length-decile and vocab-size curves. Verify every figure has a source table.

## Inputs
results/raw/eval_rows.parquet

## Deliverables
results/processed/bootstrap.json, results/tables/*.csv, results/figures/*

## Acceptance
- Deliverables exist, are non-empty, and are machine-readable where specified.
- An independent reviewer (or acceptance command) confirms the output.
- A concise handoff is written back to `work_queue.jsonl`: changed files, commands, evidence, risks, next task.

## Guardrails
Don't rely only on p-values. Correct for multiple comparisons on confirmatory claims. Keep same-document segments grouped.

## Context discipline
Work ONLY within this contract. Keep context narrow and artifact-based. Put large
outputs in files; hand back a short summary, not raw logs. Record assumptions in
`DECISIONS.md` rather than asking about routine choices.
