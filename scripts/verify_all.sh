#!/usr/bin/env bash
# verify_all.sh — full reproduction gate (plan.md §20 Phase 9 gate).
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/.."

PROFILE="${1:-pilot}"
fail=0

echo "== verify_all (profile=$PROFILE) =="

echo "[1/4] tests"
uv run pytest -q -m "not network" || fail=1

echo "[2/4] doctor"
bash scripts/doctor.sh || fail=1

echo "[3/4] pipeline verify gate"
uv run msdocs-tok verify --profile "$PROFILE" || fail=1

echo "[4/4] no accidentally-committed raw corpora / large files"
# Fail if any tracked file lives under the git-ignored raw/external trees.
leak=$(git ls-files -- external/ 'data/raw/**' 'data/normalized/**' 'data/segments/**' \
        'data/splits/*.corpus.txt' 'artifacts/tokenizers/*/' 2>/dev/null | head -20)
if [ -n "$leak" ]; then
  echo "  ✗ tracked raw/large artifacts detected:"; echo "$leak"; fail=1
else
  echo "  ✓ no raw corpora or large artifacts tracked"
fi

# Fail on any tracked file > 5 MB
big=$(git ls-files | while read -r f; do
  [ -f "$f" ] || continue
  sz=$(wc -c < "$f" 2>/dev/null || echo 0)
  if [ "$sz" -gt 5242880 ]; then echo "  $f ($sz bytes)"; fi
done)
if [ -n "$big" ]; then echo "  ✗ tracked files > 5MB:"; echo "$big"; fail=1; fi

echo
if [ "$fail" -eq 0 ]; then echo "VERIFY_ALL: OK"; exit 0; else echo "VERIFY_ALL: FAIL"; exit 1; fi
