# 🌸 Welcome to Mokuro (モクロ)

<p align="center">
  <img src="assets/logo.png" alt="Mokuro Logo (あ)" width="160" height="160" />
  <br/>
  <em>Read Japanese Manga with Instant Selectable Text & Popup Dictionaries</em>
</p>

---

## ⚡ What is Mokuro?

**Mokuro** is an open-source tool that processes raw Japanese manga images or archives (`.cbz`, `.zip`, or folders) and overlays **selectable, searchable text** directly on top of the original manga artwork.

By combining an advanced text detector with **Manga-OCR** (a state-of-the-art vision transformer trained on Japanese manga text), Mokuro turns static manga pages into an interactive reading experience where you can:
- **Hover or click** on speech bubbles to highlight Japanese text.
- Use popup dictionaries like **Yomitan** (formerly Yomichan) for instant 1-click definitions, readings, and pitch accents.
- Export vocabulary and sentences directly into **Anki** with screenshots for vocabulary mining.

---

## 🚀 Quick Start (In 3 Steps)

### Step 1: Put your manga in `manga_input`
Place any manga volume folder (containing `.jpg`, `.png`, or `.webp` pages) or `.cbz` / `.zip` file inside:
```
manga_input/
```

### Step 2: Run the Batch Processor
Open a terminal inside this folder and run:
```bash
./batch_process.sh
```
Or process a specific volume directly:
```bash
mokuro "/path/to/your/manga_volume"
```
*(On first execution, the Manga-OCR AI model `kha-white/manga-ocr-base` (~400MB) will download automatically into your cache.)*

### Step 3: Open and Read!
Inside your processed volume folder, you will find an **`.html`** file (e.g. `Volume_01.html`).
- Double-click the `.html` file to open it in Firefox or Chrome.
- Hover over any Japanese dialog bubble to select text or trigger Yomitan!

---

## 📂 Folder Overview

| File / Folder | Purpose |
| :--- | :--- |
| **[`manga_input/`](manga_input)** | Drop your unprocessed manga volumes or `.cbz` files here. |
| **[`manga_library/`](manga_library)** | Organized library for your processed manga. |
| **[`process_volume.sh`](process_volume.sh)** | Helper script to process any single volume with interactive path picker. |
| **[`batch_process.sh`](batch_process.sh)** | Automatically processes all volumes waiting in `manga_input/`. |
| **[`serve_library.sh`](serve_library.sh)** | Launches a lightweight local web server to read without browser CORS restrictions. |
| **[`update_mokuro.sh`](update_mokuro.sh)** | Checks for and updates Mokuro to the latest version. |
| **[`CLI_REFERENCE.md`](docs/CLI_REFERENCE.md)** | Complete guide to all command-line flags and options. |
| **[`READING_GUIDE.md`](docs/READING_GUIDE.md)** | Built-in reader tips, hotkeys, and modern web reader frontends. |
| **[`YOMITAN_ANKI_GUIDE.md`](docs/YOMITAN_ANKI_GUIDE.md)** | Step-by-step setup for popup dictionaries and 1-click Anki mining. |
| **[`OPTIMIZATION_AND_TIPS.md`](docs/OPTIMIZATION_AND_TIPS.md)** | Hardware performance, furigana tips, and cache management. |
| **[`docs/`](docs)** | Guides: CLI reference, reading, Yomitan/Anki, tips. |
| **[`assets/`](assets)** | High-resolution logo (`あ`) in SVG and PNG formats. |

> **Note:** No manga is included in this repo. `manga_input/` and `manga_library/` are empty on purpose; bring your own files.

## 🖥️ Optional: desktop launchers (KDE)

The `desktop/` folder has `.desktop` launchers. Replace `INSTALL_DIR` in each file with the full path to this folder, then copy them to `~/.local/share/applications/` or your Desktop.

## 🙏 Credits

Built around [mokuro](https://github.com/kha-white/mokuro) and [manga-ocr](https://github.com/kha-white/manga-ocr) by kha-white. This repo is only helper scripts and a small local server.

## License

[MIT](LICENSE)
