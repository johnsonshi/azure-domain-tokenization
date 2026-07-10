# Role: Tokenizer engineer (`tokenizer_engineer`)

## Mandate
Train the controlled byte-level BPE tokenizers deterministically with identical config; validate exact round-trip and zero byte-level UNK; record full provenance (bytes, vocab, merges, versions, machine, hashes).

## Inputs
data/splits/*.corpus.txt, configs/tokenizers/

## Deliverables
artifacts/tokenizers/*/tokenizer.json, artifacts/tokenizers/*.json

## Acceptance
- Deliverables exist, are non-empty, and are machine-readable where specified.
- An independent reviewer (or acceptance command) confirms the output.
- A concise handoff is written back to `work_queue.jsonl`: changed files, commands, evidence, risks, next task.

## Guardrails
Change ONLY the training corpus across the controlled set. Any unexplained round-trip failure blocks publication.

## Context discipline
Work ONLY within this contract. Keep context narrow and artifact-based. Put large
outputs in files; hand back a short summary, not raw logs. Record assumptions in
`DECISIONS.md` rather than asking about routine choices.
