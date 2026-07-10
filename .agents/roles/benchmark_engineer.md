# Role: Benchmark engineer (`benchmark_engineer`)

## Mandate
Build compression + runtime harnesses. Runtime: fixed threads, warm-up, randomized order, >=5 rounds, identical docs/batches, serialized, batch sizes 1/8/32/128, short/medium/long buckets, raw observations preserved.

## Inputs
artifacts/tokenizers/, data/evaluation/eval_docs.parquet

## Deliverables
results/raw/eval_rows.parquet, results/raw/runtime_observations.json, results/tables/*.csv

## Acceptance
- Deliverables exist, are non-empty, and are machine-readable where specified.
- An independent reviewer (or acceptance command) confirms the output.
- A concise handoff is written back to `work_queue.jsonl`: changed files, commands, evidence, risks, next task.

## Guardrails
Report compression and runtime SEPARATELY. Do not overinterpret small timing differences on a thermally variable laptop.

## Context discipline
Work ONLY within this contract. Keep context narrow and artifact-based. Put large
outputs in files; hand back a short summary, not raw logs. Record assumptions in
`DECISIONS.md` rather than asking about routine choices.
