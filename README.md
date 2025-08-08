# CardViewer

**Check out your AI character cards (PNG files) the easy way. Flip through, search, preview, and manage thousands of cards in seconds, whether they’re SFW or NSFW. Sorting’s a breeze, too.**

---

## Features

* Loads thousands of cards crazy fast.
* Lets you see card images and info right away.
* Comes with both dark and light themes—switch whenever you want.
* Sort cards by name or creator, just one click.
* Search by name, creator, or tag (super easy).
* Add new cards by dragging PNGs straight into your folder.
* Right-click anywhere to open cards, export info, or save the PNG.
* Remembers your theme, folder, search, and window size for next time.

---

## Installation

**Requirements:**

* Python 3.8 or newer
* [PySide6](https://pypi.org/project/PySide6/) (Qt for Python)
* [Pillow](https://pypi.org/project/Pillow/) (for image handling)

### **1. Clone this repo**

```sh
git clone https://github.com/kaosnews/CardViewer.git
cd CardViewer
```

### **2. Install dependencies**

```sh
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, use:

```sh
pip install PySide6 Pillow
```

### **3. Run it!**

```sh
python card_viewer.py
```

---

## Supported Cards

* Works with TavernAI and SillyTavern PNG character cards.
* Extracts and displays embedded metadata (including non-standard fields).


---

## Changelog

### v2.0
* **Background scanning & cache** – PNGs are indexed in the background via `ScanWorker` on a `QThread`, and the cache is saved atomically to `cards.json` to avoid corruption
* **Smarter index fields** – Each card now tracks `filename`, `mtime`, `creator`, and `tags`; quick rescans update only changed files
* **Tag-aware search + new sort** – Search filters by name/creator/tags, and you can group by creator (with non-selectable headers)
* **UI polish**
  * Thumbnails are cached
  * Details pane got collapsible sections (Alternate Greetings) and linkified text
  * Horizontal scrollbars are disabled to keep layouts neat
  * Better selection handling (skip headers), delete confirmation, and status bar info (file size)
* **Context menu upgrades** – Added Duplicate Card, Export Metadata, and Save PNG As…
* **Quality-of-life** – Drag-and-drop to add PNGs; remembers last folder, geometry, theme, search, sort, and splitter sizes
* **Theme handling** – Light/Dark modes retained with tweaked styles; dark message boxes get a matching skin

### v1.4
* Added full tag search: You can now search for cards by tag from the main search bar (previously only name and creator were supported)

### v1.3
* Added “Save PNG As...” to right-click menu
* Improved dark/light mode switch, more consistent UI coloring
* Context menu and dialogs now follow theme
* DEL key support for quick delete
* Performance tweaks for large folders
* Version display and About dialog
* Improved error handling
* Numerous polish/UX tweaks

### v1.2
* Added creator sorting (grouped cards by creator)
* Remembers last folder, theme, sort mode, and search
* Card deletion now updates cache for instant response
* Drag & drop card adding (from anywhere)
* Improved metadata parsing

### v1.1
* Added light mode option
* Fast search bar (search by name, creator, tag)
* UI refinements and bug fixes

### v1.0
* Initial release: super-fast browsing, search, and preview for AI PNG cards
* Supports SFW/NSFW cards, with instant metadata view
