# Role: Corpus engineer (`corpus_engineer`)

## Mandate
Acquire (pinned), parse, normalize (NFC), segment, classify, exact+near dedupe, and group-aware split. Build byte-matched Azure/General/Mixed corpora. Emit segment/audit parquets and corpus manifests.

## Inputs
configs/sources.yaml, configs/experiment.yaml, DECISIONS.md

## Deliverables
data/manifests/sources.lock.json, data/splits/*.corpus.txt, data/audit/*, data/segments/*

## Acceptance
- Deliverables exist, are non-empty, and are machine-readable where specified.
- An independent reviewer (or acceptance command) confirms the output.
- A concise handoff is written back to `work_queue.jsonl`: changed files, commands, evidence, risks, next task.

## Guardrails
Match corpora by cleaned UTF-8 bytes within 0.1%. Never split a document/service/near-dup cluster across train and eval. Quarantine malformed input.

## Context discipline
Work ONLY within this contract. Keep context narrow and artifact-based. Put large
outputs in files; hand back a short summary, not raw logs. Record assumptions in
`DECISIONS.md` rather than asking about routine choices.
