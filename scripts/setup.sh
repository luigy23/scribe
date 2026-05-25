#!/usr/bin/env bash
# Scribe — one-shot developer setup.
# Creates the venv, installs deps, checks Ollama, and pulls the default model.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

G="\033[0;32m"; B="\033[0;34m"; Y="\033[0;33m"; R="\033[0;31m"; N="\033[0m"
MODEL="${SCRIBE_MODEL:-qwen2.5-coder:7b}"

echo -e "${B}==>${N} Scribe setup at $REPO_ROOT"

# 1. Python
PY=""
for cand in python3.13 python3.12 python3.11; do
    if command -v "$cand" >/dev/null 2>&1; then
        PY="$cand"
        break
    fi
done
if [ -z "$PY" ]; then
    echo -e "${R}ERROR${N}: Python 3.11+ not found. Install with: brew install python@3.13"
    exit 1
fi
echo -e "${G}✓${N} Using $($PY --version)"

if [ ! -d .venv ]; then
    echo -e "${B}==>${N} Creating .venv ..."
    "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -e . --quiet
pip install -r requirements.txt --quiet
echo -e "${G}✓${N} Python dependencies installed"

# 2. Ollama
if ! command -v ollama >/dev/null 2>&1; then
    echo -e "${Y}WARN${N}: ollama not found. Install with: brew install ollama"
    echo "Then re-run this script."
    exit 1
fi

# Start the server if it isn't already running.
if ! curl -sf "http://localhost:11434" >/dev/null 2>&1; then
    echo -e "${B}==>${N} Starting Ollama server in background..."
    ollama serve > /tmp/ollama.log 2>&1 &
    disown
    sleep 2
fi
echo -e "${G}✓${N} Ollama server is up"

# Pull the model if not present
if ! ollama list 2>/dev/null | awk 'NR>1 {print $1}' | grep -q "^${MODEL%%:*}"; then
    echo -e "${B}==>${N} Pulling model: $MODEL (this takes a few minutes)"
    ollama pull "$MODEL"
fi
echo -e "${G}✓${N} Model $MODEL is ready"

echo ""
echo -e "${G}Done.${N}"
echo ""
echo "Try one of these:"
echo "  source .venv/bin/activate"
echo "  scribe --help"
echo "  scribe status"
echo "  scribe analyze ."
echo "  scribe generate . --output README.generated.md"
echo "  scribe ui"
