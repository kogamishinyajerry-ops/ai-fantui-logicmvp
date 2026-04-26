#!/usr/bin/env bash
# P46-01 (2026-04-26): single-command /workbench dev server.
#
# What this script does, in order:
#   1. Picks a port (default 8780; override with PORT=xxxx).
#   2. Resolves the MiniMax API key. Order of preference (matches
#      _resolve_minimax_api_key in demo_server.py):
#        a) $MINIMAX_API_KEY already in this shell
#        b) $Minimax_API_key already in this shell
#        c) export Minimax_API_key="..." line in ~/.zshrc
#        d) ~/.minimax_key file
#      If none resolve, the LLM interpreter strategy will fall back
#      to rules; the server still starts so the demo works without
#      a key.
#   3. Sets WORKBENCH_PROPOSALS_DIR + WORKBENCH_DEV_QUEUE_DIR to
#      .planning/proposals + .planning/dev_queue under the repo
#      root so the on-disk state (gitignored) lives with the repo.
#   4. Kills any existing process on the chosen port, then exec's
#      `python3 -m well_harness.demo_server --port <port>` with
#      PYTHONPATH=src so the import works without `pip install -e`.
#
# Usage:
#   ./scripts/dev-serve.sh           # foreground on :8780
#   PORT=9000 ./scripts/dev-serve.sh # foreground on :9000
#   make dev                          # same, via Makefile

set -euo pipefail

# Resolve repo root from this script's location (works whether the
# user calls it via ./scripts/dev-serve.sh, make dev, or absolute path).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

PORT="${PORT:-8780}"

# ── Step 2: resolve MiniMax key (best-effort; non-fatal if missing).
resolve_minimax_key() {
    if [[ -n "${MINIMAX_API_KEY:-}" ]]; then
        printf '%s' "$MINIMAX_API_KEY"
        return 0
    fi
    if [[ -n "${Minimax_API_key:-}" ]]; then
        printf '%s' "$Minimax_API_key"
        return 0
    fi
    if [[ -f "$HOME/.zshrc" ]]; then
        # Match `export Minimax_API_key="..."` (the user's actual var name)
        local from_zshrc
        from_zshrc=$(grep -E '^export[[:space:]]+Minimax_API_key=' "$HOME/.zshrc" \
            | tail -n 1 \
            | sed -E 's/^export[[:space:]]+Minimax_API_key=//' \
            | sed -E 's/^"(.*)"$/\1/' \
            | sed -E "s/^'(.*)'\$/\1/")
        if [[ -n "$from_zshrc" ]]; then
            printf '%s' "$from_zshrc"
            return 0
        fi
    fi
    if [[ -f "$HOME/.minimax_key" ]]; then
        # Strip trailing whitespace/newlines.
        local from_file
        from_file=$(tr -d '[:space:]' < "$HOME/.minimax_key")
        if [[ -n "$from_file" ]]; then
            printf '%s' "$from_file"
            return 0
        fi
    fi
    return 1
}

if KEY=$(resolve_minimax_key); then
    export MINIMAX_API_KEY="$KEY"
    echo "[dev-serve] MINIMAX_API_KEY resolved (${#KEY} chars, prefix ${KEY:0:8}…)"
else
    echo "[dev-serve] no MiniMax key found; LLM interpreter will fall back to rules"
fi

# ── Step 3: per-session demo state lives under the repo (gitignored).
export WORKBENCH_PROPOSALS_DIR="$REPO_ROOT/.planning/proposals"
export WORKBENCH_DEV_QUEUE_DIR="$REPO_ROOT/.planning/dev_queue"
mkdir -p "$WORKBENCH_PROPOSALS_DIR" "$WORKBENCH_DEV_QUEUE_DIR"

# ── Step 4: free the port + start the server.
if existing=$(lsof -ti:"$PORT" 2>/dev/null); then
    echo "[dev-serve] port $PORT busy (pid $existing); killing"
    kill "$existing" 2>/dev/null || true
    # Brief settle; lsof often returns before the kernel reaps.
    sleep 1
fi

echo "[dev-serve] starting demo server on http://127.0.0.1:$PORT/workbench"
echo "[dev-serve]   proposals dir : $WORKBENCH_PROPOSALS_DIR"
echo "[dev-serve]   dev_queue dir : $WORKBENCH_DEV_QUEUE_DIR"
exec env PYTHONPATH=src python3 -m well_harness.demo_server --port "$PORT"
