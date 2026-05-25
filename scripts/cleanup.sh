#!/usr/bin/env bash
# Scribe — cleanup.
# Removes generated artifacts; with --hard also deletes the repo.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Scribe cleanup at: $REPO_ROOT"

# Python virtualenv
if [ -d "$REPO_ROOT/.venv" ]; then
    echo "Removing .venv ..."
    rm -rf "$REPO_ROOT/.venv"
fi

# Example outputs
if [ -d "$REPO_ROOT/examples/output" ]; then
    echo "Removing examples/output ..."
    rm -rf "$REPO_ROOT/examples/output"
fi

# Python caches
find "$REPO_ROOT" -type d -name "__pycache__"      -prune -exec rm -rf {} + 2>/dev/null || true
find "$REPO_ROOT" -type d -name ".pytest_cache"    -prune -exec rm -rf {} + 2>/dev/null || true
find "$REPO_ROOT" -type d -name ".ruff_cache"      -prune -exec rm -rf {} + 2>/dev/null || true
find "$REPO_ROOT" -type d -name "*.egg-info"       -prune -exec rm -rf {} + 2>/dev/null || true

# Dev logs
rm -rf "$REPO_ROOT/.dev-logs" 2>/dev/null || true

# Optional: prompt before removing the Ollama model (shared resource)
echo ""
echo "To also remove the Ollama model (frees ~4.7 GB), run:"
echo "  ollama rm qwen2.5-coder:7b"
echo ""

echo "Standard cleanup complete."

if [ "${1:-}" = "--hard" ]; then
    echo ""
    read -p "HARD MODE: delete entire repo at $REPO_ROOT? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$HOME"
        rm -rf "$REPO_ROOT"
        echo "Repo deleted."
    fi
fi
