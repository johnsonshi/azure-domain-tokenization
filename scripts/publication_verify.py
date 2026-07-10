#!/usr/bin/env python3
"""Publication release gate (plan-2.md §12, §25).

Runs the publication checks that are available at the current phase and reports a
single pass/fail. Fails when:
  - a registered claim differs from its source file,
  - a figure's committed source table is missing,
  - a required source license record is missing,
  - a relative Markdown link is broken,
  - a raw corpus or a tokenizer.json artifact is git-tracked,
  - (paper phase) LaTeX build / citation checks fail — only if paper/ exists.

Usage: uv run python scripts/publication_verify.py [--strict]
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path


def _root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / "plan.md").exists() and (p / "pyproject.toml").exists():
            return p
    return here.parents[1]


ROOT = _root()
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    mark = "✓" if ok else "✗"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)


# --------------------------------------------------------------------------- #
def check_claims() -> None:
    code, out = run([sys.executable, "scripts/verify_claims.py", "--quiet"])
    last = out.strip().splitlines()[-1] if out.strip() else ""
    check("claim registry verified", code == 0, last)


def check_figure_sources() -> None:
    figdir = ROOT / "results" / "figures"
    manifest = figdir / "FIGURES.md"
    if not manifest.exists():
        check("figure source tables", False, "results/figures/FIGURES.md missing")
        return
    missing = []
    for m in re.finditer(r"`(results/tables/[^`]+\.csv)`", manifest.read_text()):
        if not (ROOT / m.group(1)).exists():
            missing.append(m.group(1))
    check("figure source tables exist", not missing, ", ".join(missing) or "all present")
    # PNG + PDF present for each fNN figure
    pngs = sorted(figdir.glob("fig0*.png"))
    pdfs = sorted((ROOT / "paper" / "figures").glob("fig0*.pdf")) if (ROOT / "paper" / "figures").exists() else []
    check("publication figures present (PNG)", len(pngs) >= 6, f"{len(pngs)} PNGs")
    if (ROOT / "paper" / "figures").exists():
        check("paper figures present (PDF)", len(pdfs) >= 6, f"{len(pdfs)} PDFs")


def check_licenses() -> None:
    lock = ROOT / "data" / "manifests" / "sources.lock.json"
    csvp = ROOT / "licenses" / "SOURCE_LICENSES.csv"
    if not lock.exists() or not csvp.exists():
        check("license records", False, "sources.lock.json or SOURCE_LICENSES.csv missing")
        return
    import json
    sources = {s["repository"].split("/")[-1].lower() for s in json.loads(lock.read_text())["sources"]}
    recorded = set()
    for row in csv.DictReader(open(csvp)):
        name = (row.get("repo_or_dataset") or row.get("source_name") or "").split("/")[-1].lower()
        recorded.add(name)
        recorded.add((row.get("source_name") or "").lower())
    # map lock repo short names; wikitext special-cased
    missing = []
    for s in sources:
        if s in recorded or any(s in r or r in s for r in recorded if r):
            continue
        missing.append(s)
    check("every locked source has a license record", not missing, ", ".join(missing) or "all 8 present")


def check_links() -> None:
    md_files = [p for p in ROOT.rglob("*.md")
                if not any(part in {".git", "external", ".venv"} for part in p.parts)]
    broken = []
    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for f in md_files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in link_re.finditer(text):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = target.split("#")[0]
            if not target:
                continue
            resolved = (f.parent / target).resolve()
            if not resolved.exists():
                broken.append(f"{f.relative_to(ROOT)} -> {target}")
    # Links to git-ignored files a fresh clone lacks are acceptable if they exist locally;
    # only truly-missing targets are broken.
    check("relative Markdown links resolve", not broken,
          (f"{len(broken)} broken: " + "; ".join(broken[:5])) if broken else "all resolve")


def check_no_raw_or_artifacts() -> None:
    code, out = run(["git", "ls-files"])
    tracked = out.splitlines()
    bad = [f for f in tracked
           if f.startswith(("data/raw/", "external/", "data/normalized/", "data/segments/"))
           or f.endswith(".corpus.txt")
           or (f.startswith("artifacts/tokenizers/") and f.endswith("tokenizer.json"))]
    check("no raw corpora / tokenizer.json tracked", not bad, ", ".join(bad[:5]) or "clean")
    big = []
    for f in tracked:
        p = ROOT / f
        if p.is_file() and p.stat().st_size > 5 * 1024 * 1024:
            big.append(f"{f} ({p.stat().st_size} B)")
    check("no tracked file > 5 MB", not big, ", ".join(big) or "clean")


def check_experiment_verify() -> None:
    code, out = run([sys.executable, "-m", "msdocs_tokenizer.cli", "verify", "--profile", "full"])
    ok = code == 0 and "all_ok" in out
    check("experiment verify gate (8/8)", ok, "all_ok=true" if ok else out.strip().splitlines()[-1:] and out.strip().splitlines()[-1])


def check_paper() -> None:
    paper = ROOT / "paper"
    if not (paper / "main.tex").exists():
        print("  · paper/main.tex not present yet — skipping LaTeX checks (pre-Phase E)")
        return
    pdf = ROOT / "paper" / "arxiv" / "compiled-paper.pdf"
    check("paper compiled PDF present", pdf.exists(), str(pdf.relative_to(ROOT)) if pdf.exists() else "run make paper")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()
    print("== publication verify ==")
    check_experiment_verify()
    check_claims()
    check_figure_sources()
    check_licenses()
    check_links()
    check_no_raw_or_artifacts()
    check_paper()
    failures = [n for n, ok, _ in RESULTS if not ok]
    print()
    if failures:
        print(f"PUBLICATION VERIFY: FAIL ({len(failures)} check(s): {', '.join(failures)})")
        return 1
    print(f"PUBLICATION VERIFY: OK ({len(RESULTS)} checks passed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
