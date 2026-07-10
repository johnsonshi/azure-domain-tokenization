# Licensing restrictions and redistribution policy

This is not legal advice. It is a conservative licensing gate for the CPU-only tokenizer-efficiency study.

## Raw corpora policy

**NO-GO: do not commit raw text for any corpus.** Even where licenses permit redistribution with attribution, the repository policy is to keep raw corpora out of git and publish acquisition scripts, manifests, hashes, and aggregate results instead.

Per-source raw text status:

- `azure-docs`: license permits redistribution under CC-BY-4.0 with attribution; project policy still forbids committing raw text.
- `architecture-center`: license permits redistribution under CC-BY-4.0 with attribution; project policy still forbids committing raw text.
- `azure-devops-docs`: license permits redistribution under CC-BY-4.0 with attribution; project policy still forbids committing raw text.
- `sql-docs`: license permits redistribution under CC-BY-4.0 with attribution; project policy still forbids committing raw text.
- `powershell-docs`: NOASSERTION resolved to CC-BY-4.0 documentation and MIT code; project policy still forbids committing raw text.
- `kubernetes-website`: license permits redistribution under CC-BY-4.0 with attribution; project policy still forbids committing raw text.
- `wikitext-103`: **VETO raw redistribution** in this project. It is Wikipedia-derived, the Hugging Face metadata and card text disagree between CC-BY-SA/GFDL and CC-BY-SA-4.0 wording, and article-level attribution/history obligations are not satisfied by the current manifest.

## Tokenizer artifacts

Artifacts may include vocabulary entries, merge rules, normalization metadata, or special-token tables. Treat them as potentially derived from the training corpus until legal confirms otherwise.

- **GO with attribution:** tokenizer artifacts trained solely from CC-BY-4.0 documentation sources (`azure-docs`, other MicrosoftDocs sources if used for training, and/or `kubernetes-website`) may be distributed if the release includes the attribution text in `licenses/ATTRIBUTION.md`, license links, modification notices, and no trademark endorsement.
- **GO for tooling libraries:** `huggingface/tokenizers` is Apache-2.0. `openai/tiktoken` source is MIT; however, this review did not locate a separate license for downloaded OpenAI public encoding blob data, so do not redistribute cached `.tiktoken`/GPT-2 encoding files outside normal package use without confirmation.
- **VETO / LOCAL-USE-ONLY:** tokenizer artifacts trained on `wikitext-103` alone, or on a mixed corpus that includes `wikitext-103`, must not be redistributed unless legal confirms (1) the applicable CC-BY-SA/GFDL version, (2) that the tokenizer artifact can be released under compatible share-alike terms, and (3) adequate Wikipedia article/contributor/history attribution can be provided.

## Share-alike implications for WikiText and mixed-corpus tokenizers

WikiText is derived from Wikipedia and is labeled on Hugging Face as `cc-by-sa-3.0` plus `gfdl`, while the card text also says CC BY-SA 4.0. CC BY-SA requires attribution and generally requires adaptations to be shared under the same or a compatible license. If a tokenizer vocabulary/merge table is considered adapted material or a database extraction from WikiText, a mixed-corpus tokenizer could inherit share-alike obligations that are incompatible with a permissive or proprietary artifact release. Because the study does not preserve article-level source attribution and because license-version evidence is inconsistent, this reviewer vetoes redistribution of WikiText-derived or mixed-with-WikiText tokenizer artifacts.

## Final recommendations

1. **Committing raw text:** **NO-GO for all sources.** Keep raw text ignored/untracked; publish reproducible acquisition scripts, source manifests, pinned commits/revisions, and hashes.
2. **Distributing tokenizer artifacts:** **GO** only for artifacts trained exclusively on CC-BY-4.0 sources with attribution. **NO-GO/VETO** for WikiText-only or mixed-with-WikiText artifacts pending legal review. **UNCLEAR** for separate redistribution of tiktoken cached encoding blobs because no standalone blob license text was located.
3. **Publishing scripts, manifests, hashes, and aggregate results:** **GO.** This is the preferred publication path for all corpora and the only approved path for WikiText in this review.

## License evidence read

- MicrosoftDocs/azure-docs: `LICENSE`, `LICENSE-CODE`, `ThirdPartyNotices.md` at commit 80e8be2fca4160d1ff2528ae84bbf96f4a90d46e.
- MicrosoftDocs/architecture-center: `LICENSE`, `LICENSE-CODE` at commit 9bb6e65cf6b109039e966e27aad44ce71ab4120b; no root notice found.
- MicrosoftDocs/azure-devops-docs: `LICENSE`, `LICENSE-CODE` at commit 83e590364fe13aab331d166cab63b5cbea0b35ab; no root notice found.
- MicrosoftDocs/sql-docs: `LICENSE`, `LICENSE-CODE` at commit b1212537b039d992f1acafa81747239794ff32a1; no root notice found.
- MicrosoftDocs/PowerShell-Docs: `LICENSE.md`, `LICENSE-CODE.md`, `ThirdPartyNotices.md` at commit 99a350b144ef809f844e0f48d09f0cd9c9f2bd4b.
- kubernetes/website: `LICENSE` and `README.md` at commit 71d23f81e3479361befc94564e2b955860c03164; no root notice found.
- Salesforce/wikitext: Hugging Face README/dataset card at revision b08601e04326c79dfdd32d625aee71d232d685c3.
- openai/tiktoken: `LICENSE`, `README.md`, `tiktoken_ext/openai_public.py` at commit 08a5f3b2c987ada4fc5aa1f16c643c203fa8acaa.
- huggingface/tokenizers: `LICENSE` at commit 05741122105911e14dbe307c8f640c757fa97779; no root NOTICE found.

## Provenance note: WikiText revision pinning (added during publication audit)

`data/manifests/sources.lock.json` records the general-English source as
`Salesforce/wikitext` at `commit_sha: hf:main` because acquisition fetched the
`wikitext-103-raw-v1` parquet from the dataset's `main` branch at acquisition
time (2026-07-10). The licensing review resolved the dataset **README** to
revision `b08601e04326c79dfdd32d625aee71d232d685c3`.

For exact reproduction, pin the Hugging Face dataset revision explicitly
(`hf_hub_download(..., revision="<sha>")`). This provenance note does not alter
the frozen experiment; it documents the pin. WikiText redistribution and any
WikiText-derived (General/Mixed) tokenizer-artifact redistribution remain
**VETOED / local-use-only** pending legal review of the exact license version
(the HF card lists CC-BY-SA-3.0 + GFDL metadata and CC-BY-SA-4.0 in prose).

## Note: PowerShell-Docs reviewed but not selected

`licenses/SOURCE_LICENSES.csv` and `licenses/ATTRIBUTION.md` retain a
`MicrosoftDocs/PowerShell-Docs` (CC-BY-4.0) entry from the discovery phase. It
was **reviewed but is NOT one of the 8 final locked sources** in
`data/manifests/sources.lock.json` (fabric-docs + microsoft-365-docs were
selected instead). The entry is kept for provenance; it does not affect any
published artifact.
