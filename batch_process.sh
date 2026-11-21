#!/usr/bin/env bash
# ==============================================================================
# Mokuro Batch Processor for manga_input/
# ==============================================================================

set -uo pipefail

# If launched from GUI without an interactive terminal, relaunch inside Konsole
if [ ! -t 0 ] && [ ! -t 1 ]; then
    if command -v konsole &>/dev/null; then
        exec konsole --noclose -e "$0" "$@"
    fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$HOME/.local/bin:$PATH"

INPUT_DIR="$SCRIPT_DIR/manga_input"
LIBRARY_DIR="$SCRIPT_DIR/manga_library"

ALREADY_PROMPTED=0

cleanup() {
    local exit_code=$?
    if [ "$ALREADY_PROMPTED" -eq 0 ] && [ -t 0 ]; then
        echo ""
        if [ "$exit_code" -ne 0 ]; then
            echo "⚠️  Batch processing stopped or encountered an error (exit code: $exit_code)."
        fi
        read -rp "Press [Enter] to close this window..."
    fi
}
trap cleanup EXIT INT TERM

mkdir -p "$INPUT_DIR" "$LIBRARY_DIR"

if ! command -v mokuro &>/dev/null; then
    echo "❌ Error: 'mokuro' executable not found in PATH."
    echo "Ensure ~/.local/bin is in your PATH or reinstall via uv."
    exit 1
fi

echo "=========================================================="
echo "🌸 Mokuro Batch Processor"
echo "Scanning input directory: $INPUT_DIR"
echo "=========================================================="

# Find directories or archive files in manga_input
ITEMS=()
while IFS= read -r -d '' item; do
    [ "$(basename "$item")" = "_ocr" ] && continue
    ITEMS+=("$item")
done < <(find "$INPUT_DIR" -mindepth 1 -maxdepth 1 \( -type d -o -name "*.cbz" -o -name "*.zip" \) -print0)

if [ ${#ITEMS[@]} -eq 0 ]; then
    echo "ℹ️  No manga folders or .cbz/.zip archives found in:"
    echo "   $INPUT_DIR"
    echo ""
    echo "👉 Place your manga folders or archives into that directory and run this script again!"
    echo ""
    ALREADY_PROMPTED=1
    read -rp "Press [Enter] to close this window..."
    exit 0
fi

echo "Found ${#ITEMS[@]} item(s) to process:"
for item in "${ITEMS[@]}"; do
    echo " • $(basename "$item")"
done
echo ""

for item in "${ITEMS[@]}"; do
    echo "----------------------------------------------------------"
    echo "🚀 Processing: $(basename "$item")"
    echo "----------------------------------------------------------"
    if [ -d "$item" ]; then
        image_count=$(find "$item" -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" -o -iname "*.avif" \) 2>/dev/null | wc -l)
        archive_count=$(find "$item" -maxdepth 1 -type f \( -iname "*.cbz" -o -iname "*.zip" \) 2>/dev/null | wc -l)
        subdir_count=$(find "$item" -mindepth 1 -maxdepth 1 -type d ! -name "_ocr" 2>/dev/null | wc -l)

        if [ "$image_count" -gt 0 ]; then
            mokuro "$item" --disable_confirmation=True
        elif [ "$archive_count" -gt 0 ] || [ "$subdir_count" -gt 0 ]; then
            mokuro --parent_dir="$item" --disable_confirmation=True
        else
            echo "⚠️ Warning: No manga pages or archives found in $(basename "$item"), skipping."
            continue
        fi
    else
        mokuro "$item" --disable_confirmation=True
    fi

    # Automatically move completed volumes to manga_library and update bookshelf
    if [ -f "$SCRIPT_DIR/sync_library.py" ]; then
        python3 "$SCRIPT_DIR/sync_library.py"
    fi
done

echo ""
echo "=========================================================="
echo "🎉 Batch processing complete!"
echo "All processed volumes are now ready in your library."
echo "Run ./serve_library.sh (or click 'Start Manga Server') to read!"
echo "=========================================================="
echo ""

ALREADY_PROMPTED=1
read -rp "Press [Enter] to close this window..."
