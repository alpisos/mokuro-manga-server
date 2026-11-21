# 🎯 Yomitan & Anki Mining Guide

Pairing **Mokuro** with **Yomitan** (the modern active successor to Yomichan) turns reading raw Japanese manga into an effortless language-learning experience.

---

## 🧩 Step 1: Install & Set Up Yomitan

### 1. Install the Extension:
- **Firefox**: [Yomitan on Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/yomitan/)
- **Chrome / Chromium**: [Yomitan on Chrome Web Store](https://chromewebstore.google.com/detail/yomitan/likgccflfdipajodogechhijaiklgcnh)

### 2. Enable File URL Access (If reading local `.html` files directly):
1. In your browser, open `chrome://extensions` or `about:addons`.
2. Find **Yomitan** and click **Details / Manage**.
3. Toggle ON **"Allow access to file URLs"**.
*(Note: If you use `./serve_library.sh`, this step is not needed as it runs via `http://localhost:8080`).*

### 3. Install Recommended Japanese Dictionaries:
Open Yomitan Settings -> **Dictionaries** -> **Configure installed and enabled dictionaries**:
- **Jitendex** or **JMdict**: Primary Japanese-English dictionary with definitions and nuances.
- **Kanjidic**: Kanji breakdown, stroke count, JLPT level, components.
- **KireiCake** / **Pixiv Slang**: Essential for manga colloquialisms, contractions, internet slang, and dialectal endings (e.g. Kansai-ben).
- **Pitch Accent Dictionary**: Visual pitch accent curves (low/high pitch).
- **Daijisen** / **Shinmeikai** (Optional): High-quality Japanese monolingual dictionaries.

---

## 🗃️ Step 2: Connect Anki for 1-Click Sentence Mining

### 1. Install Anki & AnkiConnect:
1. Ensure **Anki** is installed on your computer.
2. In Anki, go to `Tools` -> `Add-ons` -> `Get Add-ons...`.
3. Enter code: **`2055492159`** (*AnkiConnect*) and click OK.
4. Restart Anki.

### 2. Configure Yomitan Anki Integration:
1. Open Yomitan Settings -> **Anki**.
2. Toggle **Enable Anki integration** ON.
3. Verify connection (Server: `http://127.0.0.1:8765`).
4. Select your preferred **Deck** and **Model** (Note Type).

### 3. Recommended Field Mapping:
Map your note fields to Yomitan tags:
- **Expression / Word**: `{marker}{expression}`
- **Reading**: `{reading}`
- **Glossary / Definition**: `{glossary-brief}`
- **Sentence / Context**: `{sentence}`
- **Screenshot / Image**: `{screenshot}` *(Captures the manga panel automatically!)*
- **Audio**: `{audio}`

---

## ⚡ The Manga Reading & Mining Workflow

1. Open your processed manga volume in the browser.
2. Hold `Shift` (or your configured scan key) and hover over any Japanese text inside a speech bubble.
3. Yomitan displays the definition, reading, and kanji information instantly in a clean popup.
4. Click the green **`+`** button in the Yomitan popup window.
5. **Boom!** A complete flashcard with the word, reading, definition, full sentence context, and a cropped screenshot of the manga panel is created in Anki in under 1 second.
