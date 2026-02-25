#!/bin/bash

# loom -- autonomous Claude Code loop
# Each iteration: run claude with AGENT_PROMPT.md, log output, repeat

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PROMPT_FILE="$SCRIPT_DIR/AGENT_PROMPT.md"
DELAY=${LOOM_DELAY:-60}  # seconds between iterations, default 60

mkdir -p "$LOG_DIR"

iteration=0

while true; do
    iteration=$((iteration + 1))
    timestamp=$(date +"%Y%m%d_%H%M%S")
    logfile="$LOG_DIR/${timestamp}_${iteration}.log"

    echo "--- iteration $iteration starting at $(date) ---"

    if [ ! -f "$PROMPT_FILE" ]; then
        echo "AGENT_PROMPT.md not found. Exiting."
        exit 1
    fi

    claude --dangerously-skip-permissions \
           -p "$(cat "$PROMPT_FILE")" \
           --model claude-opus-4-6 \
           &> "$logfile" || true

    echo "--- iteration $iteration finished at $(date) ---"
    echo "    log: $logfile"

    sleep "$DELAY"
done
