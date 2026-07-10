"""Provenance, hashing, machine metadata, and atomic/locked writes.

Everything that must be reproducible or auditable funnels through here so that
hashing and machine-metadata capture are identical everywhere.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Iterator

from . import config

# --------------------------------------------------------------------------- #
# Hashing
# --------------------------------------------------------------------------- #
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# Atomic + locked writes (plan.md §22: atomic writes, lock shared outputs)
# --------------------------------------------------------------------------- #
def atomic_write_bytes(path: str | Path, data: bytes) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
    return path


def atomic_write_text(path: str | Path, text: str) -> Path:
    return atomic_write_bytes(path, text.encode("utf-8"))


def atomic_write_json(path: str | Path, obj: Any, *, indent: int = 2, sort_keys: bool = True) -> Path:
    return atomic_write_text(path, json.dumps(obj, indent=indent, sort_keys=sort_keys, ensure_ascii=False) + "\n")


@contextlib.contextmanager
def file_lock(target: str | Path, timeout: float = 120.0, poll: float = 0.1) -> Iterator[None]:
    """Simple cross-process advisory lock via O_CREAT|O_EXCL lockfile.

    Serializes writes to shared state files (plan.md §19 parallelism rules).
    """
    lock = Path(str(target) + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                raise TimeoutError(f"Could not acquire lock {lock} within {timeout}s")
            time.sleep(poll)
    try:
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(lock)


# --------------------------------------------------------------------------- #
# Machine metadata + package versions
# --------------------------------------------------------------------------- #
_TRACKED_PACKAGES = (
    "tokenizers",
    "tiktoken",
    "numpy",
    "pandas",
    "pyarrow",
    "pydantic",
    "datasketch",
    "scipy",
    "matplotlib",
)


def package_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in _TRACKED_PACKAGES:
        try:
            out[name] = importlib_metadata.version(name)
        except importlib_metadata.PackageNotFoundError:
            out[name] = "not-installed"
    return out


def _sysctl(key: str) -> str | None:
    try:
        return subprocess.check_output(["sysctl", "-n", key], text=True).strip()
    except Exception:
        return None


def machine_metadata() -> dict[str, Any]:
    mem_bytes = None
    raw_mem = _sysctl("hw.memsize")
    if raw_mem and raw_mem.isdigit():
        mem_bytes = int(raw_mem)
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor() or _sysctl("machdep.cpu.brand_string"),
        "hw_model": _sysctl("hw.model"),
        "logical_cores": os.cpu_count(),
        "physical_cores": int(_sysctl("hw.physicalcpu") or 0) or None,
        "ram_bytes": mem_bytes,
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
    }


def git_commit(root: Path | None = None) -> str:
    root = root or config.ROOT
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        # Note dirty state
        dirty = subprocess.call(
            ["git", "-C", str(root), "diff", "--quiet", "--ignore-submodules"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return out + ("-dirty" if dirty != 0 else "")
    except Exception:
        return "uncommitted"


def machine_id() -> str:
    md = machine_metadata()
    key = f"{md.get('hw_model')}|{md.get('processor')}|{md.get('logical_cores')}|{md.get('ram_bytes')}"
    return sha256_text(key)[:16]


def provenance_stamp() -> dict[str, Any]:
    """A compact, embeddable provenance block for any result artifact."""
    return {
        "git_commit": git_commit(),
        "machine_id": machine_id(),
        "machine": machine_metadata(),
        "package_versions": package_versions(),
        "seed": config.GLOBAL_SEED,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
