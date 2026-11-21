#!/usr/bin/env python3
"""
Mokuro Library Synchronizer and Bookshelf Generator
---------------------------------------------------
1. Scans manga_input/ for completed Mokuro volumes (*.html + volume directory).
2. Moves completed volumes, their OCR data, and archives to manga_library/.
3. Generates a responsive, modern dark-mode bookshelf (index.html) in manga_library/.
"""

import os
import sys
import shutil
import re
from pathlib import Path
from urllib.parse import quote
import html

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = SCRIPT_DIR / "manga_input"
LIBRARY_DIR = SCRIPT_DIR / "manga_library"
ASSETS_DIR = SCRIPT_DIR / "assets"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


def natural_sort_key(s):
    """Sort strings containing numbers naturally (e.g. 1, 2, 10 instead of 1, 10, 2)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", str(s))]


def sync_completed_volumes():
    """Finds completed Mokuro outputs in manga_input and moves them to manga_library."""
    if not INPUT_DIR.exists():
        return

    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

    # Copy assets folder to library so bookshelf can access the logo
    if ASSETS_DIR.exists():
        dest_assets = LIBRARY_DIR / "assets"
        if not dest_assets.exists():
            try:
                shutil.copytree(ASSETS_DIR, dest_assets)
            except Exception:
                pass

    # Find all *.html files in manga_input (excluding any potential index.html)
    html_files = [f for f in INPUT_DIR.glob("**/*.html") if f.name != "index.html"]

    moved_count = 0
    for html_file in html_files:
        volume_name = html_file.stem
        parent_dir = html_file.parent
        img_dir = parent_dir / volume_name

        # A volume is considered complete if the HTML file and its unzipped image folder exist
        if not (img_dir.is_dir() and any(f.suffix.lower() in IMAGE_EXTENSIONS for f in img_dir.iterdir())):
            continue

        rel_parent = parent_dir.relative_to(INPUT_DIR)
        target_dir = LIBRARY_DIR / rel_parent
        target_dir.mkdir(parents=True, exist_ok=True)

        print(f"📦 Moving completed volume: {volume_name} -> manga_library/{rel_parent}")

        # 1. Move HTML file
        target_html = target_dir / html_file.name
        if target_html.exists():
            target_html.unlink()
        shutil.move(str(html_file), str(target_html))

        # 2. Move volume images directory
        target_img_dir = target_dir / volume_name
        if target_img_dir.exists():
            shutil.rmtree(str(target_img_dir))
        shutil.move(str(img_dir), str(target_img_dir))

        # 3. Move .mokuro metadata file if present
        mokuro_file = parent_dir / f"{volume_name}.mokuro"
        if mokuro_file.exists():
            target_mokuro = target_dir / mokuro_file.name
            if target_mokuro.exists():
                target_mokuro.unlink()
            shutil.move(str(mokuro_file), str(target_mokuro))

        # 4. Keep associated archive (.cbz / .zip) intact in manga_input
        # Archives are left untouched in manga_input so the user's original files are never deleted or moved.

        # 5. Move OCR cache if present in _ocr/volume_name
        ocr_cache_dir = parent_dir / "_ocr" / volume_name
        if ocr_cache_dir.is_dir():
            target_ocr_dir = target_dir / "_ocr" / volume_name
            target_ocr_dir.parent.mkdir(parents=True, exist_ok=True)
            if target_ocr_dir.exists():
                shutil.rmtree(str(target_ocr_dir))
            shutil.move(str(ocr_cache_dir), str(target_ocr_dir))

        moved_count += 1

    # Clean up empty directories in manga_input
    for dirpath, dirnames, filenames in os.walk(str(INPUT_DIR), topdown=False):
        current = Path(dirpath)
        if current == INPUT_DIR:
            continue
        try:
            # If folder only contains empty _ocr or is completely empty
            contents = list(current.iterdir())
            if not contents or (len(contents) == 1 and contents[0].name == "_ocr" and not any(contents[0].iterdir())):
                if (current / "_ocr").exists():
                    shutil.rmtree(str(current / "_ocr"), ignore_errors=True)
                current.rmdir()
        except OSError:
            pass

    if moved_count > 0:
        print(f"✨ Successfully moved {moved_count} volume(s) into manga_library!")


def generate_bookshelf():
    """Scans manga_library and creates an interactive index.html bookshelf."""
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

    # Find all .html readers in manga_library (excluding index.html)
    html_files = [f for f in LIBRARY_DIR.glob("**/*.html") if f.name != "index.html"]

    volumes = []
    processed_dirs = set()
    for html_file in html_files:
        volume_name = html_file.stem
        parent_dir = html_file.parent
        img_dir = parent_dir / volume_name

        if not img_dir.is_dir():
            # Check if parent_dir itself contains images
            if any(f.suffix.lower() in IMAGE_EXTENSIONS for f in parent_dir.iterdir()):
                img_dir = parent_dir
            else:
                continue

        images = [f for f in img_dir.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]
        if not images:
            continue

        processed_dirs.add(img_dir.resolve())
        processed_dirs.add(parent_dir.resolve())

        images.sort(key=lambda p: natural_sort_key(p.name))
        cover_image = images[0]

        rel_parent = parent_dir.relative_to(LIBRARY_DIR)
        series_name = rel_parent.parts[0] if rel_parent.parts else "Single Volumes"

        rel_html = html_file.relative_to(LIBRARY_DIR).as_posix()
        rel_cover = cover_image.relative_to(LIBRARY_DIR).as_posix()

        volumes.append({
            "title": volume_name,
            "series": series_name,
            "html_path": rel_html,
            "cover_path": rel_cover,
            "pages": len(images),
        })

    # Find un-OCR'd / pending volume folders in manga_library
    unprocessed_volumes = []
    for candidate in sorted(LIBRARY_DIR.iterdir(), key=lambda p: natural_sort_key(p.name)):
        if not candidate.is_dir() or candidate.name in ("assets", "_ocr", ".directory"):
            continue
        if candidate.resolve() in processed_dirs:
            continue
        # Check if candidate has image files
        images = [f for f in candidate.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]
        if not images:
            continue
        # Check if candidate or its parent already has an html reader
        if any(f.suffix.lower() == ".html" for f in candidate.iterdir()):
            continue

        images.sort(key=lambda p: natural_sort_key(p.name))
        cover_image = images[0]
        unprocessed_volumes.append({
            "title": candidate.name,
            "cover_path": cover_image.relative_to(LIBRARY_DIR).as_posix(),
            "pages": len(images),
            "folder_path": str(candidate),
        })

    # Sort volumes naturally by series, then by title
    volumes.sort(key=lambda v: (natural_sort_key(v["series"]), natural_sort_key(v["title"])))

    # Group by series
    series_groups = {}
    for v in volumes:
        series_groups.setdefault(v["series"], []).append(v)

    # Build modern dark HTML page
    html_content = build_bookshelf_html(series_groups, len(volumes), unprocessed_volumes)

    index_file = LIBRARY_DIR / "index.html"
    index_file.write_text(html_content, encoding="utf-8")
    print(f"📚 Bookshelf updated: {len(volumes)} volume(s) across {len(series_groups)} series -> {index_file}")
    if unprocessed_volumes:
        print(f"⚠️  Notice: {len(unprocessed_volumes)} un-OCR'd manga volume(s) found in manga_library/ waiting for Mokuro processing.")
        print(f"   👉 Run 'Process Manga (Mokuro)' or 'Batch Process Manga (Mokuro)' to generate interactive readers.")


def build_bookshelf_html(series_groups, total_volumes, unprocessed_volumes=None):
    if unprocessed_volumes is None:
        unprocessed_volumes = []
    total_series = len(series_groups)
    stats_text = f"{total_series} Series • {total_volumes} Volume{'s' if total_volumes != 1 else ''}"
    if unprocessed_volumes:
        stats_text += f" • {len(unprocessed_volumes)} Pending OCR"

    sections_html = ""
    if not series_groups and not unprocessed_volumes:
        sections_html = """
        <div class="empty-state">
            <div class="empty-icon">📖</div>
            <h2>Your manga library is empty</h2>
            <p>Place your manga in <code>manga_input</code> and run <code>batch_process.sh</code> or <code>process_volume.sh</code>.</p>
            <p>Once processed, volumes will automatically appear here on your bookshelf!</p>
        </div>
        """
    else:
        for series_name, vols in series_groups.items():
            cards_html = ""
            for v in vols:
                escaped_title = html.escape(v["title"])
                cards_html += f"""
                <div class="manga-card" data-title="{escaped_title.lower()}">
                    <a href="{quote(v['html_path'])}" class="card-cover-wrapper" title="Read {escaped_title}">
                        <img src="{quote(v['cover_path'])}" alt="{escaped_title}" loading="lazy" class="card-cover">
                        <div class="card-badge">{v['pages']} pages</div>
                        <div class="card-overlay">
                            <span class="read-btn">Read Volume ▶</span>
                        </div>
                    </a>
                    <div class="card-details">
                        <h4 class="card-title" title="{escaped_title}">{escaped_title}</h4>
                        <a href="{quote(v['html_path'])}" class="quick-link">Open Reader →</a>
                    </div>
                </div>
                """

            escaped_series = html.escape(series_name)
            sections_html += f"""
            <section class="series-section" data-series="{escaped_series.lower()}">
                <div class="series-header">
                    <h2 class="series-title">{escaped_series}</h2>
                    <span class="series-badge">{len(vols)} volume{'s' if len(vols) != 1 else ''}</span>
                </div>
                <div class="cards-grid">
                    {cards_html}
                </div>
            </section>
            """

        if unprocessed_volumes:
            unproc_cards = ""
            for v in unprocessed_volumes:
                escaped_title = html.escape(v["title"])
                unproc_cards += f"""
                <div class="manga-card unproc-card" data-title="{escaped_title.lower()}">
                    <div class="card-cover-wrapper" title="{escaped_title} (Mokuro OCR processing needed)">
                        <img src="{quote(v['cover_path'])}" alt="{escaped_title}" loading="lazy" class="card-cover">
                        <div class="card-badge badge-warning">⏳ OCR Needed</div>
                        <div class="card-overlay unproc-overlay">
                            <span class="read-btn unproc-btn">Run Mokuro to Read ⚠️</span>
                        </div>
                    </div>
                    <div class="card-details">
                        <h4 class="card-title" title="{escaped_title}">{escaped_title}</h4>
                        <span class="status-note">{v['pages']} pages • Waiting for OCR</span>
                    </div>
                </div>
                """

            sections_html += f"""
            <section class="series-section unproc-section" data-series="unprocessed">
                <div class="series-header">
                    <div>
                        <h2 class="series-title">⏳ Waiting for Mokuro OCR</h2>
                        <p class="unproc-desc">Found {len(unprocessed_volumes)} raw volume(s). To enable selectable Japanese text and Yomitan dictionary lookups, run <strong>Process Manga (Mokuro)</strong> or <strong>Batch Process Manga (Mokuro)</strong>.</p>
                    </div>
                    <span class="series-badge badge-warning-count">{len(unprocessed_volumes)} volume{'s' if len(unprocessed_volumes) != 1 else ''}</span>
                </div>
                <div class="cards-grid">
                    {unproc_cards}
                </div>
            </section>
            """

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mokuro Manga Library</title>
    <style>
        :root {{
            --bg-base: #0f1015;
            --bg-surface: #181920;
            --bg-card: #20222c;
            --bg-card-hover: #292b38;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent: #ff6b81;
            --accent-glow: rgba(255, 107, 129, 0.35);
            --border: #2e313d;
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}

        body {{
            background-color: var(--bg-base);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* Header */
        header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(15, 16, 21, 0.92);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
            text-decoration: none;
            color: inherit;
        }}

        .brand-logo {{
            width: 38px;
            height: 38px;
            border-radius: var(--radius-sm);
            background: #2a2d3d;
            object-fit: cover;
        }}

        .brand-title {{
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .brand-subtitle {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            font-weight: 400;
        }}

        .header-controls {{
            display: flex;
            align-items: center;
            gap: 1rem;
            flex: 1;
            max-width: 500px;
            justify-content: flex-end;
        }}

        .search-box {{
            position: relative;
            width: 100%;
        }}

        .search-input {{
            width: 100%;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 0.65rem 1rem 0.65rem 2.5rem;
            color: var(--text-primary);
            font-size: 0.9rem;
            outline: none;
            transition: all 0.2s ease;
        }}

        .search-input:focus {{
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }}

        .search-icon {{
            position: absolute;
            left: 0.85rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.9rem;
            opacity: 0.6;
            pointer-events: none;
        }}

        .stats-badge {{
            padding: 0.45rem 0.85rem;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            font-size: 0.8rem;
            color: var(--text-secondary);
            white-space: nowrap;
        }}

        /* Main Container */
        main {{
            flex: 1;
            max-width: 1500px;
            width: 100%;
            margin: 0 auto;
            padding: 2.5rem 2rem;
            display: flex;
            flex-direction: column;
            gap: 3rem;
        }}

        /* Series Section */
        .series-section {{
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}

        .series-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            border-bottom: 2px solid var(--border);
            padding-bottom: 0.65rem;
        }}

        .series-title {{
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.01em;
        }}

        .series-badge {{
            font-size: 0.8rem;
            padding: 0.25rem 0.75rem;
            background: var(--bg-card);
            border-radius: 999px;
            color: var(--accent);
            font-weight: 600;
        }}

        .badge-warning {{
            background: rgba(234, 179, 8, 0.25) !important;
            color: #fde047 !important;
            border: 1px solid rgba(234, 179, 8, 0.4);
        }}

        .badge-warning-count {{
            background: rgba(234, 179, 8, 0.15);
            color: #fde047;
            border: 1px solid rgba(234, 179, 8, 0.3);
        }}

        .unproc-desc {{
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-top: 0.35rem;
            line-height: 1.4;
        }}

        .status-note {{
            font-size: 0.75rem;
            color: #facc15;
            font-weight: 500;
        }}

        .unproc-btn {{
            background: #ca8a04 !important;
            box-shadow: 0 4px 12px rgba(202, 138, 4, 0.4) !important;
        }}

        /* Grid */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 1.5rem;
        }}

        @media (min-width: 1200px) {{
            .cards-grid {{
                grid-template-columns: repeat(auto-fill, minmax(195px, 1fr));
            }}
        }}

        /* Manga Card */
        .manga-card {{
            background: var(--bg-card);
            border-radius: var(--radius-md);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid var(--border);
            transition: transform 0.25s cubic-bezier(0.2, 0, 0, 1), box-shadow 0.25s ease, border-color 0.25s ease;
        }}

        .manga-card:hover {{
            transform: translateY(-5px);
            border-color: var(--accent);
            box-shadow: 0 12px 24px -10px rgba(0, 0, 0, 0.6), 0 0 16px -2px var(--accent-glow);
        }}

        .card-cover-wrapper {{
            position: relative;
            width: 100%;
            aspect-ratio: 1 / 1.42;
            background: #15161d;
            overflow: hidden;
            display: block;
        }}

        .card-cover {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.35s ease;
        }}

        .manga-card:hover .card-cover {{
            transform: scale(1.05);
        }}

        .card-badge {{
            position: absolute;
            top: 0.6rem;
            right: 0.6rem;
            background: rgba(15, 16, 21, 0.85);
            backdrop-filter: blur(4px);
            color: #fff;
            font-size: 0.75rem;
            padding: 0.2rem 0.55rem;
            border-radius: var(--radius-sm);
            font-weight: 500;
        }}

        .card-overlay {{
            position: absolute;
            inset: 0;
            background: rgba(15, 16, 21, 0.65);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s ease;
        }}

        .manga-card:hover .card-overlay {{
            opacity: 1;
        }}

        .read-btn {{
            background: var(--accent);
            color: #fff;
            padding: 0.6rem 1.1rem;
            border-radius: var(--radius-sm);
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(255, 107, 129, 0.4);
            transform: translateY(6px);
            transition: transform 0.2s ease;
        }}

        .manga-card:hover .read-btn {{
            transform: translateY(0);
        }}

        .card-details {{
            padding: 0.85rem 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
            background: var(--bg-card);
            flex: 1;
            justify-content: space-between;
        }}

        .card-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.35;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .quick-link {{
            color: var(--accent);
            text-decoration: none;
            font-size: 0.78rem;
            font-weight: 600;
            transition: opacity 0.2s ease;
        }}

        .quick-link:hover {{
            opacity: 0.85;
            text-decoration: underline;
        }}

        /* Empty State */
        .empty-state {{
            margin: 5rem auto;
            text-align: center;
            max-width: 520px;
            background: var(--bg-surface);
            padding: 3rem 2rem;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
        }}

        .empty-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
        }}

        .empty-state h2 {{
            font-size: 1.4rem;
            margin-bottom: 0.75rem;
        }}

        .empty-state p {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 0.5rem;
        }}

        .empty-state code {{
            background: #252836;
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            color: var(--accent);
            font-size: 0.85rem;
        }}

        footer {{
            margin-top: auto;
            border-top: 1px solid var(--border);
            padding: 1.5rem 2rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <header>
        <a href="/" class="brand">
            <img src="assets/logo.png" alt="Mokuro Logo" class="brand-logo" onerror="this.style.display='none'">
            <div>
                <div class="brand-title">Mokuro Library <span style="color:var(--accent);">モクロ</span></div>
                <div class="brand-subtitle">Interactive Japanese Manga Bookshelf</div>
            </div>
        </a>

        <div class="header-controls">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" class="search-input" placeholder="Search volumes or series..." autocomplete="off">
            </div>
            <div class="stats-badge" id="statsBadge">
                {stats_text}
            </div>
        </div>
    </header>

    <main id="libraryContent">
        {sections_html}
    </main>

    <footer>
        Mokuro OCR Bookshelf &bull; Hover over text in the reader for instant popup dictionary lookups
    </footer>

    <script>
        const searchInput = document.getElementById('searchInput');
        const sections = document.querySelectorAll('.series-section');

        searchInput.addEventListener('input', (e) => {{
            const query = e.target.value.trim().toLowerCase();

            sections.forEach(section => {{
                const seriesName = section.getAttribute('data-series') || '';
                const cards = section.querySelectorAll('.manga-card');
                let visibleCount = 0;

                cards.forEach(card => {{
                    const title = card.getAttribute('data-title') || '';
                    const matches = title.includes(query) || seriesName.includes(query);
                    card.style.display = matches ? '' : 'none';
                    if (matches) visibleCount++;
                }});

                section.style.display = visibleCount > 0 ? '' : 'none';
            }});
        }});
    </script>
</body>
</html>
"""


def main():
    sync_completed_volumes()
    generate_bookshelf()


if __name__ == "__main__":
    main()
