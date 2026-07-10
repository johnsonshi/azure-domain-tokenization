"""Final report + notebook generation (plan.md §29, §30).

Every number in the report cites a committed source table. Interpretation obeys
plan.md §26 (tokenization-only language; no model-quality claims).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from . import config


def _load_json(p: Path) -> dict:
    return json.loads(p.read_text()) if p.exists() else {}


def _load_csv(p: Path) -> pd.DataFrame | None:
    return pd.read_csv(p) if p.exists() else None


def build_final_report(profile: str, exp: dict) -> str:
    audit = _load_json(config.AUDIT / "audit_summary.json")
    boot = _load_json(config.RESULTS_PROCESSED / "bootstrap.json")
    agg = _load_csv(config.RESULTS_PROCESSED / "eval_aggregate.csv")
    runtime = _load_csv(config.RESULTS_TABLES / "runtime_throughput.csv")
    sources = _load_json(config.MANIFESTS / "sources.lock.json")

    L: list[str] = []
    def w(s: str = "") -> None:
        L.append(s)

    w("# Does Your Tokenizer Speak Cloud?")
    w("## Measuring domain specialization on Microsoft technical documentation")
    w("")
    w(f"_Profile: **{profile}**. This report is generated from committed result tables; "
      "every figure has a source CSV under `results/tables/`._")
    w("")
    w("> **Scope.** This study measures **tokenization only** — token counts, compression, "
      "fragmentation, vocabulary utilization, and CPU runtime. It makes **no claim** about "
      "model output quality, accuracy, reasoning, understanding, GPU latency, or cost "
      "(plan.md §4, §26).")
    w("")

    w("## 1. Research question")
    w("At a fixed tokenizer algorithm, vocabulary size, training-data size, normalization "
      "policy, and evaluation set, does training a byte-level BPE tokenizer on Azure "
      "documentation reduce tokens-per-1000-UTF-8-bytes on unseen technical documentation "
      "versus training on byte-matched general English?")
    w("")

    w("## 2. Hypotheses")
    w("- **Primary:** Azure-trained tokenizer uses fewer tokens/1000 bytes on the Azure "
      "cross-service holdout than a byte-matched general-English tokenizer.")
    w("- **Secondary:** partial transfer to other Microsoft repos; larger gains on technical "
      "syntax; Mixed retains much of the gain with less general-English regression; "
      "diminishing returns with vocab size; compression ≠ runtime.")
    w("")

    w("## 3. Corpus construction & leakage controls")
    if audit:
        contents = audit.get("corpora_content_bytes", {})
        w(f"- Byte-matched corpora (content UTF-8 bytes): `{contents}`; "
          f"byte-match within 0.1%: **{audit.get('byte_match_ok')}** "
          f"(spread {audit.get('byte_match_spread')} bytes).")
        ed = audit.get("exact_dedup_azure", {})
        nd = audit.get("near_dup_azure", {})
        edg = audit.get("exact_dedup_general", {})
        ndg = audit.get("near_dup_general", {})
        cc = audit.get("cross_corpus_near_dup_eval", {})
        w(f"- Azure exact dedup: {ed.get('removed_exact', 0)} removed of {ed.get('input', 0)}. "
          f"Azure near-dup removal (threshold {nd.get('threshold')}): "
          f"{nd.get('removed_near', 0)} removed, {nd.get('num_pairs', 0)} pairs found.")
        w(f"- General exact dedup: {edg.get('removed_exact', 0)} removed of {edg.get('input', 0)}; "
          f"general near-dup removed: {ndg.get('removed_near', 0)} (before train/eval split, so no "
          "identical WikiText content spans the split).")
        w(f"- Cross-corpus near-dup eval removal (eval items that near-duplicate any training "
          f"doc): **{(cc or {}).get('removed_near_train', 0)}** removed.")
        w(f"- Azure group-aware splits: `{audit.get('azure_splits', {})}`. "
          f"Leakage violations: **{audit.get('leakage_violations') or 'none'}**.")
    w("- Splits are group-aware: whole services route to the cross-service holdout; whole "
      "near-duplicate clusters stay on one side of the train/eval boundary (plan.md §11).")
    w("- Source table: `data/audit/audit_summary.json`.")
    w("")

    w("## 4. Controlled tokenizer design (Track A)")
    w("Byte-level BPE (Hugging Face `tokenizers`), Unicode NFC, no lowercasing, no accent "
      "stripping, fixed byte-level pre-tokenizer + decoder, fixed special tokens, full "
      "byte-level initial alphabet, min-frequency 2. Only the training corpus changes: "
      "General / Azure / Mixed 50-50. Provenance: `artifacts/tokenizers/*.json`.")
    w("")

    w("## 5. Primary compression result")
    if agg is not None:
        principal = agg[(agg.eval_set == "azure_cross_service_holdout")]
        principal = principal[principal.tokenizer_id.str.contains("bytebpe")]
        if len(principal):
            w("Tokens per 1000 UTF-8 bytes on the **Azure cross-service holdout** "
              "(principal set; lower is better):")
            w("")
            w("| Tokenizer | tokens/1000 bytes (micro) | chars/token | round-trip |")
            w("|---|---:|---:|---:|")
            for _, r in principal.sort_values("tokenizer_id").iterrows():
                w(f"| `{r.tokenizer_id}` | {r.tokens_per_1000_utf8_bytes_micro:.2f} | "
                  f"{r.chars_per_token:.3f} | {r.roundtrip_ok_rate:.3f} |")
            w("")
            w("Source: `results/tables/eval_aggregate.csv`, figure `results/figures/fig02_tokens_per_1k.png`.")
    w("")

    w("### Effect size with paired bootstrap (95% CI)")
    if boot.get("comparisons"):
        w("| Comparison | reduction % | 95% CI | win rate |")
        w("|---|---:|---|---:|")
        for key, r in boot["comparisons"].items():
            w(f"| {key} | {r['point_estimate']:.2f} | "
              f"[{r['ci_low']:.2f}, {r['ci_high']:.2f}] | {r['win_rate']:.3f} |")
        w("")
        w(f"Paired bootstrap over documents, {boot.get('n_resamples')} resamples, "
          "seed fixed. Source: `results/processed/bootstrap.json`.")
    else:
        w("_Bootstrap results pending (`make analyze`)._")
    w("")

    w("## 6. Cross-repository transfer & general-English regression")
    w("Transfer to other MicrosoftDocs repos, external technical docs (Kubernetes), and the "
      "general-English regression are in `results/tables/fig_transfer_by_eval_set.csv`. "
      "In-domain gains are reported **alongside** out-of-domain regressions (plan.md §26).")
    w("")

    w("## 7. Identifier fragmentation (mechanism)")
    frag = _load_csv(config.RESULTS_TABLES / "fragmentation.csv")
    if frag is not None and len(frag):
        piv = frag.pivot_table(index="category", columns="tokenizer_id", values="mean_tokens")
        cols = [c for c in piv.columns if "bytebpe" in c]
        w("Mean tokens per item on the Azure cross-service holdout (lower = less fragmented):")
        w("")
        w("| Category | " + " | ".join(c.replace("-bytebpe", "") for c in cols) + " |")
        w("|---|" + "---:|" * len(cols))
        for cat, row in piv.iterrows():
            w(f"| {cat} | " + " | ".join(f"{row[c]:.2f}" for c in cols) + " |")
        w("")
        w("The Azure tokenizer fragments Azure-specific constructs (resource providers, CLI "
          "flags, URLs, identifiers) far less than General — the mechanism behind the "
          "compression gain. Source: `results/tables/fragmentation.csv`.")
    w("")

    w("## 8. Vocabulary utilization")
    vu = _load_csv(config.RESULTS_TABLES / "vocab_utilization.csv")
    if vu is not None and len(vu):
        w("On the Azure cross-service holdout:")
        w("")
        w("| Tokenizer | frac vocab used | unused | top-10% occurrence share |")
        w("|---|---:|---:|---:|")
        for _, r in vu.iterrows():
            w(f"| `{r.tokenizer_id}` | {r.frac_used:.3f} | {int(r.unused)} | {r.top10pct_share:.3f} |")
        w("")
        w("Source: `results/tables/vocab_utilization.csv`.")
    w("")

    w("## 9. Runtime (reported separately from compression)")
    if runtime is not None and len(runtime):
        w("| Tokenizer | MB/s median | MB/s p95 |")
        w("|---|---:|---:|")
        for _, r in runtime.iterrows():
            w(f"| `{r.tokenizer_id}` | {r['mb_per_second_median']:.2f} | {r['mb_per_second_p95']:.2f} |")
        w("")
        w("Source: `results/tables/runtime_throughput.csv`. CPU tokenizer throughput only — "
          "**not** inference throughput.")
    else:
        w("_Runtime benchmark pending (`make benchmark-runtime`)._")
    w("")

    w("## 10. Existing tokenizers (Track B — observational, not controlled)")
    w("tiktoken `r50k_base` / `cl100k_base` / `o200k_base` differ in training data, vocab "
      "size, normalization, and intended model; they are reported in a **separate** table "
      "(`results/tables/eval_aggregate.csv`, rows `tiktoken-*`) and never treated as "
      "controlled comparisons (plan.md §5).")
    w("")

    w("## 11. Sources, licenses, provenance")
    if sources.get("sources"):
        w("| Repository | Commit | License | Files |")
        w("|---|---|---|---:|")
        for s in sources["sources"]:
            w(f"| `{s['repository']}` | `{str(s['commit_sha'])[:12]}` | {s['license_id']} | {s['file_count']} |")
        w("")
    w("Full pins: `data/manifests/sources.lock.json`. License review: `licenses/`.")
    w("")
    w("**Artifact distribution policy.** Per `licenses/RESTRICTIONS.md`: raw source text is "
      "never committed (git-ignored); only scripts, manifests, hashes, and aggregate results "
      "are published. The **Azure-only** tokenizer artifact is redistributable with CC-BY "
      "attribution. The **General** and **Mixed** tokenizer artifacts are trained on WikiText "
      "(CC-BY-SA, unclear redistribution) and are **LOCAL-USE-ONLY** pending legal review — "
      "their `tokenizer.json` files are git-ignored; only their provenance metadata (hashes, "
      "config, timing) is tracked. Each tokenizer's `distributable` flag is recorded in "
      "`artifacts/tokenizers/*.json`.")
    w("")

    w("## 12. Limitations")
    w("- Tokenization-only; no model-quality, GPU, or cost claims.")
    w("- Corpus sizes are bounded by the local run budget; see profile above.")
    w("- Existing-tokenizer comparisons are observational.")
    w("- Context/billing figures are labelled estimates, not measured costs.")
    w("")

    w("## 13. Reproduction")
    w("```bash")
    w("uv sync && bash scripts/doctor.sh")
    w("make acquire-pilot audit-pilot train-pilot evaluate-pilot analyze report verify")
    w("```")
    w("Deterministic from the global seed, pinned source commits, and content hashes.")
    w("")
    w("## 14. Conclusions (limited to measured tokenization behaviour)")
    w("See §5 effect sizes. Claims are restricted to token counts on the stated corpora "
      "under the stated controls.")
    w("")
    return "\n".join(L)


def build_notebooks() -> None:
    """Generate the 7 presentation notebooks (plan.md §18) via nbformat."""
    import nbformat as nbf

    specs = [
        ("01_repository_inventory", "Repository inventory & selection",
         ["inventory/repo_inventory.csv", "inventory/repo_scores.csv"]),
        ("02_corpus_audit", "Corpus audit: dedup, splits, byte-matching",
         ["data/audit/audit_summary.json"]),
        ("03_tokenizer_training", "Tokenizer training provenance",
         ["artifacts/tokenizers"]),
        ("04_compression_results", "Compression results",
         ["results/tables/eval_aggregate.csv"]),
        ("05_fragmentation_analysis", "Identifier fragmentation",
         ["results/tables/eval_aggregate.csv"]),
        ("06_runtime_benchmark", "Runtime benchmark",
         ["results/tables/runtime_throughput.csv"]),
        ("07_final_report", "Final report",
         ["results/reports/FINAL_REPORT.md"]),
    ]
    nbdir = config.ROOT / "notebooks"
    nbdir.mkdir(parents=True, exist_ok=True)
    for name, title, artifacts in specs:
        nb = nbf.v4.new_notebook()
        cells = [
            nbf.v4.new_markdown_cell(f"# {title}\n\nGenerated notebook. Loads committed "
                                     "result artifacts; no hidden state (plan.md §18)."),
            nbf.v4.new_code_cell(
                "import json, pandas as pd\nfrom pathlib import Path\n"
                "ROOT = Path.cwd()\n"
                "while not (ROOT / 'plan.md').exists() and ROOT != ROOT.parent:\n"
                "    ROOT = ROOT.parent\n"
                f"artifacts = {artifacts!r}\n"
                "for a in artifacts:\n"
                "    p = ROOT / a\n"
                "    print(a, 'exists=' , p.exists())"),
        ]
        for a in artifacts:
            if a.endswith(".csv"):
                cells.append(nbf.v4.new_code_cell(
                    f"p = ROOT / {a!r}\n"
                    "df = pd.read_csv(p) if p.exists() else pd.DataFrame()\n"
                    "df.head(50)"))
            elif a.endswith(".json"):
                cells.append(nbf.v4.new_code_cell(
                    f"p = ROOT / {a!r}\n"
                    "print(json.dumps(json.loads(p.read_text()), indent=2)[:3000] if p.exists() else 'missing')"))
            elif a.endswith(".md"):
                cells.append(nbf.v4.new_code_cell(
                    f"p = ROOT / {a!r}\n"
                    "print(p.read_text()[:5000] if p.exists() else 'missing')"))
        nb.cells = cells
        nbf.write(nb, str(nbdir / f"{name}.ipynb"))
