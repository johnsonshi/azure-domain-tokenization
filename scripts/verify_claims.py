#!/usr/bin/env python3
"""Programmatic claim registry verifier (plan-2.md §4.2, §12).

Reads `publication/claims.yaml` and checks that every registered numeric claim's
frozen `display_value` still matches the authoritative result file it was
extracted from, within `tolerance`. No number may appear in the README, docs,
figures, tables, or paper unless it is registered here and passes this check.

Exit code 0 = all claims verified; non-zero = at least one mismatch/error.
Also emits `publication/claim_evidence.csv` with the resolved actual values.

Usage:
  uv run python scripts/verify_claims.py [--registry publication/claims.yaml] [--quiet]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import yaml


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / "plan.md").exists() and (p / "pyproject.toml").exists():
            return p
    return here.parents[1]


ROOT = _repo_root()


# --------------------------------------------------------------------------- #
# Extractors: each returns a float|int|bool from an authoritative result file.
# --------------------------------------------------------------------------- #
def _json_path(spec: dict):
    data = json.loads((ROOT / spec["file"]).read_text())
    cur = data
    for key in spec["path"]:
        cur = cur[key]
    return cur


def _csv_cell(spec: dict):
    import pandas as pd

    df = pd.read_csv(ROOT / spec["file"])
    for col, val in spec.get("match", {}).items():
        df = df[df[col].astype(str) == str(val)]
    if len(df) != 1:
        raise ValueError(f"csv_cell matched {len(df)} rows (expected 1): {spec}")
    return df.iloc[0][spec["column"]]


def _csv_reduction(spec: dict):
    """100 * (general - specialized) / general from two rows of a CSV."""
    import pandas as pd

    df = pd.read_csv(ROOT / spec["file"])
    es = df[df["eval_set"] == spec["eval_set"]]
    col = spec.get("column", "tokens_per_1000_utf8_bytes_micro")
    g = float(es[es["tokenizer_id"] == spec["general_id"]].iloc[0][col])
    a = float(es[es["tokenizer_id"] == spec["specialized_id"]].iloc[0][col])
    return 100.0 * (g - a) / g


def _parquet(spec: dict):
    import pandas as pd

    df = pd.read_parquet(ROOT / spec["file"])
    op = spec["op"]
    t = op["type"]
    if t == "row_count":
        return len(df)
    if t == "distinct_count":
        return int(df[op["column"]].nunique())
    if t == "sum":
        for col, val in op.get("where", {}).items():
            df = df[df[col] == val]
        return float(df[op["column"]].sum())
    if t == "roundtrip_all_ok":
        nz = df[df["utf8_bytes"] > 0]
        return bool(nz["roundtrip_ok"].all())
    if t == "reduction":
        sub = df[df["eval_set"] == op["eval_set"]]
        def micro(tok):
            r = sub[sub["tokenizer_id"] == tok]
            return 1000.0 * r["token_count"].sum() / r["utf8_bytes"].sum()
        g, a = micro(op["general_id"]), micro(op["azure_id"])
        return 100.0 * (g - a) / g
    raise ValueError(f"unknown parquet op {t}")


def _yaml_value(spec: dict):
    data = yaml.safe_load((ROOT / spec["file"]).read_text())
    cur = data
    for key in spec["path"]:
        cur = cur[key]
    return cur


EXTRACTORS = {
    "json_path": _json_path,
    "csv_cell": _csv_cell,
    "csv_reduction": _csv_reduction,
    "parquet": _parquet,
    "yaml_value": _yaml_value,
}


def extract(spec: dict):
    return EXTRACTORS[spec["kind"]](spec)


def verify(registry_path: Path, quiet: bool = False) -> int:
    reg = yaml.safe_load(registry_path.read_text())
    claims = reg["claims"]
    rows = []
    failures = 0
    for c in claims:
        cid = c["id"]
        try:
            actual = extract(c["extractor"])
        except Exception as exc:  # noqa: BLE001
            failures += 1
            rows.append({"id": cid, "status": "ERROR", "display": c.get("display_value"),
                         "actual": f"{type(exc).__name__}: {exc}", "source": c["extractor"].get("file", "")})
            if not quiet:
                print(f"  ✗ {cid}: EXTRACT ERROR {exc}")
            continue
        disp = c.get("display_value")
        tol = float(c.get("tolerance", 0.0))
        ok = True
        if isinstance(disp, bool) or isinstance(actual, bool):
            ok = bool(disp) == bool(actual)
        elif isinstance(disp, (int, float)) and isinstance(actual, (int, float)):
            ok = abs(float(actual) - float(disp)) <= tol
        else:
            ok = str(actual) == str(disp)
        if not ok:
            failures += 1
        rows.append({"id": cid, "status": "OK" if ok else "MISMATCH",
                     "display": disp, "actual": actual,
                     "tolerance": tol, "type": c.get("type"),
                     "source": c["extractor"].get("file", "")})
        if not quiet:
            mark = "✓" if ok else "✗"
            print(f"  {mark} {cid}: display={disp} actual={actual} (tol {tol}) [{c['extractor'].get('file','')}]")

    # Emit evidence CSV
    out = ROOT / "publication" / "claim_evidence.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "type", "status", "display", "actual", "tolerance", "source"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})

    total = len(claims)
    passed = total - failures
    print(f"\nCLAIM VERIFICATION: {passed}/{total} passed" + (f", {failures} FAILED" if failures else " — ALL OK"))
    print(f"Evidence written to {out.relative_to(ROOT)}")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="publication/claims.yaml")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    return verify(ROOT / args.registry, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
