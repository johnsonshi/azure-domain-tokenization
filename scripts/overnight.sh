#!/usr/bin/env bash
# overnight.sh — run the study end-to-end under caffeinate (plan.md §0, §20).
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/.."

PROFILE="${1:-pilot}"
LOG="results/raw/logs/overnight_$(date +%Y%m%d_%H%M%S).log"
mkdir -p results/raw/logs

echo "== overnight run (profile=$PROFILE) ==" | tee "$LOG"

run() { echo ">> $*" | tee -a "$LOG"; caffeinate -i -s "$@" 2>&1 | tee -a "$LOG"; }

bash scripts/doctor.sh 2>&1 | tee -a "$LOG" || { echo "doctor failed"; exit 1; }

run uv run msdocs-tok acquire --profile "$PROFILE"
run uv run msdocs-tok audit   --profile "$PROFILE"
run uv run msdocs-tok train   --profile "$PROFILE"
run uv run msdocs-tok evaluate --profile "$PROFILE"
run uv run msdocs-tok benchmark --profile "$PROFILE"
run uv run msdocs-tok analyze --profile "$PROFILE"
run uv run msdocs-tok report  --profile "$PROFILE"
run uv run msdocs-tok verify  --profile "$PROFILE"

echo "== overnight run complete ==" | tee -a "$LOG"
