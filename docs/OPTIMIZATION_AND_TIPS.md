# ⚙️ Optimization, Performance & Tips

---

## ⚡ 1. Hardware Performance on CPU

Your system runs Mokuro on an **Intel 12th Gen (Alder Lake)** processor with PyTorch CPU acceleration.

### Performance Expectations:
- **Average speed**: ~1.0 – 2.0 seconds per manga page.
- A standard 200-page volume typically completes in **3 to 6 minutes**.
- **Memory footprint**: PyTorch + Manga-OCR models use roughly ~1.5 GB to 2.5 GB of RAM during active processing.

### CPU Tips:
- Close heavy 3D or compilation tasks while batch-processing large series to give PyTorch full CPU thread availability.
- PyTorch automatically utilizes all available CPU cores.

---

## 🔍 2. Understanding Text Detection & Furigana

### Furigana Handling:
- Manga-OCR is specially trained on Japanese manga fonts and layouts.
- In most standard speech bubbles, Manga-OCR transcribes the main kanji and intelligently integrates or filters out ruby furigana to prevent duplicate characters in the dictionary lookup (so `私` with `わたし` furigana is read cleanly as `私`, allowing Yomitan to look it up immediately without confusion).

### Vertical vs. Horizontal Text:
- Mokuro automatically classifies each text block's orientation:
  - **Vertical text** (*tategaki*): Standard for character speech and dialogue balloons.
  - **Horizontal text** (*yokogaki*): Common for signs, sound effects, phone messages, and chapter titles.

### Handwritten Sound Effects (Onomatopoeia / SFX):
- Stylized, hand-drawn SFX (gitaigo / giseigo) embedded directly in the art:
  - Large or heavily distorted graphic SFX might occasionally be skipped by layout detection.
  - Standard printed dialogue bubbles have an accuracy rate of ~98%+.

---

## 📁 3. Recommended Manga Library Organization

To keep your manga library clean and easy to browse:

```text
manga_library/
└── Frieren/
    ├── Volume_01/
    │   ├── 001.jpg
    │   ├── 002.jpg
    │   ├── _ocr/                 <-- OCR cache data
    │   ├── Volume_01.html        <-- Interactive Reader
    │   └── Volume_01.mokuro      <-- Metadata file
    ├── Volume_02/
    └── Volume_03/
```

> [!TIP]
> Keep the `_ocr/` folder! If you ever update Mokuro or change reader templates in the future, re-running Mokuro on a folder that has `_ocr/` will generate new HTML files in **less than 1 second** without having to re-run AI inference.

---

## 🔄 4. Keeping Mokuro Updated

Mokuro is managed cleanly using `uv`. You can update it anytime by running:

```bash
./update_mokuro.sh
```
Or directly in the terminal:
```bash
uv tool upgrade mokuro
```
