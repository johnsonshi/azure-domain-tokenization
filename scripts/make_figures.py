#!/usr/bin/env python3
"""Publication figure generation (plan-2.md §10, §19).

Regenerates every public/paper figure deterministically from committed source
tables in results/. Each figure writes:
  - a source CSV under results/tables/ (so the figure has a committed source table),
  - a PNG under results/figures/ (for the README),
  - a vector PDF under paper/figures/ (for the manuscript),
and an entry in results/figures/FIGURES.md (caption + alt text + source table).

Palette is the colorblind-safe Okabe-Ito set. No 3D, no dual axes, no misleading
truncated axes. Run: `uv run python scripts/make_figures.py` (`make figures`).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / "plan.md").exists() and (p / "pyproject.toml").exists():
            return p
    return here.parents[1]


ROOT = _root()
FIG_PNG = ROOT / "results" / "figures"
FIG_PDF = ROOT / "paper" / "figures"
TABLES = ROOT / "results" / "tables"
PROC = ROOT / "results" / "processed"
for d in (FIG_PNG, FIG_PDF, TABLES):
    d.mkdir(parents=True, exist_ok=True)

# Okabe-Ito colorblind-safe palette
C_GENERAL = "#E69F00"   # orange
C_AZURE = "#0072B2"     # blue
C_MIXED = "#009E73"     # bluish green
C_NEUTRAL = "#555555"
C_TRACKB = "#CC79A7"    # reddish purple

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 120,
    "font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6,
    "figure.autolayout": True, "savefig.bbox": "tight",
    "pdf.fonttype": 42, "ps.fonttype": 42,  # embed TrueType for arXiv
})

_MANIFEST: list[dict] = []


def _save(fig, name: str, caption: str, alt: str, source_table: str) -> None:
    # Deterministic outputs: strip the wall-clock CreationDate so regenerating a
    # figure yields byte-identical files (no spurious git diffs).
    fig.savefig(FIG_PNG / f"{name}.png", metadata={"Software": "msdocs-tokenizer"})
    fig.savefig(FIG_PDF / f"{name}.pdf",
                metadata={"CreationDate": None, "Creator": "msdocs-tokenizer",
                          "Producer": "matplotlib"})
    plt.close(fig)
    _MANIFEST.append({"figure": name, "source_table": source_table, "caption": caption, "alt": alt})
    print(f"  ✓ {name}.png / .pdf  (source: {source_table})")


def _agg() -> pd.DataFrame:
    return pd.read_csv(PROC / "eval_aggregate.csv")


def _boot() -> dict:
    return json.loads((PROC / "bootstrap.json").read_text())


def _micro(agg, tok, es):
    r = agg[(agg.tokenizer_id == tok) & (agg.eval_set == es)]
    return float(r.iloc[0].tokens_per_1000_utf8_bytes_micro)


# --------------------------------------------------------------------------- #
def fig01_primary():
    """Primary Azure cross-service reduction with 95% CI (by vocab size)."""
    b = _boot()
    rows = []
    for v in (8192, 16384, 32768):
        c = b["comparisons"][f"azure_vs_general:{v}:azure_cross_service_holdout"]
        rows.append({"vocab": v, "reduction_pct": c["point_estimate"],
                     "ci_low": c["ci_low"], "ci_high": c["ci_high"]})
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "fig01_primary_reduction.csv", index=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    x = range(len(df))
    yerr = [df.reduction_pct - df.ci_low, df.ci_high - df.reduction_pct]
    ax.bar(x, df.reduction_pct, color=C_AZURE, width=0.55,
           yerr=yerr, capsize=5, error_kw={"ecolor": C_NEUTRAL, "elinewidth": 1.2})
    ax.set_xticks(list(x)); ax.set_xticklabels([f"{v//1024}K" for v in df.vocab])
    ax.set_xlabel("vocabulary size"); ax.set_ylabel("token reduction (%), higher = better")
    ax.set_title("Azure vs General: reduction on cross-service holdout")
    ax.axhline(0, color=C_NEUTRAL, lw=0.8)
    for xi, r in zip(x, df.reduction_pct):
        ax.text(xi, r + 0.6, f"{r:.1f}%", ha="center", fontsize=9)
    _save(fig, "fig01_primary",
          "Relative token reduction (%) of the Azure-trained vs byte-matched General "
          "tokenizer on the Azure cross-service holdout, by vocabulary size. Error bars "
          "are 95% paired-bootstrap CIs over documents. Higher is better.",
          "Bar chart of token reduction percent at 8K, 16K, 32K vocabularies, all near "
          "36 percent with tight confidence intervals.",
          "results/tables/fig01_primary_reduction.csv")


def fig02_tradeoff():
    """Azure gain vs general-English regression for General/Azure/Mixed."""
    agg = _agg()
    rows = []
    for tok, name in [("general-bytebpe-16384", "General"),
                      ("azure-bytebpe-16384", "Azure"),
                      ("mixed-bytebpe-16384", "Mixed")]:
        g_az = _micro(agg, "general-bytebpe-16384", "azure_cross_service_holdout")
        g_en = _micro(agg, "general-bytebpe-16384", "general_english")
        az = 100 * (g_az - _micro(agg, tok, "azure_cross_service_holdout")) / g_az
        en = 100 * (g_en - _micro(agg, tok, "general_english")) / g_en
        rows.append({"tokenizer": name, "azure_holdout_pct": az, "general_english_pct": en})
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "fig02_tradeoff.csv", index=False)
    fig, ax = plt.subplots(figsize=(6, 4.2))
    colors = {"General": C_GENERAL, "Azure": C_AZURE, "Mixed": C_MIXED}
    for _, r in df.iterrows():
        ax.scatter(r.general_english_pct, r.azure_holdout_pct, s=120,
                   color=colors[r.tokenizer], zorder=3, label=r.tokenizer)
        ax.annotate(r.tokenizer, (r.general_english_pct, r.azure_holdout_pct),
                    textcoords="offset points", xytext=(8, 4), fontsize=10)
    ax.axhline(0, color=C_NEUTRAL, lw=0.8); ax.axvline(0, color=C_NEUTRAL, lw=0.8)
    ax.set_xlabel("general-English reduction (%) vs General\n(negative = regression)")
    ax.set_ylabel("Azure holdout reduction (%) vs General")
    ax.set_title("Specialization–generalization tradeoff (16K)")
    _save(fig, "fig02_tradeoff",
          "Token reduction (%) relative to the General tokenizer on the Azure cross-"
          "service holdout (y) vs held-out general English (x), for General, Azure, and "
          "Mixed (16K). Up and left is more Azure gain; right is less English regression.",
          "Scatter plot showing Azure tokenizer high on Azure gain but far left (large "
          "English regression), Mixed high on Azure gain and near zero English regression, "
          "General at the origin.",
          "results/tables/fig02_tradeoff.csv")


def fig03_transfer():
    """Transfer across evaluation sets (Azure vs General, 16K)."""
    b = _boot()
    order = [("azure_cross_service_holdout", "Azure cross-service"),
             ("azure_same_service_holdout", "Azure same-service"),
             ("ms_data", "MS data"), ("ms_devops", "MS DevOps"),
             ("external_technical", "Kubernetes (external)"),
             ("ms_architecture", "MS architecture"),
             ("ms_broad_enterprise", "MS broad enterprise"),
             ("general_english", "General English")]
    rows = []
    for k, label in order:
        v = b["by_eval_set"][k]
        rows.append({"eval_set": k, "label": label, "reduction_pct": v["point_estimate"],
                     "ci_low": v["ci_low"], "ci_high": v["ci_high"]})
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "fig03_transfer.csv", index=False)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    y = range(len(df))[::-1]
    colors = [C_AZURE if r > 0 else C_GENERAL for r in df.reduction_pct]
    xerr = [df.reduction_pct - df.ci_low, df.ci_high - df.reduction_pct]
    ax.barh(list(y), df.reduction_pct, color=colors, height=0.6,
            xerr=xerr, capsize=3, error_kw={"ecolor": C_NEUTRAL, "elinewidth": 1})
    ax.set_yticks(list(y)); ax.set_yticklabels(df.label)
    ax.set_xlabel("token reduction (%) vs General, 16K  (negative = regression)")
    ax.set_title("Cross-domain transfer and general-English regression")
    ax.axvline(0, color=C_NEUTRAL, lw=0.8)
    _save(fig, "fig03_transfer",
          "Relative token reduction (%) of Azure vs General (16K) across evaluation sets, "
          "with 95% paired-bootstrap CIs. Positive = Azure uses fewer tokens; the general-"
          "English bar is negative (regression).",
          "Horizontal bar chart: positive reductions 26-36 percent for Azure and Microsoft "
          "and Kubernetes docs; negative about -35 percent for general English.",
          "results/tables/fig03_transfer.csv")


def fig04_vocab():
    """Vocabulary-size sensitivity."""
    df = pd.read_csv(TABLES / "fig_relative_reduction_by_vocab.csv")
    df = df.sort_values("vocab")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df.vocab, df.relative_token_reduction_pct, "o-", color=C_AZURE, lw=2, ms=8)
    for _, r in df.iterrows():
        ax.annotate(f"{r.relative_token_reduction_pct:.1f}%", (r.vocab, r.relative_token_reduction_pct),
                    textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    ax.set_xscale("log", base=2); ax.set_xticks(df.vocab)
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v//1024)}K"))
    ax.set_xlabel("vocabulary size (log2)"); ax.set_ylabel("token reduction (%) vs General")
    ax.set_title("Vocabulary-size sensitivity (cross-service holdout)")
    _save(fig, "fig04_vocab",
          "Azure vs General token reduction (%) on the cross-service holdout across 8K/16K/"
          "32K vocabularies. The reduction is stable near 36%, indicating corpus composition "
          "dominated over the tested vocabulary range.",
          "Line chart of reduction percent versus vocabulary size, roughly flat between 35 "
          "and 37 percent.",
          "results/tables/fig_relative_reduction_by_vocab.csv")


def fig05_content():
    """Content-type breakdown on the principal holdout."""
    b = _boot()
    rows = []
    for ct in ("prose", "heading", "table", "inline_code"):
        v = b["by_content_type"][ct]
        rows.append({"content_type": ct, "reduction_pct": v["point_estimate"],
                     "ci_low": v["ci_low"], "ci_high": v["ci_high"], "n": v["n_documents"]})
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "fig05_content.csv", index=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    x = range(len(df))
    yerr = [df.reduction_pct - df.ci_low, df.ci_high - df.reduction_pct]
    ax.bar(x, df.reduction_pct, color=C_AZURE, width=0.6, yerr=yerr, capsize=4,
           error_kw={"ecolor": C_NEUTRAL, "elinewidth": 1})
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{r.content_type}\n(n={r.n})" for _, r in df.iterrows()])
    ax.set_ylabel("token reduction (%) vs General, 16K")
    ax.set_title("Reduction by content type (cross-service holdout)")
    ax.axhline(0, color=C_NEUTRAL, lw=0.8)
    _save(fig, "fig05_content",
          "Azure vs General reduction (%) by dominant content type on the cross-service "
          "holdout, with 95% paired-bootstrap CIs and per-stratum document counts. The prose "
          "stratum (n=900) still shows a large reduction, so the effect is not only code/markup.",
          "Bar chart with prose, heading, table, inline code all showing positive reductions "
          "between 33 and 44 percent; prose has the largest sample.",
          "results/tables/fig05_content.csv")


def fig06_runtime():
    """Compression vs CPU throughput (separate axes conceptually, single scatter)."""
    agg = _agg()
    rt = pd.read_csv(TABLES / "runtime_throughput.csv")
    rows = []
    for _, r in rt.iterrows():
        tok = r.tokenizer_id
        es = "azure_cross_service_holdout"
        sub = agg[(agg.tokenizer_id == tok) & (agg.eval_set == es)]
        if not len(sub):
            continue
        rows.append({"tokenizer_id": tok,
                     "tokens_per_1000_bytes": float(sub.iloc[0].tokens_per_1000_utf8_bytes_micro),
                     "mb_per_second_median": r.mb_per_second_median,
                     "track": "A (controlled)" if "bytebpe" in tok else "B (tiktoken, observational)"})
    df = pd.DataFrame(rows)
    df.to_csv(TABLES / "fig06_runtime.csv", index=False)
    # Also a runtime summary table for claim registration
    rt2 = rt.copy(); rt2["track"] = ["A" if "bytebpe" in t else "B" for t in rt2.tokenizer_id]
    summ = rt2.groupby("track")["mb_per_second_median"].agg(["min", "max"]).reset_index()
    summ.to_csv(TABLES / "runtime_summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    for track, color, marker in [("A (controlled)", C_AZURE, "o"), ("B (tiktoken, observational)", C_TRACKB, "s")]:
        d = df[df.track == track]
        ax.scatter(d.mb_per_second_median, d.tokens_per_1000_bytes, s=90, color=color,
                   marker=marker, label=track, zorder=3)
    ax.set_xlabel("CPU tokenizer throughput (MB/s, median) — not model serving")
    ax.set_ylabel("tokens / 1000 UTF-8 bytes\n(lower = more compression)")
    ax.set_title("Compression vs CPU throughput (cross-service holdout)")
    ax.legend(fontsize=8, loc="best")
    _save(fig, "fig06_runtime",
          "Compression (tokens per 1000 UTF-8 bytes, lower is better) vs measured CPU "
          "tokenizer throughput (MB/s) on the cross-service holdout. Track A are the "
          "controlled tokenizers; Track B (tiktoken) are observational baselines. CPU "
          "throughput is not model-serving throughput.",
          "Scatter plot: Track A tokenizers cluster at higher compression but lower MB/s; "
          "Track B tiktoken at lower compression but higher MB/s.",
          "results/tables/fig06_runtime.csv")


def main() -> int:
    print("Generating publication figures from committed source tables ...")
    fig01_primary(); fig02_tradeoff(); fig03_transfer(); fig04_vocab(); fig05_content(); fig06_runtime()
    # Write manifest
    lines = ["# Figures manifest", "",
             "Generated by `scripts/make_figures.py` from committed source tables. "
             "Each figure has a PNG (`results/figures/`), a vector PDF (`paper/figures/`), "
             "and a source CSV.", "",
             "| Figure | Source table | Caption |", "|---|---|---|"]
    for m in _MANIFEST:
        lines.append(f"| `{m['figure']}` | `{m['source_table']}` | {m['caption']} |")
    lines += ["", "## Alt text", ""]
    for m in _MANIFEST:
        lines.append(f"- **{m['figure']}**: {m['alt']}")
    (FIG_PNG / "FIGURES.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote {len(_MANIFEST)} figures + results/figures/FIGURES.md")
    return 0


if __name__ == "__main__":
    import matplotlib.ticker  # noqa: F401 (used in fig04)
    raise SystemExit(main())
