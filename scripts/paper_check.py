#!/usr/bin/env python3
"""Paper checks (plan-2.md §12 `paper-check`): undefined citations/references,
unresolved cite keys, missing figures, and claim reconciliation. Run from repo
root or paper/. Exit nonzero on any failure.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def _root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / "plan.md").exists():
            return p
    return here.parents[1]


ROOT = _root()
PAPER = ROOT / "paper"
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'✓' if ok else '✗'} {name}" + (f" — {detail}" if detail else ""))


def main() -> int:
    log = PAPER / "arxiv" / "build" / "main.log"
    if log.exists():
        text = log.read_text(errors="ignore")
        undef = len(re.findall(r"Citation .* undefined", text)) + \
                len(re.findall(r"Reference .* undefined", text))
        check("no undefined citations/references in build log", undef == 0, f"{undef} undefined")
        check("no LaTeX errors in build log", "! LaTeX Error" not in text and "! Undefined control" not in text)
    else:
        check("paper build log present (run make paper)", False, "arxiv/build/main.log missing")

    # cite keys resolve to bib entries
    bib = (PAPER / "references.bib").read_text() if (PAPER / "references.bib").exists() else ""
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    used = set()
    for tex in (PAPER / "sections").glob("*.tex"):
        for m in re.finditer(r"\\cite[pt]?\{([^}]+)\}", tex.read_text()):
            used |= {k.strip() for k in m.group(1).split(",")}
    missing = sorted(used - bib_keys)
    check("all cited keys resolve in references.bib", not missing, ", ".join(missing) or f"{len(used)} keys OK")

    # figures referenced exist
    fig_missing = []
    for tex in (PAPER / "sections").glob("*.tex"):
        for m in re.finditer(r"\\includegraphics\[[^\]]*\]\{([^}]+)\}", tex.read_text()):
            name = m.group(1)
            if not (PAPER / "figures" / name).exists() and not (PAPER / name).exists():
                fig_missing.append(name)
    check("all included figures exist", not fig_missing, ", ".join(fig_missing) or "all present")

    # compiled PDF present
    check("compiled PDF present", (PAPER / "arxiv" / "compiled-paper.pdf").exists()
          or (PAPER / "arxiv" / "build" / "main.pdf").exists())

    # claim registry still reconciles (paper numbers come from it)
    code = subprocess.run([sys.executable, "scripts/verify_claims.py", "--quiet"],
                          cwd=ROOT, capture_output=True, text=True).returncode
    check("claim registry reconciles", code == 0)

    fails = [n for n, ok, _ in RESULTS if not ok]
    print()
    if fails:
        print(f"PAPER CHECK: FAIL ({', '.join(fails)})")
        return 1
    print(f"PAPER CHECK: OK ({len(RESULTS)} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
