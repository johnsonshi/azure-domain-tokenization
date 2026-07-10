#!/usr/bin/env bash
# resume.sh — resume the pipeline from wherever it stopped (stages are idempotent).
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/.."

PROFILE="${1:-pilot}"
echo "== resume (profile=$PROFILE): completed stages are skipped by content hash =="
ls -1 data/.stages/*.done.json 2>/dev/null | sed 's#data/.stages/#  done: #; s/.done.json//' || echo "  (no completed stages yet)"

exec bash scripts/overnight.sh "$PROFILE"
