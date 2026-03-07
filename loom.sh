#!/bin/bash

# loom -- autonomous Claude Code loop
# Each iteration: run claude with AGENT_PROMPT.md, log output, repeat
# Stops gracefully when .loom-stop file appears or SIGTERM received

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PROMPT_FILE="$SCRIPT_DIR/AGENT_PROMPT.md"
PID_FILE="$SCRIPT_DIR/.loom-pid"
STOP_FILE="$SCRIPT_DIR/.loom-stop"
LOCK_FILE="$SCRIPT_DIR/.loom-lock"
DELAY=${LOOM_DELAY:-1800}  # seconds between iterations, default 30 minutes
MIN_ITERATION_SECS=30   # if an iteration completes faster than this, something is wrong
MAX_FAST_FAILURES=3     # stop after this many consecutive fast iterations

mkdir -p "$LOG_DIR"

# Acquire exclusive lock -- prevents multiple instances
exec 9>"$LOCK_FILE"
if ! lockf -st 0 9; then
    echo "Another loom instance is running. Exiting."
    exit 0
fi

# Write PID so hooks can find us
echo $$ > "$PID_FILE"

# Track child claude PID for clean shutdown
claude_pid=""

# Clean up on exit -- only remove PID file if it's still ours
# Lock (fd 9) is released automatically when process exits
cleanup() {
    if [ -f "$PID_FILE" ] && [ "$(cat "$PID_FILE" 2>/dev/null)" = "$$" ]; then
        rm -f "$PID_FILE"
    fi
    echo "loom stopped at $(date)"
}
trap cleanup EXIT

# Handle SIGTERM gracefully -- also kill child claude if running
terminated=false
handle_term() {
    terminated=true
    echo "SIGTERM received, stopping..."
    if [ -n "$claude_pid" ] && kill -0 "$claude_pid" 2>/dev/null; then
        kill "$claude_pid" 2>/dev/null || true
    fi
}
trap handle_term TERM

# Remove stale stop file from previous run
rm -f "$STOP_FILE"

iteration=0
fast_failures=0
STARTUP_DELAY=${LOOM_STARTUP_DELAY:-120}  # wait before first iteration, gives time to start a new session

echo "loom started at $(date) (pid $$), waiting ${STARTUP_DELAY}s before first iteration..."
sleep "$STARTUP_DELAY" &
wait $! 2>/dev/null || true

# Check if we were stopped during startup delay
if [ -f "$STOP_FILE" ] || $terminated; then
    echo "Stopped during startup delay. Exiting."
    exit 0
fi

while true; do
    # Check stop conditions before starting new iteration
    if [ -f "$STOP_FILE" ]; then
        echo "Stop signal received. Exiting."
        exit 0
    fi
    if $terminated; then
        echo "Terminated. Exiting."
        exit 0
    fi

    iteration=$((iteration + 1))
    timestamp=$(date +"%Y%m%d_%H%M%S")
    logfile="$LOG_DIR/${timestamp}_${iteration}.log"

    iter_start=$(date +%s)

    echo "--- iteration $iteration starting at $(date) ---"

    if [ ! -f "$PROMPT_FILE" ]; then
        echo "AGENT_PROMPT.md not found. Exiting."
        exit 1
    fi

    LOOM_SESSION=1 claude --dangerously-skip-permissions \
           -p "$(cat "$PROMPT_FILE")" \
           --model claude-opus-4-6 \
           &> "$logfile" &
    claude_pid=$!
    wait "$claude_pid" 2>/dev/null
    exit_code=$?
    claude_pid=""

    iter_end=$(date +%s)
    iter_duration=$((iter_end - iter_start))

    echo "--- iteration $iteration finished at $(date) (exit code: $exit_code, ${iter_duration}s) ---"
    echo "    log: $logfile"

    # Guard against rapid-fire loops (broken prompt, immediate crash, etc.)
    if [ $iter_duration -lt $MIN_ITERATION_SECS ]; then
        fast_failures=$((fast_failures + 1))
        echo "Warning: iteration completed in ${iter_duration}s (<${MIN_ITERATION_SECS}s). Fast failure $fast_failures/$MAX_FAST_FAILURES."
        if [ $fast_failures -ge $MAX_FAST_FAILURES ]; then
            echo "Too many fast failures. Something is broken. Stopping loom."
            exit 1
        fi
    else
        fast_failures=0
    fi

    if [ $exit_code -ne 0 ]; then
        backoff=300  # start at 5 minutes, doubles each retry

        while true; do
            # Check stop conditions during backoff
            if [ -f "$STOP_FILE" ] || $terminated; then
                echo "Stop signal received during backoff. Exiting."
                exit 0
            fi

            echo "Error (exit code: $exit_code). Retrying in ${backoff}s ($(date))..."
            sleep "$backoff" &
            wait $! 2>/dev/null || true  # interruptible sleep
            backoff=$((backoff * 2))

            if [ -f "$STOP_FILE" ] || $terminated; then
                echo "Stop signal received during backoff. Exiting."
                exit 0
            fi

            LOOM_SESSION=1 claude --dangerously-skip-permissions \
                   -p "$(cat "$PROMPT_FILE")" \
                   --model claude-opus-4-6 \
                   &> "$logfile" &
            claude_pid=$!
            wait "$claude_pid" 2>/dev/null
            exit_code=$?
            claude_pid=""

            if [ $exit_code -eq 0 ]; then
                break
            fi
        done
    fi

    # Interruptible delay between iterations
    sleep "$DELAY" &
    wait $! 2>/dev/null || true
done
