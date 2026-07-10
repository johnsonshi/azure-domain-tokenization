"""Global configuration: seeds, paths, budgets, and controlled vocabulary.

Everything that must stay identical across the controlled comparison lives here
so that a single import gives every module the same constants.
"""
from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #
# One global seed drives every stochastic step (sampling, bootstrap, minhash).
GLOBAL_SEED: int = int(os.environ.get("MSDOCS_SEED", "20260709"))

# --------------------------------------------------------------------------- #
# Repository paths
# --------------------------------------------------------------------------- #
def repo_root() -> Path:
    """Return the repository root (directory containing plan.md)."""
    env = os.environ.get("MSDOCS_REPO_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "plan.md").exists() and (parent / "pyproject.toml").exists():
            return parent
    # Fall back to three levels up: src/msdocs_tokenizer/config.py -> repo
    return here.parents[2]


ROOT = repo_root()
CONFIGS = ROOT / "configs"
INVENTORY = ROOT / "inventory"
LICENSES = ROOT / "licenses"
RESEARCH = ROOT / "research"
EXTERNAL = ROOT / "external"
DATA = ROOT / "data"
MANIFESTS = DATA / "manifests"
RAW = DATA / "raw"
NORMALIZED = DATA / "normalized"
SEGMENTS = DATA / "segments"
SPLITS = DATA / "splits"
EVALUATION = DATA / "evaluation"
AUDIT = DATA / "audit"
CACHE = DATA / "cache"
ARTIFACTS = ROOT / "artifacts" / "tokenizers"
RESULTS = ROOT / "results"
RESULTS_RAW = RESULTS / "raw"
RESULTS_PROCESSED = RESULTS / "processed"
RESULTS_TABLES = RESULTS / "tables"
RESULTS_FIGURES = RESULTS / "figures"
RESULTS_REPORTS = RESULTS / "reports"
LOGS = RESULTS_RAW / "logs"

# --------------------------------------------------------------------------- #
# Budgets (plan.md §0, §9)
# --------------------------------------------------------------------------- #
RUNTIME_BUDGET_HOURS: float = float(os.environ.get("MSDOCS_RUNTIME_HOURS", "10"))
SOURCE_DISK_BUDGET_GB: float = 25.0
GENERATED_ARTIFACT_BUDGET_GB: float = 5.0
MIN_FREE_DISK_FRACTION: float = 0.15

PILOT_CORPUS_BYTES: int = 32 * 1024 * 1024      # 32 MiB per training corpus
FULL_CORPUS_BYTES: int = 256 * 1024 * 1024      # 256 MiB per training corpus
MAX_CORPUS_BYTES: int = 512 * 1024 * 1024       # 512 MiB ceiling
BYTE_MATCH_TOLERANCE: float = 0.001             # corpora match within 0.1%


def max_workers() -> int:
    """max(1, logical_cores - 2) for sustained CPU work (plan.md §0)."""
    return max(1, (os.cpu_count() or 2) - 2)


# --------------------------------------------------------------------------- #
# Controlled vocabulary
# --------------------------------------------------------------------------- #
CONTENT_TYPES = (
    "prose",
    "heading",
    "table",
    "inline_code",
    "code",
    "cli",
    "json",
    "yaml",
    "powershell",
    "bicep",
    "url_path",
    "mixed",
    "unknown",
)

# Content types that count as "technical syntax" (vs. natural-language prose).
TECHNICAL_CONTENT_TYPES = frozenset(
    {"code", "cli", "json", "yaml", "powershell", "bicep", "url_path", "inline_code"}
)
PROSE_CONTENT_TYPES = frozenset({"prose", "heading", "table"})

# Required tokenizer vocabulary sizes (plan.md §13).
VOCAB_SIZES_REQUIRED = (8192, 16384, 32768)
VOCAB_SIZE_PILOT = 16384

# Training corpora (plan.md §12).
TRAINING_CORPORA = ("general", "azure", "mixed")

# Special tokens (fixed across all controlled tokenizers).
SPECIAL_TOKENS = ("<|endoftext|>", "<|pad|>")

# Byte budgets per split fraction for group-aware splitting.
DEFAULT_SPLIT_FRACTIONS = {
    "azure_train": 0.80,
    "azure_same_service_holdout": 0.10,
    "azure_cross_service_holdout": 0.10,
}
