#!/usr/bin/env python3
"""Assemble a clean arXiv source archive (plan-2.md §22). Does NOT submit.

Stages only the portable LaTeX sources + figures + bibliography (+ .bbl so arXiv
need not run BibTeX), excluding build caches, logs, and any corpora. Writes
paper/arxiv/arxiv-source.tar.gz and paper/arxiv/MANIFEST.md.
"""
from __future__ import annotations

import hashlib
import shutil
import tarfile
from pathlib import Path


def _root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / "plan.md").exists():
            return p
    return here.parents[1]


ROOT = _root()
PAPER = ROOT / "paper"
BUILD = PAPER / "arxiv" / "build"
STAGE = PAPER / "arxiv" / "source"
OUT = PAPER / "arxiv" / "arxiv-source.tar.gz"


def main() -> int:
    bbl = BUILD / "main.bbl"
    if not (PAPER / "main.tex").exists():
        raise SystemExit("paper/main.tex missing — run `make paper` first")
    if not bbl.exists():
        raise SystemExit("main.bbl missing — run `make paper` (bibtex) first")

    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    included: list[str] = []

    def add_file(src: Path, rel: str) -> None:
        dst = STAGE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        included.append(rel)

    add_file(PAPER / "main.tex", "main.tex")
    add_file(PAPER / "references.bib", "references.bib")
    add_file(bbl, "main.bbl")
    for sub in ("sections", "appendix", "tables"):
        for f in sorted((PAPER / sub).glob("*.tex")):
            add_file(f, f"{sub}/{f.name}")
    # Only the vector PDF figures actually referenced
    for f in sorted((PAPER / "figures").glob("*.pdf")):
        add_file(f, f"figures/{f.name}")

    # arXiv filename compliance: ASCII, no spaces/odd chars
    bad = [r for r in included if not all(ord(c) < 128 for c in r) or " " in r]
    if bad:
        raise SystemExit(f"non-portable filenames: {bad}")

    # Build the tarball deterministically
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with tarfile.open(OUT, "w:gz") as tar:
        for rel in sorted(included):
            tar.add(STAGE / rel, arcname=rel)

    sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
    lines = ["# arXiv source package manifest", "",
             f"Archive: `arxiv-source.tar.gz` (sha256 `{sha}`)",
             f"Files: {len(included)}", "",
             "Contents (portable LaTeX only; no corpora, no build caches, no logs):", ""]
    for rel in sorted(included):
        lines.append(f"- `{rel}`")
    lines += ["", "Excluded: raw corpora, `external/`, `data/`, build caches, logs, notebooks.",
              "The `.bbl` is included so arXiv need not run BibTeX.",
              "", "Do NOT submit without author metadata + explicit approval "
              "(`publication/AUTHOR_INPUTS_REQUIRED.md`)."]
    (PAPER / "arxiv" / "MANIFEST.md").write_text("\n".join(lines) + "\n")

    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes, {len(included)} files)")
    print(f"sha256 {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
