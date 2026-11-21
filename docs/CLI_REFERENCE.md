# 💻 Mokuro CLI Reference

`mokuro` is installed in your user PATH (`~/.local/bin/mokuro`). You can invoke it from any terminal.

```bash
mokuro [OPTIONS] [PATHS]...
```

---

## 📌 Common Command Examples

### 1. Process a single volume
```bash
mokuro "/path/to/mokuro-manga-server/manga_input/OnePiece_v01"
```

### 2. Process a `.cbz` or `.zip` file without confirmation prompt
```bash
mokuro "/path/to/SpyXFamily_v01.cbz" --disable_confirmation
```
*(By default, Mokuro extracts the volume into a folder of the same name and creates the HTML overlay inside).*

### 3. Batch process an entire manga series (parent directory)
```bash
mokuro --parent_dir "/path/to/Manga_Series_Folder" --disable_confirmation
```
*(Mokuro will scan for every subfolder or archive inside and process each one in order).*

### 4. Force CPU execution
```bash
mokuro --force_cpu "/path/to/volume"
```
*(Useful if you are on a system with GPU driver conflicts, though your system defaults to CPU already).*

### 5. Reprocess / Regenerate HTML without redoing OCR
If you already processed a volume, Mokuro stores OCR bounding boxes and text in a hidden `_ocr` folder. To quickly regenerate the HTML reader without re-running OCR:
```bash
mokuro "/path/to/volume"
```
Mokuro will detect the cached `_ocr` folder and finish in seconds!

### 6. Force fresh re-run (ignoring cache)
```bash
mokuro --no_cache "/path/to/volume"
```

---

## 📋 Complete Flag Reference

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `PATHS` | `list` | *none* | Path(s) to volume folders, `.cbz`, or `.zip` files. |
| `--parent_dir` | `str` | `None` | Process all manga volumes contained within this directory. |
| `--disable_confirmation` | `bool` | `False` | Skip interactive `[y/N]` confirmation before processing starts. |
| `--force_cpu` | `bool` | `False` | Force PyTorch to run on CPU even if CUDA hardware is detected. |
| `--disable_ocr` | `bool` | `False` | Only perform layout detection and generate HTML without running text recognition. |
| `--no_cache` | `bool` | `False` | Ignore existing OCR cache in `_ocr` directories and recompute everything. |
| `--unzip` | `bool` | `False` | Extract `.zip` / `.cbz` files into their original location before processing. |
| `--legacy_html` | `bool` | `True` | Generates the classic self-contained interactive `.html` reader page. |
| `--as_one_file` | `bool` | `True` | Embeds CSS and JavaScript directly into the `.html` file instead of creating separate asset files. |
| `--pretrained_model_name_or_path` | `str` | `kha-white/manga-ocr-base` | Custom Hugging Face model identifier or local path for OCR. |
| `--ignore_errors` | `bool` | `False` | Continue processing remaining volumes even if one page or volume fails. |
| `--version` | `bool` | `False` | Display current Mokuro version and exit. |

---

## 💡 Pro Tip: Processing in the Background

For large series (e.g., 20+ volumes), you can run Mokuro in the background and monitor its progress:

```bash
nohup mokuro --parent_dir "/path/to/series" --disable_confirmation > mokuro.log 2>&1 &
tail -f mokuro.log
```
