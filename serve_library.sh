#!/usr/bin/env bash
# ==============================================================================
# Mokuro Local Library Web Server
# ==============================================================================

# If launched from GUI without an interactive terminal, relaunch inside Konsole
if [ ! -t 0 ] && [ ! -t 1 ]; then
    if command -v konsole &>/dev/null; then
        exec konsole --noclose -e "$0" "$@"
    fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Sync finished volumes from manga_input and refresh bookshelf
if [ -f "$SCRIPT_DIR/sync_library.py" ]; then
    python3 "$SCRIPT_DIR/sync_library.py"
fi

# 2. Start the local server
exec python3 "$SCRIPT_DIR/server.py"
