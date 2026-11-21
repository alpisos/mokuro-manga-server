#!/usr/bin/env bash
# ==============================================================================
# Mokuro Manga Volume & Folder Processor
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
            echo "⚠️  Process stopped or encountered an error (exit code: $exit_code)."
        fi
        read -rp "Press [Enter] to close this window..."
    fi
}
trap cleanup EXIT INT TERM

if ! command -v mokuro &>/dev/null; then
    echo "❌ Error: 'mokuro' is not in PATH."
    echo "Ensure ~/.local/bin is in your PATH or reinstall via uv."
    exit 1
fi

sanitize_path() {
    local raw="$1"
    # Trim leading and trailing whitespace
    raw="${raw#"${raw%%[![:space:]]*}"}"
    raw="${raw%"${raw##*[![:space:]]}"}"

    # Strip surrounding single or double quotes repeatedly
    while [[ ("$raw" == \'*\' && "$raw" == *[\']) || ("$raw" == \"*\" && "$raw" == *[\"]) ]]; do
        raw="${raw:1:-1}"
        raw="${raw#"${raw%%[![:space:]]*}"}"
        raw="${raw%"${raw##*[![:space:]]}"}"
    done

    # Remove file:// URI prefix and URL-decode
    if [[ "$raw" == file://* ]]; then
        raw="${raw#file://}"
        if command -v python3 &>/dev/null; then
            raw="$(python3 -c "import urllib.parse, sys; print(urllib.parse.unquote(sys.argv[1]))" "$raw" 2>/dev/null || echo "$raw")"
        fi
    fi

    # Expand tilde ~
    raw="${raw/#\~/$HOME}"

    # Handle backslash escapes (e.g. from bash tab-completion or terminal drag-and-drop)
    if [ ! -e "$raw" ]; then
        local unesc="${raw//\\ / }"
        unesc="${unesc//\\[/\[}"
        unesc="${unesc//\\]/\]}"
        unesc="${unesc//\\(//(}"
        unesc="${unesc//\\)/)}"
        if [ -e "$unesc" ]; then
            raw="$unesc"
        fi
    fi

    echo "$raw"
}

TARGET="${1:-}"

echo "=========================================================="
echo "🌸 Mokuro Manga Volume & Folder Processor"
echo "=========================================================="

# Check if manga_input has any items ready
DEFAULT_TARGET=""
if [ -d "$INPUT_DIR" ]; then
    input_item_count=$(find "$INPUT_DIR" -mindepth 1 -maxdepth 1 \( -type d ! -name "_ocr" -o -iname "*.cbz" -o -iname "*.zip" \) 2>/dev/null | wc -l)
    if [ "$input_item_count" -gt 0 ]; then
        DEFAULT_TARGET="$INPUT_DIR"
    fi
fi

while [ -z "$TARGET" ]; do
    echo ""
    if [ -n "$DEFAULT_TARGET" ]; then
        echo "💡 Found $input_item_count item(s) waiting in manga_input/:"
        for it in "$INPUT_DIR"/*; do
            [ -e "$it" ] || continue
            [ "$(basename "$it")" = "_ocr" ] && continue
            echo "   • $(basename "$it")"
        done
        echo ""
        echo "👉 Press [Enter] to process everything in manga_input/,"
        echo "   OR drag & drop any manga folder / .cbz / .zip file here:"
    else
        echo "👉 Drag & drop a manga folder or .cbz/.zip file here, or enter path:"
    fi
    read -rp "Path: " USER_INPUT

    USER_INPUT="$(sanitize_path "$USER_INPUT")"

    if [ -z "$USER_INPUT" ]; then
        if [ -n "$DEFAULT_TARGET" ]; then
            TARGET="$DEFAULT_TARGET"
            break
        else
            echo "❌ No path entered. Please provide a path or press Ctrl+C to cancel."
            continue
        fi
    fi

    if [ ! -e "$USER_INPUT" ]; then
        echo "❌ Path does not exist: '$USER_INPUT'"
        echo "   Please check the spelling or drag & drop the folder again."
        continue
    fi

    TARGET="$USER_INPUT"
done

# If passed as command-line argument, still sanitize
TARGET="$(sanitize_path "$TARGET")"

if [ ! -e "$TARGET" ]; then
    echo "❌ Error: Path does not exist: '$TARGET'"
    exit 1
fi

# Case 1: Target is manga_input itself (run batch processor)
if [ "$TARGET" = "$INPUT_DIR" ]; then
    echo ""
    echo "🚀 Running batch processor for manga_input/..."
    ALREADY_PROMPTED=1
    exec bash "$SCRIPT_DIR/batch_process.sh"
fi

# Case 2: Target is a single archive file (.cbz or .zip)
if [ -f "$TARGET" ]; then
    ext="${TARGET##*.}"
    ext="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"
    if [ "$ext" != "cbz" ] && [ "$ext" != "zip" ]; then
        echo "❌ Error: '$TARGET' is not a supported manga archive (.cbz or .zip)."
        exit 1
    fi

    echo ""
    echo "🚀 Processing archive: $(basename "$TARGET")"
    echo "----------------------------------------------------------"
    mokuro "$TARGET" --disable_confirmation=True

# Case 3: Target is a directory
elif [ -d "$TARGET" ]; then
    image_count=$(find "$TARGET" -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" -o -iname "*.avif" \) 2>/dev/null | wc -l)
    archive_count=$(find "$TARGET" -maxdepth 1 -type f \( -iname "*.cbz" -o -iname "*.zip" \) 2>/dev/null | wc -l)
    subdir_count=$(find "$TARGET" -mindepth 1 -maxdepth 1 -type d ! -name "_ocr" 2>/dev/null | wc -l)

    echo ""
    echo "🚀 Processing directory: $(basename "$TARGET")"
    echo "----------------------------------------------------------"

    if [ "$image_count" -gt 0 ]; then
        echo "📸 Found $image_count page image(s). Processing as single volume..."
        mokuro "$TARGET" --disable_confirmation=True
    elif [ "$archive_count" -gt 0 ] || [ "$subdir_count" -gt 0 ]; then
        echo "📚 Found $archive_count archive(s) and $subdir_count volume folder(s)."
        echo "Scanning and processing all volumes inside directory..."
        mokuro --parent_dir="$TARGET" --disable_confirmation=True
    else
        echo "❌ Error: No manga page images or .cbz/.zip archives found in: $TARGET"
        exit 1
    fi
else
    echo "❌ Error: '$TARGET' is not a file or directory."
    exit 1
fi

# Post-processing: check if TARGET was inside manga_input/
is_in_input=0
case "$TARGET" in
    "$INPUT_DIR"/*|"$INPUT_DIR")
        is_in_input=1
        ;;
esac

if [ "$is_in_input" -eq 1 ]; then
    echo ""
    echo "📦 Moving completed volumes to manga_library/ and updating bookshelf..."
    if [ -f "$SCRIPT_DIR/sync_library.py" ]; then
        python3 "$SCRIPT_DIR/sync_library.py"
    fi
    echo ""
    echo "=========================================================="
    echo "🎉 Manga successfully processed and added to your library!"
    echo "Click 'Start Manga Server' on your Desktop to read."
    echo "=========================================================="
else
    echo ""
    echo "=========================================================="
    echo "🎉 Processing complete!"
    echo "Generated HTML reader is inside or alongside: $TARGET"
    echo "=========================================================="

    if [[ "$TARGET" == "$LIBRARY_DIR"* ]] && [ -f "$SCRIPT_DIR/sync_library.py" ]; then
        python3 "$SCRIPT_DIR/sync_library.py"
    fi

    # Search for generated HTML files to offer opening
    html_files=()
    if [ -d "$TARGET" ]; then
        while IFS= read -r -d '' f; do
            html_files+=("$f")
        done < <(find "$TARGET" -maxdepth 2 -iname "*.html" ! -name "index.html" -print0 2>/dev/null)
    elif [ -f "$TARGET" ]; then
        parent_dir="$(dirname "$TARGET")"
        stem="$(basename "${TARGET%.*}")"
        if [ -f "$parent_dir/$stem.html" ]; then
            html_files+=("$parent_dir/$stem.html")
        fi
    fi

    if [ ${#html_files[@]} -gt 0 ]; then
        echo ""
        echo "Generated reader file: ${html_files[0]}"
        read -rp "Would you like to open it in your browser now? [y/N]: " OPEN_BROWSER
        if [[ "$OPEN_BROWSER" =~ ^[Yy]$ ]]; then
            xdg-open "${html_files[0]}" &>/dev/null &
        fi
    fi
fi

echo ""
ALREADY_PROMPTED=1
read -rp "Press [Enter] to close this window..."
