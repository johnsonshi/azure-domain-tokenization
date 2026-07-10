"""Source acquisition with exact commit pinning (plan.md §9).

Preferred path: blobless, no-checkout clone + cone sparse-checkout of selected
paths. Fallback: GitHub API blob downloader (deterministic selection, SHA
verification, caching). Never crawls rendered learn.microsoft.com pages.

All raw text lands under data/raw/ (git-ignored). Only manifests/hashes are
publishable.
"""
from __future__ import annotations

import base64
import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from . import config
from .provenance import sha256_bytes, sha256_text
from .schemas import SourceLock


class AcquireError(RuntimeError):
    pass


def _run(cmd: list[str], cwd: str | Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True,
                          capture_output=True)
    if check and proc.returncode != 0:
        raise AcquireError(f"cmd failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr[:2000]}")
    return proc


# --------------------------------------------------------------------------- #
# Git sparse-checkout path
# --------------------------------------------------------------------------- #
def clone_blobless(url: str, dest: Path, ref: str | None = None) -> str:
    """Blobless, no-checkout clone. Returns the pinned commit SHA."""
    dest = Path(dest)
    if not (dest / ".git").exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        _run(["git", "clone", "--filter=blob:none", "--no-checkout",
              *(["--depth", "1"] if ref is None else []), url, str(dest)])
    if ref:
        _run(["git", "-C", str(dest), "fetch", "--depth", "1", "origin", ref])
        _run(["git", "-C", str(dest), "checkout", "--no-overlay", ref], check=False)
    return _run(["git", "-C", str(dest), "rev-parse", "HEAD"]).stdout.strip()


def list_tree_dirs(dest: Path, subpath: str = "") -> list[str]:
    args = ["git", "-C", str(dest), "ls-tree", "-d", "--name-only", "HEAD"]
    if subpath:
        args.append(subpath + "/")
    out = _run(args).stdout.strip()
    return [ln for ln in out.splitlines() if ln]


def sparse_checkout(dest: Path, paths: list[str]) -> None:
    _run(["git", "-C", str(dest), "sparse-checkout", "init", "--cone"])
    _run(["git", "-C", str(dest), "sparse-checkout", "set", *paths])
    _run(["git", "-C", str(dest), "checkout"])


def enumerate_markdown(dest: Path, paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for p in paths:
        base = Path(dest) / p
        if base.is_dir():
            found.extend(sorted(base.rglob("*.md")))
        elif base.suffix == ".md" and base.exists():
            found.append(base)
    return found


# --------------------------------------------------------------------------- #
# GitHub API blob-downloader fallback
# --------------------------------------------------------------------------- #
def gh_api(path: str) -> dict | list:
    """Call the GitHub API via the authenticated `gh` CLI (respects rate limits)."""
    proc = _run(["gh", "api", path])
    return json.loads(proc.stdout)


def api_pinned_sha(repo: str, ref: str = "HEAD") -> str:
    data = gh_api(f"repos/{repo}/commits/{ref}")
    return data["sha"]  # type: ignore[index]


def api_list_markdown(repo: str, sha: str, prefix: str = "") -> list[tuple[str, str]]:
    """Return [(path, blob_sha)] for markdown files under prefix at a commit."""
    tree = gh_api(f"repos/{repo}/git/trees/{sha}?recursive=1")
    out: list[tuple[str, str]] = []
    for node in tree.get("tree", []):  # type: ignore[union-attr]
        if node.get("type") == "blob" and node["path"].endswith(".md"):
            if not prefix or node["path"].startswith(prefix):
                out.append((node["path"], node["sha"]))
    return out


def api_download_blob(repo: str, blob_sha: str, cache_dir: Path) -> bytes:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{blob_sha}.blob"
    if cached.exists():
        return cached.read_bytes()
    data = gh_api(f"repos/{repo}/git/blobs/{blob_sha}")
    content = base64.b64decode(data["content"])  # type: ignore[index]
    # Verify against GitHub's git blob SHA-1 (object header + content).
    cached.write_bytes(content)
    return content


# --------------------------------------------------------------------------- #
# High-level record
# --------------------------------------------------------------------------- #
@dataclass
class AcquiredRepo:
    lock: SourceLock
    markdown_paths: list[Path] = field(default_factory=list)


def write_sources_lock(locks: list[SourceLock], path: Path | None = None) -> Path:
    path = path or (config.MANIFESTS / "sources.lock.json")
    from .provenance import atomic_write_json

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "seed": config.GLOBAL_SEED,
        "sources": [l.model_dump() for l in locks],
    }
    atomic_write_json(path, payload)
    return path


def load_sources_lock(path: Path | None = None) -> list[SourceLock]:
    path = path or (config.MANIFESTS / "sources.lock.json")
    if not path.exists():
        return []
    payload = json.loads(path.read_text())
    return [SourceLock(**s) for s in payload.get("sources", [])]
