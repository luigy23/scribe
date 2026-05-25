#!/usr/bin/env bash
# Scribe — local development launcher.
# Ensures Ollama is running, then opens the Streamlit UI.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

G="\033[0;32m"; B="\033[0;34m"; Y="\033[0;33m"; R="\033[0;31m"; N="\033[0m"

PORT="${SCRIBE_UI_PORT:-8501}"

# Pre-flight
if [ ! -d .venv ]; then
    echo -e "${R}ERROR${N}: .venv not found. Run ./scripts/setup.sh first."
    exit 1
fi

# Start Ollama if not running
if ! curl -sf "http://localhost:11434" >/dev/null 2>&1; then
    if ! command -v ollama >/dev/null 2>&1; then
        echo -e "${R}ERROR${N}: ollama not found. brew install ollama"
        exit 1
    fi
    echo -e "${B}→${N} Starting Ollama server..."
    ollama serve > /tmp/ollama.log 2>&1 &
    disown
    until curl -sf "http://localhost:11434" >/dev/null 2>&1; do sleep 1; done
fi
echo -e "${G}✓${N} Ollama server ready"

# Activate venv and launch UI
# shellcheck disable=SC1091
source .venv/bin/activate
echo -e "${B}→${N} Launching Scribe UI on http://localhost:$PORT ..."
exec scribe ui --port "$PORT"
