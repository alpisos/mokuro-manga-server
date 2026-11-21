#!/usr/bin/env bash
# ==============================================================================
# Mokuro Updater
# ==============================================================================

set -e

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv &>/dev/null; then
    echo "❌ Error: 'uv' is not installed."
    exit 1
fi

echo "=========================================================="
echo "🌸 Checking for Mokuro Updates via uv..."
echo "=========================================================="

uv tool upgrade mokuro

echo ""
echo "✅ Mokuro is up to date!"
mokuro --version
