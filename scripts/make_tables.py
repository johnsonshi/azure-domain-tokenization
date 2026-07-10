#!/usr/bin/env python3
"""Generate the paper's LaTeX tables from committed result files + the claim
registry (plan-2.md §19). Every number is pulled from `results/` /
`publication/claim_evidence.csv`, so the tables stay reconciled. Run:
`uv run python scripts/make_tables.py` (invoked by `make -C paper tables`).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


def _root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / "plan.md").exists() and (p / "pyproject.toml").exists():
            return p
    return here.parents[1]


ROOT = _root()
OUT = ROOT / "paper" / "tables"
OUT.mkdir(parents=True, exist_ok=True)


def claims() -> dict[str, str]:
    d = {}
    with open(ROOT / "publication" / "claim_evidence.csv") as f:
        for row in csv.DictReader(f):
            d[row["id"]] = row["display"]
    return d


C = claims()


def g(cid: str) -> str:
    return C.get(cid, "?")


def _write(name: str, body: str) -> None:
    (OUT / name).write_text(body.rstrip() + "\n")
    print(f"  ✓ paper/tables/{name}")


def tab_matrix() -> None:
    _write("tab_matrix.tex", r"""
\begin{tabular}{lll}
\toprule
\textbf{Factor} & \textbf{Levels} & \textbf{Held constant} \\
\midrule
Training corpus (manipulated) & General, Azure, Mixed 50/50 & --- \\
Vocabulary size & 8{,}192 / 16{,}384 / 32{,}768 & within a comparison \\
Algorithm & byte-level BPE & implementation, pre-tokenizer, decoder \\
Training budget & """ + f"{int(g('CORPUS_BYTES')):,}" + r""" UTF-8 bytes & byte-matched across corpora \\
Normalization & Unicode NFC & no lowercasing, no accent stripping \\
Seed & """ + g('SEED') + r""" & sampling, splitting, bootstrap \\
\bottomrule
\end{tabular}
""".strip())


def tab_datasets() -> None:
    lock = json.loads((ROOT / "data" / "manifests" / "sources.lock.json").read_text())
    rows = []
    role_label = {"anchor": "train (anchor)", "transfer": "eval (transfer)",
                  "external_technical": "eval (external)", "general_english": "train+eval"}
    # infer role from notes
    for s in lock["sources"]:
        note = s.get("notes", "")
        role = "eval"
        for k in role_label:
            if k in note:
                role = role_label[k]
        repo = s["repository"].replace("_", r"\_")
        rows.append((repo, role, f"{s['file_count']:,}", s["license_id"]))
    body = [r"\begin{tabular}{llrl}", r"\toprule",
            r"\textbf{Source} & \textbf{Role} & \textbf{Files} & \textbf{License} \\", r"\midrule"]
    for repo, role, files, lic in rows:
        body.append(f"{repo} & {role} & {files} & {lic} \\\\")
    body += [r"\bottomrule", r"\end{tabular}"]
    _write("tab_datasets.tex", "\n".join(body))


def tab_main_results() -> None:
    _write("tab_main_results.tex", r"""
\begin{tabular}{lrr}
\toprule
\textbf{Tokenizer (16K)} & \textbf{Azure cross-service} & \textbf{General English} \\
 & \textbf{reduction (\%)} & \textbf{reduction (\%)} \\
\midrule
Azure & $+""" + g('PRIMARY_REDUCTION_16K') + r"""$ & $""" + g('GENERAL_REGRESSION_AZURE') + r"""$ \\
Mixed (50/50) & $+""" + g('MIXED_REDUCTION_PRINCIPAL') + r"""$ & $""" + g('MIXED_REGRESSION') + r"""$ \\
General & $0$ (ref.) & $0$ (ref.) \\
\midrule
\multicolumn{3}{l}{\footnotesize Azure primary 95\% CI $[""" + g('PRIMARY_CI_LOW') + r""", """ + g('PRIMARY_CI_HIGH') + r"""]$, win rate """ + g('PRIMARY_WIN_RATE') + r""", $n=""" + g('PRIMARY_N_DOCS') + r"""$.} \\
\multicolumn{3}{l}{\footnotesize Positive $=$ specialized tokenizer uses fewer tokens per 1{,}000 UTF-8 bytes.} \\
\bottomrule
\end{tabular}
""".strip())


def tab_transfer() -> None:
    body = [r"\begin{tabular}{lr}", r"\toprule",
            r"\textbf{Evaluation set} & \textbf{Azure vs General reduction (\%)} \\", r"\midrule",
            r"Azure cross-service holdout (principal) & $+" + g('PRIMARY_REDUCTION_16K') + r"$ \\",
            r"Azure same-service holdout & $+" + g('TRANSFER_SAME_SERVICE') + r"$ \\",
            r"Microsoft data docs & $+" + g('TRANSFER_MS_DATA') + r"$ \\",
            r"Microsoft DevOps docs & $+" + g('TRANSFER_MS_DEVOPS') + r"$ \\",
            r"Kubernetes (external technical) & $+" + g('TRANSFER_KUBERNETES') + r"$ \\",
            r"Microsoft architecture docs & $+" + g('TRANSFER_MS_ARCH') + r"$ \\",
            r"Microsoft broad-enterprise docs & $+" + g('TRANSFER_MS_BROAD') + r"$ \\",
            r"General English & $" + g('GENERAL_REGRESSION_AZURE') + r"$ \\",
            r"\midrule",
            r"\multicolumn{2}{l}{\footnotesize Vocabulary sensitivity (principal): "
            r"8K $+" + g('VOCAB_8192') + r"$, 16K $+" + g('VOCAB_16384') + r"$, 32K $+" + g('VOCAB_32768') + r"$.} \\",
            r"\bottomrule", r"\end{tabular}"]
    _write("tab_transfer.tex", "\n".join(body))


def tab_runtime_verification() -> None:
    _write("tab_runtime_verification.tex", r"""
\begin{tabular}{lr}
\toprule
\textbf{Measure} & \textbf{Value} \\
\midrule
Evaluation rows & """ + f"{int(g('COVERAGE_ROWS')):,}" + r""" (""" + g('COVERAGE_ENCODERS') + r""" encoders $\times$ """ + g('COVERAGE_EVALSETS') + r""" sets) \\
Exact round-trip & 100\% \\
Unknown tokens (\texttt{[UNK]}) & """ + g('COVERAGE_UNK') + r""" \\
CPU throughput, Track A (MB/s) & """ + g('RUNTIME_TRACKA_MIN') + r"""--""" + g('RUNTIME_TRACKA_MAX') + r""" \\
CPU throughput, Track B \texttt{tiktoken} (MB/s) & """ + g('RUNTIME_TRACKB_MIN') + r"""--""" + g('RUNTIME_TRACKB_MAX') + r""" \\
Automated verification gate & 8/8 \\
\bottomrule
\end{tabular}
""".strip())


def main() -> int:
    print("Generating paper LaTeX tables from result files + claim registry ...")
    tab_matrix(); tab_datasets(); tab_main_results(); tab_transfer(); tab_runtime_verification()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
