# 📖 Mokuro Reading & Viewing Guide

Once Mokuro processes a volume, you can read it interactively in any modern web browser.

---

## 🖥️ 1. The Built-in HTML Reader

When Mokuro finishes processing a manga folder, it creates a single file named after the folder, such as `Volume_01.html`.

### How to Open:
1. Navigate to the manga folder inside [`manga_library/`](../manga_library).
2. Double-click the `.html` file to open it in your default browser (Firefox, Chromium, Chrome, etc.).

### Controls & Shortcuts:
| Action | Key / Gesture |
| :--- | :--- |
| **Next Page** | `Left Arrow` (Standard Japanese right-to-left manga layout) or `Space` / `Page Down` |
| **Previous Page** | `Right Arrow` or `Page Up` |
| **Toggle Text Boxes** | Hover over any dialogue balloon to see the highlight box |
| **Select Text** | Click and drag over the text box, or hover with a popup dictionary active |
| **Fullscreen** | `F11` (Browser fullscreen) |
| **Toggle Layout Menu** | Click the gear / controls icon in the top corner of the viewer |

---

## 🌐 2. Web Readers & Modern Frontends

If you want advanced features like double-page spread emulation, continuous vertical scrolling, custom zoom modes, or library shelf management:

### Option A: Mokuro Web Reader (PWA)
- **URL**: [https://reader.mokuro.app](https://reader.mokuro.app)
- **Features**:
  - Works 100% offline (it's a Progressive Web App).
  - Clean two-page manga reader UI.
  - Automatically loads `.mokuro` metadata files or unzipped folders.
  - Customizable hotkeys and touch-friendly gestures for trackpads and tablets.

### Option B: Local Web Server (Recommended for Extensions)
Some browser security policies restrict extensions (like Yomitan) from accessing `file:///` URLs without manual permission toggles.

To avoid this, simply run our helper script:
```bash
./serve_library.sh
```
This serves your [`manga_library/`](../manga_library) at `http://localhost:8080` and opens your browser automatically!

---

## ⚙️ 3. Reading Direction & Display Settings

Japanese manga is read **Right to Left (RTL)**:
- In the reader options, make sure **Reading Direction** is set to **RTL** (`Right to Left`).
- If double pages (spreads) appear misaligned, use the **Shift Page Offset** toggle in the reader menu so cover pages and dual-page illustrations line up correctly.
