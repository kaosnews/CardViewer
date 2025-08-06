# CardViewer

**A simple viewer for AI character cards (PNG-based). Instantly browse, search, preview, and manage thousands of character cards, with support for SFW/NSFW and advanced sorting.**

---

## Features

* **Lightning-fast loading:** Handles thousands of cards in a snap.
* **PNG card preview:** See card images and metadata instantly.
* **Dark & Light mode:** Switch themes any time.
* **Sort by name or creator:** Toggle with one click.
* **Smart search:** Find cards by name, creator, or tag.
* **Drag & drop add:** Drop PNG files right into your folder.
* **Right-click menu:** Open, export metadata, or “Save PNG As...” anywhere.
* **Remembers your settings:** Theme, folder, search, window size.

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

### v1.3 — *2025-08-06*

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

