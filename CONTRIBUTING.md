# Contributing

Thanks for your interest. This repository is a **research artifact** accompanying
a paper on domain-specialized tokenizer compression. Its primary goal is
reproducibility and clarity, not feature development.

## Ground rules

- **Do not alter the frozen experiment.** The verified results under `results/`,
  the source pins in `data/manifests/`, and the tokenizer provenance under
  `artifacts/tokenizers/*.json` are the scientific record. Changing them would
  invalidate the paper's claims. The snapshot is tagged
  `experiment-full-verified-20260709`.
- **Every public number must be registered.** Any number shown in the README,
  docs, figures, tables, or paper must be in `publication/claims.yaml` and pass
  `make verify-claims`. Add new numbers to the registry with an extraction spec.
- **Do not commit raw corpora or secrets.** Raw source text and the local git
  clone are git-ignored. Run `detect-secrets scan $(git ls-files)` before
  committing.
- **Tokenization-only claims.** Do not add claims about model quality, accuracy,
  reasoning, inference latency, GPU throughput, or realized cost.

## Development setup

```bash
uv sync                     # create the environment (Python 3.12)
bash scripts/doctor.sh      # environment preflight
uv run pytest -q -m "not network"
make verify                 # re-check the existing artifacts (no retraining)
make verify-claims          # reconcile every registered number
```

## Making changes

- Code lives in `src/msdocs_tokenizer/`; tests in `tests/`. Add/adjust tests for
  any behavior change and keep them passing.
- Regenerate derived artifacts with the Make targets (`make analyze`, `make
  figures`, `make report`) rather than editing outputs by hand.
- Keep documentation numbers sourced from the claim registry.
- Follow the existing style (type hints, small focused functions, comments only
  where clarification is needed).

## Reporting issues

Open an issue describing the observed vs expected behavior and the exact command.
For anything touching results, include the output of `make verify` and
`make verify-claims`.

## Scope of contributions welcomed

- Documentation clarity, reproducibility fixes, additional tests, portability.
- New analyses that extend (not replace) the frozen results, clearly labeled.

By contributing you agree your contributions are licensed under the repository's
[MIT LICENSE](LICENSE) (original code/writing only; third-party corpora retain
their own licenses).
