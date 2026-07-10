"""Resumable pipeline stages (plan.md §22).

Every stage is safe to re-run: it records a content hash of its declared inputs
+ parameters and skips recomputation when nothing changed and outputs exist.
Stale downstream artifacts are detected by input-hash mismatch.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import config
from .provenance import atomic_write_json, git_commit, sha256_file, sha256_text


def _hash_inputs(input_files: list[str | Path], params: dict) -> str:
    parts = [f"params:{json.dumps(params, sort_keys=True, default=str)}"]
    for f in sorted(str(p) for p in input_files):
        p = Path(f)
        parts.append(f"file:{f}:{sha256_file(p) if p.exists() else 'MISSING'}")
    return sha256_text("\n".join(parts))


@dataclass
class StageResult:
    name: str
    skipped: bool
    input_hash: str
    outputs: list[str]
    seconds: float


def stage(
    name: str,
    input_files: list[str | Path],
    output_files: list[str | Path],
    params: dict,
    fn: Callable[[], None],
    force: bool = False,
    marker_dir: Path | None = None,
) -> StageResult:
    """Run ``fn`` unless a completed marker matches current inputs & outputs exist.

    ``fn`` must (re)create every path in ``output_files``.
    """
    marker_dir = marker_dir or (config.DATA / ".stages")
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker = marker_dir / f"{name}.done.json"

    input_hash = _hash_inputs(input_files, params)
    outputs_exist = all(Path(o).exists() for o in output_files)

    if not force and marker.exists() and outputs_exist:
        prev = json.loads(marker.read_text())
        if prev.get("input_hash") == input_hash:
            return StageResult(name, skipped=True, input_hash=input_hash,
                               outputs=[str(o) for o in output_files], seconds=0.0)

    t0 = time.perf_counter()
    fn()
    dt = time.perf_counter() - t0

    missing = [str(o) for o in output_files if not Path(o).exists()]
    if missing:
        raise RuntimeError(f"stage {name!r} did not produce outputs: {missing}")

    atomic_write_json(marker, {
        "name": name,
        "input_hash": input_hash,
        "outputs": [str(o) for o in output_files],
        "git_commit": git_commit(),
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "seconds": round(dt, 3),
    })
    return StageResult(name, skipped=False, input_hash=input_hash,
                       outputs=[str(o) for o in output_files], seconds=dt)


def stage_is_complete(name: str, marker_dir: Path | None = None) -> bool:
    marker_dir = marker_dir or (config.DATA / ".stages")
    return (marker_dir / f"{name}.done.json").exists()
