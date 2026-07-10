#!/usr/bin/env bash
# doctor.sh — environment + budget preflight checks (plan.md §20 Phase 0 gate).
set -uo pipefail

export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/.."

fail=0
warn=0
ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$1"; fail=$((fail+1)); }
note() { printf '  \033[33m!\033[0m %s\n' "$1"; warn=$((warn+1)); }

echo "== msdocs-tokenizer doctor =="

echo "[tools]"
command -v uv >/dev/null 2>&1 && ok "uv $(uv --version 2>/dev/null | awk '{print $2}')" || bad "uv not found (install: https://astral.sh/uv)"
command -v git >/dev/null 2>&1 && ok "git $(git --version | awk '{print $3}')" || bad "git not found"
command -v gh >/dev/null 2>&1 && ok "gh $(gh --version | head -1 | awk '{print $3}')" || note "gh not found (needed for repo inventory)"
command -v caffeinate >/dev/null 2>&1 && ok "caffeinate present" || note "caffeinate not found (macOS keep-awake)"

echo "[github auth]"
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  ok "gh authenticated"
else
  note "gh not authenticated (run: gh auth login) — inventory/acquisition may be rate-limited"
fi

echo "[python env]"
if uv run python -c "import sys; assert sys.version_info[:2]==(3,12)" >/dev/null 2>&1; then
  ok "python $(uv run python -c 'import platform;print(platform.python_version())' 2>/dev/null)"
else
  note "python is not 3.12 (run: uv sync)"
fi

echo "[packages]"
uv run python - <<'PY'
import importlib, sys
mods = ["tokenizers","tiktoken","numpy","pandas","pyarrow","pydantic",
        "yaml","psutil","datasketch","typer","matplotlib","nbformat"]
missing = []
for m in mods:
    try:
        importlib.import_module(m)
    except Exception as e:
        missing.append(f"{m}: {e}")
if missing:
    print("MISSING:" + ";".join(missing)); sys.exit(1)
print("ALL_OK")
PY
if [ $? -eq 0 ]; then ok "core packages import"; else bad "some packages missing (run: uv sync)"; fi

echo "[package self-import]"
uv run python -c "import msdocs_tokenizer; print(msdocs_tokenizer.__version__)" >/dev/null 2>&1 \
  && ok "msdocs_tokenizer importable" || bad "msdocs_tokenizer not importable (run: uv sync)"

echo "[cpu]"
cores=$(python3 -c 'import os;print(os.cpu_count() or 1)')
workers=$(python3 -c "import os;print(max(1,(os.cpu_count() or 2)-2))")
ok "logical cores: ${cores}; sustained workers: ${workers}"

echo "[disk]"
avail_kb=$(df -k . | awk 'NR==2{print $4}')
total_kb=$(df -k . | awk 'NR==2{print $2}')
avail_gb=$(python3 -c "print(f'{${avail_kb}/1024/1024:.1f}')")
free_frac=$(python3 -c "print(${avail_kb}/${total_kb})")
ok "free disk: ${avail_gb} GiB"
if python3 -c "import sys; sys.exit(0 if ${free_frac} >= 0.15 else 1)"; then
  ok "free disk >= 15%"
else
  bad "free disk below 15% — stop condition (plan.md §28)"
fi

echo "[budget files]"
for f in STATE.md DECISIONS.md FINDINGS.md RUN_LOG.md work_queue.jsonl; do
  [ -f "$f" ] && ok "$f present" || note "$f missing"
done

echo
if [ "$fail" -gt 0 ]; then
  printf '\033[31mDOCTOR: %d hard failure(s), %d warning(s)\033[0m\n' "$fail" "$warn"
  exit 1
fi
printf '\033[32mDOCTOR: OK\033[0m (%d warning(s))\n' "$warn"
exit 0
