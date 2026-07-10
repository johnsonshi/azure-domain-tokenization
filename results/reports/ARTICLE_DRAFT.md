# Does Your Tokenizer Speak Cloud?

### A controlled, CPU-only study of domain-specialized tokenizer efficiency on Microsoft technical documentation

*Article draft. Every number here is generated from a committed result table in this
repository (`results/tables/`, `results/processed/`) and is reproducible from a clean
checkout. This study measures **tokenization only** — it makes no claim about model
output quality, accuracy, reasoning, latency, or cost.*

---

## The question

Large language models read text as **tokens**, not characters. A tokenizer trained on
general web text may chop a string like `Microsoft.ContainerRegistry/registries` into a
dozen pieces. If you work all day in Azure documentation, that fragmentation adds up: more
tokens per page means less content per context window and a higher token bill.

So we asked a narrow, falsifiable question:

> At a fixed algorithm, vocabulary size, training-data size, and evaluation set, does
> training a byte-level BPE tokenizer on **Azure documentation** reduce the number of
> tokens needed to encode *unseen* technical documentation, compared with an otherwise
> identical tokenizer trained on **byte-matched general English**?

## How we set it up (and what makes it a controlled experiment)

We trained tokenizers that are **identical in every respect except the training corpus**:
same byte-level BPE implementation, same Unicode NFC normalization, same pre-tokenizer and
decoder, same special tokens, the same requested vocabulary size, and the *same number of
training bytes* (32 MiB, matched to within 0 bytes). The only thing we changed was the
text they learned from:

- **General** — Wikipedia-derived English (WikiText-103).
- **Azure** — 20 Azure documentation services from `MicrosoftDocs/azure-docs`.
- **Mixed** — a deterministic 50/50 interleave of the two.

We trained all three at three vocabulary sizes (8,192 / 16,384 / 32,768) — nine tokenizers
in total.

The hard part of a study like this is **leakage**. If a page you test on also appears in
training, the "specialized" tokenizer looks better than it is. We were strict:

- Whole Azure **services** are held out as the principal test set (`data-factory`,
  `event-hubs`, `expressroute`, `frontdoor`, `virtual-network`) — the tokenizer never sees
  a single page from them during training.
- **Exact** duplicates are removed (SHA-256), and **near-duplicates** are removed with
  MinHash. Azure auto-generates near-identical "Azure Policy reference" pages across many
  services; left in, these would quietly bridge test services into training. We drop them.
- Any test page that is a near-duplicate of *any* training page — across all corpora — is
  removed before scoring.

Every tokenizer reconstructs its input exactly (100% round-trip, zero `[UNK]`), because
byte-level BPE has full byte coverage.

## The headline result

On the held-out Azure services, the Azure-trained tokenizer needs **36.7% fewer tokens per
1,000 bytes** than the byte-matched general tokenizer (240 vs 380 tokens / 1,000 UTF-8
bytes; 95% paired-bootstrap CI [35.8%, 37.6%]; it wins on **100%** of the 964 test pages).

This is not a code-fence artifact. If we look at **prose only** — the natural-language
sentences, with code stripped out — the Azure tokenizer still wins by **+36.8%**.

## Why: it stops shattering Azure's vocabulary

The mechanism is visible in how each tokenizer fragments Azure-specific strings on the
held-out set (mean tokens per item, lower is better):

| Construct | Azure | General |
|---|---:|---:|
| Resource provider (`Microsoft.X/Y`) | **10.5** | 22.6 |
| URL / path | **26.3** | 42.8 |
| CLI flag (`--resource-group`) | **4.6** | 8.1 |
| camelCase identifier | **2.9** | 6.5 |
| Prose word | **1.6** | 2.9 |

And it uses its vocabulary far more efficiently on Azure content: the Azure tokenizer
actually uses **82%** of its 16K vocabulary on the held-out set; the general tokenizer
uses only **48%**, wasting thousands of entries on words that never appear.

## The honest trade-off

Specialization cuts both ways. On **general English**, the Azure tokenizer is **34.8%
*worse*** than the general one. That is exactly what you would expect, and we report it
next to the gain rather than hiding it.

The interesting middle ground is **Mixed (50/50)**: it keeps **+34.2%** of the Azure gain
on Azure docs while shrinking the English penalty from −34.8% to just **−4.4%**. If you
need one tokenizer that does both, a blended corpus is a compelling option.

## How far does it travel?

The advantage decays smoothly with domain distance — and it does not stop at Microsoft:

| Test corpus | Azure vs General |
|---|---:|
| Azure (held-out services) | +36.7% |
| Azure (held-out, same services) | +35.0% |
| Microsoft data docs (SQL, Fabric) | +32.9% |
| Microsoft DevOps docs | +31.8% |
| **Kubernetes docs (non-Microsoft)** | **+31.2%** |
| Microsoft architecture docs | +26.0% |
| Broad Microsoft enterprise docs | +25.9% |

## Bigger vocabulary helps — with diminishing returns

Going from 8K → 16K → 32K vocabulary lowers everyone's token counts (general 404 → 380 →
361 tokens/1,000 bytes; Azure 256 → 240 → 233), with the biggest jump at the low end. The
*relative* Azure advantage stays remarkably stable at ~36–37%.

## Compression is not speed

A smaller token count does **not** automatically mean a faster tokenizer. On CPU, our
research-grade Hugging Face tokenizers run at ~5 MB/s, while the production-optimized
`tiktoken` runs at 11–19 MB/s. We report compression and runtime as **separate** axes, and
we treat production tokenizers as an *observational* baseline, never a controlled
comparison.

## What this does and doesn't show

It shows, on these corpora, under these controls, that a domain-matched tokenizer encodes
Microsoft technical documentation in substantially fewer tokens — and it explains why
(less fragmentation of identifiers, paths, and commands; better vocabulary utilization).

It does **not** show better model quality, reasoning, or accuracy; it does not promise
proportional GPU-latency or cost savings; and it does not suggest you can swap a model's
tokenizer without retraining its embeddings. Those are different experiments.

## Reproduce it

```bash
uv sync && bash scripts/doctor.sh
make acquire-pilot audit-pilot train-pilot evaluate-pilot analyze report verify
```

Everything is deterministic from a fixed seed, pinned source commits, and content hashes.
Raw corpora are never committed; we publish the scripts, manifests, hashes, and aggregate
results so anyone can regenerate every number above.
