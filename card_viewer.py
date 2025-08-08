# card_viewer.py - Character Card Viewer v2.0

import sys
import os
import json
import base64
import shutil
import logging
import tempfile

from PIL import Image, ImageQt, PngImagePlugin
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QLabel, QPushButton, QListWidget, QVBoxLayout,
    QMessageBox, QScrollArea, QListWidgetItem, QSplitter, QLineEdit, QHBoxLayout, QStatusBar, QMenu, QFrame, QSizePolicy, QTextBrowser
)
from PySide6.QtCore import Qt, QEvent, QSettings, Signal, QObject, QThread, QSize
from PySide6.QtGui import QPixmap, QPalette, QColor, QDesktopServices, QAction, QCursor, QTextOption

__version__ = "2.0"

# -------------------------
# Logging
# -------------------------
LOG = logging.getLogger("CardViewer")
LOG.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
LOG.addHandler(_handler)

# -------------------------
# Theme helpers (kept as-is per user request)
# -------------------------

def enable_dark_mode(app):
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53,53,53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25,25,25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53,53,53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53,53,53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

def enable_light_mode(app):
    light_palette = QPalette()
    light_palette.setColor(QPalette.Window, QColor(245,245,245))
    light_palette.setColor(QPalette.WindowText, Qt.black)
    light_palette.setColor(QPalette.Base, QColor(255,255,255))
    light_palette.setColor(QPalette.AlternateBase, QColor(245,245,245))
    light_palette.setColor(QPalette.ToolTipBase, Qt.black)
    light_palette.setColor(QPalette.ToolTipText, Qt.white)
    light_palette.setColor(QPalette.Text, Qt.black)
    light_palette.setColor(QPalette.Button, QColor(232,232,232))
    light_palette.setColor(QPalette.ButtonText, Qt.black)
    light_palette.setColor(QPalette.BrightText, Qt.red)
    light_palette.setColor(QPalette.Link, QColor(0, 122, 204))
    light_palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
    light_palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(light_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #007acc; border: 1px solid #007acc; }")

DARK_EXTRA_STYLES = """
QPushButton {
    background-color: #232629;
    color: #fafbfc;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 10.5pt;
}

QMenu {
    background-color: #232629;
    color: #fafbfc;
    border: 1px solid #393f45;
    font-size: 10pt;
}
QMenu::item {
    background-color: transparent;
    padding: 4px 24px 4px 24px;
}
QMenu::item:selected {
    background-color: #355a7c;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background: #3a3a3a;
    margin-left: 10px;
    margin-right: 5px;
}

QPushButton:hover {
    background-color: #393f45;
    border: 1px solid #0078d7;
}
QPushButton:pressed {
    background-color: #15191b;
}
QPushButton:disabled {
    background-color: #292929;
    color: #6c6c6c;
    border: 1px solid #343434;
}
QLineEdit {
    background-color: #232629;
    color: #fafbfc;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 10.5pt;
}
QListWidget {
    background-color: #191b1c;
    color: #fafbfc;
    border: 1px solid #393f45;
    font-size: 10.5pt;
    selection-background-color: #355a7c;
    selection-color: #ffffff;
}
QListWidget::item {
    padding: 3px 0 3px 5px;
}
QScrollBar:vertical {
    background: #242424;
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #393f45;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}
QLabel[isHeader="true"] {
    color: #ffdf50;
    font-weight: bold;
}
QPushButton#DeleteCardBtn {
    color: #fff;
    background-color: #a83232;
    border: 1.5px solid #a83232;
    font-weight: bold;
}
QPushButton#DeleteCardBtn:hover {
    background-color: #d9534f;
    border: 1.5px solid #ff6c6c;
}

"""

LIGHT_EXTRA_STYLES = """
QPushButton {
    background-color: #f2f2f2;
    color: #212121;
    border: 1px solid #bbb;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 10.5pt;
}
QPushButton:hover {
    background-color: #e6f0fa;
    border: 1px solid #0078d7;
}
QPushButton:pressed {
    background-color: #dbeafd;
}
QPushButton:disabled {
    background-color: #ececec;
    color: #a0a0a0;
    border: 1px solid #d0d0d0;
}
QLineEdit {
    background-color: #fff;
    color: #212121;
    border: 1px solid #bbb;
    border-radius: 4px;
    padding: 5px 8px;
    font-size: 10.5pt;
}
QListWidget {
    background-color: #f7f7f7;
    color: #212121;
    border: 1px solid #e6e6e6;
    font-size: 10.5pt;
    selection-background-color: #e2eaff;
    selection-color: #00529b;
}
QListWidget::item {
    padding: 3px 0 3px 5px;
}
QScrollBar:vertical {
    background: #f0f0f0;
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #d0d0d0;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}
QLabel[isHeader="true"] {
    color: #b38800;
    font-weight: bold;
}
QPushButton#DeleteCardBtn {
    color: #fff;
    background-color: #d95454;
    border: 1.5px solid #a83232;
    font-weight: bold;
}
QPushButton#DeleteCardBtn:hover {
    background-color: #f26969;
    border: 1.5px solid #ff6c6c;
}
"""

def apply_messagebox_dark(msgbox):
    msgbox.setStyleSheet("""
        QMessageBox {
            background-color: #232629;
            color: #fafbfc;
        }
        QLabel {
            color: #fafbfc;
        }
        QPushButton {
            background-color: #393f45;
            color: #fafbfc;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 6px 10px;
            min-width: 60px;
        }
        QPushButton:hover {
            background-color: #355a7c;
            color: #fff;
        }
    """)

# -------------------------
# Metadata helpers
# -------------------------

def read_card_metadata(filepath):
    """
    Unified function to read character card metadata from a PNG.
    Supports 'chara' and 'ccv3' keys. If a nested 'data' dict exists,
    merge it without clobbering top-level keys.
    Returns: (metadata_dict or None, error_str or None)
    """
    try:
        with PngImagePlugin.PngImageFile(filepath) as im:
            text_chunks = im.text
            b64 = text_chunks.get('chara') or text_chunks.get('ccv3')
            if not b64:
                return None, "No character card metadata found"
            try:
                data = json.loads(base64.b64decode(b64).decode('utf-8'))
            except Exception as e:
                return None, f"Decode error: {e}"
            if "data" in data and isinstance(data["data"], dict):
                # Non-destructive merge: nested data fills in missing top-level keys only
                merged = dict(data)
                for k, v in data["data"].items():
                    if k not in merged:
                        merged[k] = v
                data = merged
            return data, None
    except Exception as e:
        LOG.exception("Error reading metadata for %s", filepath)
        return None, str(e)

def get_basic_index_info(filepath):
    """
    Get lightweight info needed for index: creator, tags.
    Uses read_card_metadata() but avoids heavy processing elsewhere.
    """
    meta, _ = read_card_metadata(filepath)
    creator = "Unknown"
    tags = []
    if meta:
        creator = meta.get("creator") or "Unknown"
        t = meta.get("tags", [])
        if isinstance(t, list):
            tags = t
    return creator, tags

def atomic_write_json(path, data):
    """Write JSON atomically to avoid corruption."""
    dirpath = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".cards_tmp_", dir=dirpath, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        # Clean up temp file if replace failed
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise

def get_png_files(folder):
    return sorted([f for f in os.listdir(folder) if f.lower().endswith('.png')])

def format_filesize(nbytes):
    for unit in ["B","KB","MB","GB"]:
        if nbytes < 1024.0:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024.0
    return f"{nbytes:.1f} TB"

# -------------------------
# Background worker
# -------------------------

class ScanWorker(QObject):
    progress = Signal(int, int)  # processed, total
    updated_entries = Signal(list)  # list of new/updated index entries
    finished = Signal()

    def __init__(self, folder, tasks):
        super().__init__()
        self.folder = folder
        self.tasks = tasks  # list of file names to (re)scan

    def run(self):
        new_entries = []
        total = len(self.tasks)
        for i, fname in enumerate(self.tasks, 1):
            try:
                fpath = os.path.join(self.folder, fname)
                mtime = int(os.path.getmtime(fpath))
                creator, tags = get_basic_index_info(fpath)
                new_entries.append({
                    "filename": fname,
                    "mtime": mtime,
                    "creator": creator,
                    "tags": tags
                })
            except Exception:
                LOG.exception("Failed scanning %s", fname)
            self.progress.emit(i, total)
        self.updated_entries.emit(new_entries)
        self.finished.emit()

# -------------------------
# UI Widgets
# -------------------------

class CardDetails(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.image_label = QLabel()
        self.image_label.setFixedSize(180, 220)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        self.meta_area = QScrollArea()
        self.meta_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.meta_area.setWidgetResizable(True)
        self.meta_widget = QWidget()
        self.meta_layout = QVBoxLayout()
        self.meta_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.meta_widget.setLayout(self.meta_layout)
        self.meta_area.setWidget(self.meta_widget)
        layout.addWidget(self.meta_area)

        self.delete_btn = QPushButton("Delete Card")
        self.delete_btn.setObjectName("DeleteCardBtn")
        self.delete_btn.setEnabled(False)
        layout.addWidget(self.delete_btn, alignment=Qt.AlignmentFlag.AlignLeft)


        self.setLayout(layout)
       


    def show_info_message(self, text, error=False):
        # Clear out all previous widgets
        color = "red" if error else "#888"
        label = QLabel(f"<span style='color:{color}'><i>{text}</i></span>")
        label.setWordWrap(True)
        self.meta_layout.addWidget(label)
        self.delete_btn.setEnabled(False)

    def show_image(self, pixmap: QPixmap | None):
        if pixmap is None:
            self.image_label.clear()
        else:
            self.image_label.setPixmap(pixmap)

    @staticmethod
    def _linkify(text: str) -> str:
        # very basic linkify for http(s) and mailto
        import re
        def repl(match):
            url = match.group(0)
            return f'<a href="{url}">{url}</a>'
        # http/https
        text = re.sub(r'(https?://[^\s<]+)', repl, text)
        # mailto
        text = re.sub(r'(mailto:[^\s<]+)', repl, text)
        return text
    
    def _add_collapsible_section(self, title: str):
        """Returns the inner VBoxLayout you can add widgets to."""
        # make them children of the scroll area's content widget
        btn = QPushButton(f"{title} ▸", parent=self.meta_widget)
        btn.setCheckable(True)
        btn.setChecked(False)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        container = QWidget(parent=self.meta_widget)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        inner = QVBoxLayout()
        inner.setContentsMargins(16, 4, 0, 6)  # small indent
        inner.setSpacing(4)
        container.setLayout(inner)
        container.setVisible(False)

        def on_toggle(checked: bool):
            container.setVisible(checked)
            btn.setText(f"{title} {'▾' if checked else '▸'}")
        btn.toggled.connect(on_toggle)

        self.meta_layout.addWidget(btn)
        self.meta_layout.addWidget(container)
        return inner

    def _clear_metadata(self):
        while self.meta_layout.count():
            item = self.meta_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


    def show_metadata(self, meta, clickable_links=True):
        for i in reversed(range(self.meta_layout.count())):
            widget = self.meta_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        def add_field(label, value):
            if value is None or value == "" or value == "none":
                return
            l = QLabel(f"<b>{label}:</b>")
            l.setWordWrap(True)
            self.meta_layout.addWidget(l)
            v = QLabel()
            v.setWordWrap(True)
            if isinstance(value, list):
                value = ", ".join(map(str, value))
            value_str = str(value)
            if clickable_links:
                v.setTextFormat(Qt.TextFormat.RichText)
                v.setOpenExternalLinks(True)
                v.setText(self._linkify(value_str))
            else:
                v.setText(value_str)
            self.meta_layout.addWidget(v)

        if not meta:
            l = QLabel("<span style='color:red'>Could not load card metadata.</span>")
            self.meta_layout.addWidget(l)
            self.delete_btn.setEnabled(False)
            return
            
        self._clear_metadata()
        
        add_field("Name", meta.get("name"))
        add_field("Creator", meta.get("creator"))
        add_field("Description", meta.get("description"))
        add_field("Personality", meta.get("personality"))
        add_field("Scenario", meta.get("scenario"))
        add_field("First Message", meta.get("first_mes"))
        # --- Alternate Greetings ---
        alt = meta.get("alternate_greetings")
        if isinstance(alt, list) and alt:
            hdr = QLabel(f"<b>Alternate Greetings ({len(alt)})</b>")
            hdr.setWordWrap(True)
            self.meta_layout.addWidget(hdr)

            for i, g in enumerate(alt, 1):
                title = QLabel(f"Alternate Greeting {i}")
                title.setWordWrap(True)
                self.meta_layout.addWidget(title)

                tb = QTextBrowser()                                # was QTextBrowser(parent=self.meta_widget)
                tb.setReadOnly(True)
                tb.setOpenExternalLinks(True)
                tb.setFrameShape(QFrame.NoFrame)
                tb.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                tb.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                tb.setLineWrapMode(QTextBrowser.WidgetWidth)
                tb.setWordWrapMode(QTextOption.WrapAnywhere)
                tb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)  # add this
                tb.setMaximumHeight(220)
                tb.setHtml(self._linkify(str(g)))
                self.meta_layout.addWidget(tb)


        # Post-history instructions (simple text field)
        phi = meta.get("post_history_instructions")
        if phi:
            add_field("Post-History Instructions", phi)

        add_field("Example Dialogue", meta.get("mes_example"))
        add_field("Tags", meta.get("tags", []))
        add_field("Talkativeness", meta.get("talkativeness"))
        add_field("Favorite", "Yes" if meta.get("fav") else "")
        add_field("Creator Comment", meta.get("creatorcomment") or meta.get("creator_notes"))
        add_field("Chat", meta.get("chat"))
        add_field("Card Version", meta.get("character_version"))
        add_field("Spec", meta.get("spec"))
        add_field("Spec Version", meta.get("spec_version"))
        add_field("Create Date", meta.get("create_date"))
        
        self.delete_btn.setEnabled(True)


class CardViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Character Card Viewer v{__version__}")
        self.resize(900, 540)

        # State
        self.folder = ""
        self.cards_index = []  # list of dicts: filename, mtime, creator, tags
        self.file_index_map = {}
        self.thumb_cache: dict[str, QPixmap] = {}  # in-memory thumbnail cache
        self._scan_thread: QThread | None = None

        # Settings
        self.settings = QSettings("CardViewer", "Deluxe")
        self.last_folder = self.settings.value("last_folder", "")
        self.sort_mode = self.settings.value("sort_mode", "name")  # name | creator
        if self.sort_mode not in ("name", "creator"):
            self.sort_mode = "name"
        self.last_search = self.settings.value("last_search", "")
        self.is_dark_mode = self.settings.value("dark_mode", "1") == "1"
        if self.settings.value("window_geometry"):
            self.restoreGeometry(self.settings.value("window_geometry"))

        # UI layout
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        self.left_panel = QVBoxLayout(left_widget)

        btn_row = QHBoxLayout()
        btn_open = QPushButton("Open Card Folder")
        btn_open.clicked.connect(self.select_folder)
        btn_row.addWidget(btn_open)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_folder)
        btn_row.addWidget(self.refresh_btn)

        self.toggle_mode_button = QPushButton("Light Mode" if self.is_dark_mode else "Dark Mode")
        self.toggle_mode_button.clicked.connect(self.toggle_dark_mode)
        btn_row.addWidget(self.toggle_mode_button)

        self.left_panel.addLayout(btn_row)

        # Sorting buttons (fixed row, no re-parenting)
        self.sort_by_name_btn = QPushButton("Sort by Name")
        self.sort_by_creator_btn = QPushButton("Group by Creator")
        self.sort_by_name_btn.clicked.connect(lambda: self.set_sort_mode('name'))
        self.sort_by_creator_btn.clicked.connect(lambda: self.set_sort_mode('creator'))

        sort_row = QHBoxLayout()
        sort_row.addWidget(self.sort_by_name_btn)
        sort_row.addWidget(self.sort_by_creator_btn)
        self.left_panel.addLayout(sort_row)


        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by name, creator, tag...")
        self.search_bar.setText(self.last_search)
        self.search_bar.textChanged.connect(self.update_listbox)
        self.left_panel.addWidget(self.search_bar)

        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet("color: gray;")
        self.left_panel.addWidget(self.folder_label)

        self.listbox = QListWidget()
        self.listbox.setMinimumWidth(180)
        self.listbox.setMaximumWidth(400)
        self.listbox.itemSelectionChanged.connect(self._fix_selection)
        self.left_panel.addWidget(self.listbox)
        self.listbox.installEventFilter(self)
        self.listbox.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listbox.customContextMenuRequested.connect(self.show_context_menu)
        self.listbox.setAcceptDrops(True)
        left_widget.setAcceptDrops(True)

        main_splitter.addWidget(left_widget)

        self.details = CardDetails()
        main_splitter.addWidget(self.details)
        main_splitter.setStretchFactor(1, 1)
        self.setCentralWidget(main_splitter)

        # Restore splitter sizes if any
        sizes_json = self.settings.value("splitter_sizes")
        if sizes_json:
            try:
                sizes = json.loads(sizes_json)
                main_splitter.setSizes(sizes)
            except Exception:
                pass

        # Connect details buttons
        self.details.delete_btn.clicked.connect(self.delete_card)

        # Status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Accept drops
        self.setAcceptDrops(True)
        self.listbox.viewport().setAcceptDrops(True)

        # Style (init)
        app = QApplication.instance()
        if self.is_dark_mode:
            enable_dark_mode(app)
            app.setStyleSheet(DARK_EXTRA_STYLES)
        else:
            enable_light_mode(app)
            app.setStyleSheet(LIGHT_EXTRA_STYLES)

        # Load last folder quickly using cache
        if self.last_folder and os.path.isdir(self.last_folder):
            self.folder = self.last_folder
            self.folder_label.setText(self.folder)
            self.load_or_update_index_cache(force_refresh=False)
            self.update_listbox()

        # Keep ref to splitter for saving sizes on close
        self._splitter = main_splitter

    def closeEvent(self, event):
        self.settings.setValue("last_folder", self.folder)
        self.settings.setValue("sort_mode", self.sort_mode)
        self.settings.setValue("last_search", self.search_bar.text())
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("dark_mode", "1" if self.is_dark_mode else "0")
        # Save splitter sizes
        if self._splitter:
            try:
                sizes = self._splitter.sizes()
                self.settings.setValue("splitter_sizes", json.dumps(sizes))
            except Exception:
                pass
                
        # Ensure background scan thread exits cleanly
        try:
            if self._scan_thread and self._scan_thread.isRunning():
                self._scan_thread.quit()
                self._scan_thread.wait(2000)  # up to 2s for a clean stop
        except Exception:
            pass
            
        super().closeEvent(event)

    # -------------------------
    # Sorting & filtering
    # -------------------------
    def set_sort_mode(self, mode):
        if mode not in ("name", "creator"):
            mode = "name"
        self.sort_mode = mode
        # Visual feedback: disable the active one
        self.sort_by_name_btn.setEnabled(mode != "name")
        self.sort_by_creator_btn.setEnabled(mode != "creator")
        self.update_listbox()


    def update_listbox(self):
        filter_text = self.search_bar.text().strip().lower()
        self.file_index_map = {}
        self.listbox.clear()
        items_added = 0

        entries = list(self.cards_index)

        if self.sort_mode == 'name':
            entries.sort(key=lambda e: e['filename'].lower())
            for i, entry in enumerate(entries):
                fname = entry['filename']
                creator = entry.get('creator', 'Unknown') or "Unknown"
                tags = entry.get('tags', [])
                meta_match = (
                    (filter_text in fname.lower())
                    or (filter_text in creator.lower())
                    or any(filter_text in (t or "").lower() for t in tags)
                ) if filter_text else True
                if not meta_match:
                    continue
                item = QListWidgetItem(fname)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.listbox.addItem(item)
                self.file_index_map[self.listbox.count() - 1] = self.cards_index.index(entry)
                items_added += 1

        elif self.sort_mode == 'creator':
            # Group by creator
            creator_map = {}
            for entry in entries:
                creator = entry.get("creator", "Unknown") or "Unknown"
                creator_map.setdefault(creator, []).append(entry)

            for creator in sorted(creator_map, key=lambda s: s.lower()):
                group = creator_map[creator]
                # filter group
                filtered = []
                for entry in group:
                    fname = entry['filename']
                    tags = entry.get('tags', [])
                    meta_match = (
                        (filter_text in fname.lower())
                        or (filter_text in creator.lower())
                        or any(filter_text in (t or "").lower() for t in tags)
                    ) if filter_text else True
                    if meta_match:
                        filtered.append(entry)
                if not filtered:
                    continue
                header = QListWidgetItem(creator)
                header.setFlags(header.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled)
                font = header.font()
                font.setBold(True)
                header.setFont(font)
                header.setData(Qt.UserRole, "header")
                self.listbox.addItem(header)
                for entry in sorted(filtered, key=lambda e: e['filename'].lower()):
                    item = QListWidgetItem("    " + entry['filename'])
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    self.listbox.addItem(item)
                    self.file_index_map[self.listbox.count() - 1] = self.cards_index.index(entry)
                    items_added += 1


        # Auto-select first selectable item (skip headers)
        self._fix_selection()
        mode_label = "Sort by Name" if self.sort_mode == "name" else "Group by Creator"
        self.statusbar.showMessage(f"{items_added} card(s) | Mode: {mode_label}")


    def _fix_selection(self, force=False):
        row = self.listbox.currentRow()
        if row == -1:
            # Try selecting first selectable item
            for idx in range(self.listbox.count()):
                item = self.listbox.item(idx)
                if item and (item.flags() & Qt.ItemFlag.ItemIsSelectable):
                    self.listbox.setCurrentRow(idx)
                    break
            row = self.listbox.currentRow()
            if row == -1:
                self.details.show_image(None)
                self.details.show_metadata(None)
                self.statusbar.clearMessage()
                return

        item = self.listbox.item(row)
        if item and (item.flags() & Qt.ItemFlag.ItemIsSelectable):
            self.show_card()
            return

        # Move to next selectable
        next_row = row + 1
        while next_row < self.listbox.count():
            item = self.listbox.item(next_row)
            if item and (item.flags() & Qt.ItemFlag.ItemIsSelectable):
                self.listbox.setCurrentRow(next_row)
                self.show_card()
                return
            next_row += 1

        # Move to previous selectable
        prev_row = row - 1
        while prev_row >= 0:
            item = self.listbox.item(prev_row)
            if item and (item.flags() & Qt.ItemFlag.ItemIsSelectable):
                self.listbox.setCurrentRow(prev_row)
                self.show_card()
                return
            prev_row -= 1

        self.listbox.setCurrentRow(-1)
        self.details.show_image(None)
        self.details.show_metadata(None)
        self.statusbar.clearMessage()

    # -------------------------
    # Keyboard & Events
    # -------------------------
    def eventFilter(self, obj, event):
        if obj is self.listbox:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Delete:
                    self.delete_card()
                    return True
                if event.key() in (Qt.Key_Down, Qt.Key_Up):
                    self._fix_selection(force=True)
                    return False
        return super().eventFilter(obj, event)

    # -------------------------
    # Folder / Cache management
    # -------------------------
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Card Folder")
        if not folder:
            return
        self.open_folder(folder)

    def open_folder(self, folder):
        self.folder = folder
        self.folder_label.setText(folder)
        self.settings.setValue("last_folder", folder)
        self.thumb_cache.clear()  # thumbnails are per-session
        self.load_or_update_index_cache(force_refresh=False)
        self.update_listbox()

    def refresh_folder(self):
        if not self.folder:
            return
        self.statusbar.showMessage("Scanning changed cards in background...")
        self.details.show_info_message("Scanning cards and updating cache...")
        QApplication.processEvents()
        self.load_or_update_index_cache(force_refresh=True)  # force check for changes
        self.update_listbox()
        self.statusbar.clearMessage()

    def load_or_update_index_cache(self, force_refresh=False):
        if not self.folder:
            return
        pngs = get_png_files(self.folder)
        cache_file = os.path.join(self.folder, "cards.json")

        # Load cached
        cached = []
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
            except Exception:
                LOG.exception("Failed to read cards.json")

        cached_lookup = {entry['filename']: entry for entry in cached if 'filename' in entry and 'mtime' in entry}

        # Build current list using cache where possible
        new_cards_index = []
        to_rescan = []

        for fname in pngs:
            fpath = os.path.join(self.folder, fname)
            try:
                mtime = int(os.path.getmtime(fpath))
            except Exception:
                continue
            cached_entry = cached_lookup.get(fname)
            if cached_entry and cached_entry.get('mtime') == mtime and not force_refresh:
                new_cards_index.append(cached_entry)
            else:
                # We'll add a placeholder and rescan in background
                new_cards_index.append({
                    "filename": fname,
                    "mtime": mtime,
                    "creator": cached_entry.get("creator", "Unknown") if cached_entry else "Unknown",
                    "tags": cached_entry.get("tags", []) if cached_entry else []
                })
                to_rescan.append(fname)

        # Remove deleted files
        cached_filenames = set(cached_lookup.keys())
        current_filenames = set(pngs)
        removed = list(cached_filenames - current_filenames)
        if removed:
            LOG.info("Removed %d missing entries from cache", len(removed))

        self.cards_index = new_cards_index

        # Save cache immediately (quick write) to reflect removals/additions
        try:
            atomic_write_json(cache_file, self.cards_index)
        except Exception:
            LOG.exception("Failed to save initial cards.json")

        # If there are rescans to do, do them in background
        if to_rescan:
            # kill existing scan thread if any
            if self._scan_thread and self._scan_thread.isRunning():
                # Let it finish naturally to avoid crashes; in a more advanced version we could cancel
                pass
            self._scan_thread = QThread()
            worker = ScanWorker(self.folder, to_rescan)
            worker.moveToThread(self._scan_thread)
            self._scan_thread.started.connect(worker.run)
            worker.progress.connect(self._on_scan_progress)
            worker.updated_entries.connect(self._on_scan_updated_entries)
            worker.finished.connect(self._scan_thread.quit)
            worker.finished.connect(worker.deleteLater)
            self._scan_thread.finished.connect(self._scan_thread.deleteLater)
            self._scan_thread.start()

    def _on_scan_progress(self, i, total):
        self.statusbar.showMessage(f"Scanning cards... {i}/{total}")

    def _on_scan_updated_entries(self, entries):
        # Update cards_index with new info
        lookup = {e['filename']: e for e in self.cards_index}
        for e in entries:
            lookup[e['filename']] = e
        self.cards_index = list(lookup.values())
        # Save updated cache atomically
        try:
            atomic_write_json(os.path.join(self.folder, "cards.json"), self.cards_index)
        except Exception:
            LOG.exception("Failed to save cards.json after scan")
        # Refresh list if user is on matching sort/filter
        self.update_listbox()
        self.statusbar.clearMessage()

    # -------------------------
    # Card display
    # -------------------------
    def _get_thumbnail(self, fpath) -> QPixmap | None:
        # In-memory cache for session
        if fpath in self.thumb_cache:
            return self.thumb_cache[fpath]
        try:
            im = Image.open(fpath)
            im = im.resize((180, 220), Image.LANCZOS)
            qtimg = ImageQt.ImageQt(im)
            pix = QPixmap.fromImage(qtimg)
            self.thumb_cache[fpath] = pix
            return pix
        except Exception:
            return None

    def show_card(self):
        idx = self.listbox.currentRow()
        if idx == -1 or idx not in self.file_index_map:
            self.details.show_image(None)
            self.details.show_metadata(None)
            self.statusbar.clearMessage()
            return
        meta_idx = self.file_index_map[idx]
        if meta_idx < 0 or meta_idx >= len(self.cards_index):
            self.details.show_image(None)
            self.details.show_metadata(None)
            self.statusbar.clearMessage()
            return
        entry = self.cards_index[meta_idx]
        fname = entry['filename']
        fpath = os.path.join(self.folder, fname)

        pix = self._get_thumbnail(fpath)
        self.details.show_image(pix)

        card, error = read_card_metadata(fpath)
        self.details.show_metadata(card)
        creator = entry.get('creator', 'Unknown')
        # Show file size in status for a bit more info
        try:
            size = os.path.getsize(fpath)
            self.statusbar.showMessage(f"{fname} | {creator} | {format_filesize(size)}")
        except Exception:
            self.statusbar.showMessage(f"{fname} | {creator}")

    # -------------------------
    # Actions
    # -------------------------
    def delete_card(self):
        idx = self.listbox.currentRow()
        if idx == -1 or idx not in self.file_index_map:
            return
        meta_idx = self.file_index_map[idx]
        if meta_idx < 0 or meta_idx >= len(self.cards_index):
            return
        entry = self.cards_index[meta_idx]
        fname = entry['filename']
        fpath = os.path.join(self.folder, fname)
        confirm = QMessageBox.question(
            self, "Delete Card",
            f"Delete '{fname}'?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                os.remove(fpath)
                # Update index and save
                del self.cards_index[meta_idx]
                atomic_write_json(os.path.join(self.folder, "cards.json"), self.cards_index)
                # Update UI
                self.update_listbox()
                self.details.show_image(None)
                self.details.show_metadata(None)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete file:\n{e}")

    def duplicate_card(self, fpath):
        # Create "name (copy).png", "name (copy 2).png", etc.
        base = os.path.splitext(os.path.basename(fpath))[0]
        ext = ".png"
        candidate = f"{base} (copy){ext}"
        i = 2
        while os.path.exists(os.path.join(self.folder, candidate)):
            candidate = f"{base} (copy {i}){ext}"
            i += 1
        dst = os.path.join(self.folder, candidate)
        try:
            shutil.copy2(fpath, dst)
            # Update cache quickly
            mtime = int(os.path.getmtime(dst))
            creator, tags = get_basic_index_info(dst)
            self.cards_index.append({
                "filename": candidate,
                "mtime": mtime,
                "creator": creator,
                "tags": tags
            })
            atomic_write_json(os.path.join(self.folder, "cards.json"), self.cards_index)
            self.update_listbox()
            self.statusbar.showMessage(f"Duplicated to: {candidate}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not duplicate file:\n{e}")


    # --- Drag & drop support ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".png"):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        self.dragEnterEvent(event)

    def dropEvent(self, event):
        if not self.folder:
            QMessageBox.warning(self, "No Folder", "Select a folder first!")
            return
        files_added = 0
        for url in event.mimeData().urls():
            src = url.toLocalFile()
            if src.lower().endswith(".png"):
                dst = os.path.join(self.folder, os.path.basename(src))
                if os.path.abspath(src) != os.path.abspath(dst):
                    try:
                        shutil.copy2(src, dst)
                        files_added += 1
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Could not copy file:\n{e}")
        if files_added:
            self.load_or_update_index_cache(force_refresh=True)
            self.update_listbox()
            self.statusbar.showMessage(f"Added {files_added} card(s).")

    # --- Context menu on right click ---
    def show_context_menu(self, pos):
        idx = self.listbox.indexAt(pos).row()
        # Always allow About, even when not on a card
        menu = QMenu()

        about_action = QAction("About", self)
        def do_about():
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("About")
            msg.setText(f"Character Card Viewer\nVersion: {__version__}\n\ngithub.com/kaosnews/CardViewer")
            if self.is_dark_mode:
                apply_messagebox_dark(msg)
            msg.exec()

        about_action.triggered.connect(do_about)

        if idx == -1 or idx not in self.file_index_map:
            menu.addAction(about_action)
            menu.exec(QCursor.pos())
            return

        meta_idx = self.file_index_map[idx]
        entry = self.cards_index[meta_idx]
        fname = entry['filename']
        fpath = os.path.join(self.folder, fname)

        open_action = QAction("Open in Default Viewer", self)
        export_action = QAction("Export Metadata...", self)
        save_as_action = QAction("Save PNG As...", self)
        duplicate_action = QAction("Duplicate Card", self)

        def do_open():
            QDesktopServices.openUrl(f"file:///{os.path.abspath(fpath)}")

        def do_export():
            card, error = read_card_metadata(fpath)
            if not card:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Export")
                msg.setText("No metadata found.")
                if self.is_dark_mode:
                    apply_messagebox_dark(msg)
                msg.exec()
                return
            outname, _ = QFileDialog.getSaveFileName(
                self, "Export Metadata",
                fname.replace('.png', '.json'),
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
            )
            if outname:
                try:
                    with open(outname, "w", encoding="utf-8") as f:
                        json.dump(card, f, ensure_ascii=False, indent=2)
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Export")
                    msg.setText(f"Metadata exported to {outname}")
                    if self.is_dark_mode:
                        apply_messagebox_dark(msg)
                    msg.exec()
                except Exception as e:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Export Error")
                    msg.setText(f"Failed to export: {e}")
                    if self.is_dark_mode:
                        apply_messagebox_dark(msg)
                    msg.exec()

        def do_save_as():
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save PNG As", fname, "PNG Files (*.png)"
            )
            if save_path:
                try:
                    shutil.copy2(fpath, save_path)
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Save PNG")
                    msg.setText(f"Saved as: {save_path}")
                    if self.is_dark_mode:
                        apply_messagebox_dark(msg)
                    msg.exec()
                except Exception as e:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Error")
                    msg.setText(f"Could not save file:\n{e}")
                    if self.is_dark_mode:
                        apply_messagebox_dark(msg)
                    msg.exec()

        def do_duplicate():
            self.duplicate_card(fpath)

        open_action.triggered.connect(do_open)
        export_action.triggered.connect(do_export)
        save_as_action.triggered.connect(do_save_as)
        duplicate_action.triggered.connect(do_duplicate)

        menu.addAction(open_action)
        menu.addAction(export_action)
        menu.addAction(save_as_action)
        menu.addAction(duplicate_action)
        menu.addSeparator()
        menu.addAction(about_action)

        menu.exec(QCursor.pos())

    # -------------------------
    # Theme
    # -------------------------
    def toggle_dark_mode(self):
        app = QApplication.instance()
        if self.is_dark_mode:
            enable_light_mode(app)
            app.setStyleSheet(LIGHT_EXTRA_STYLES)
            self.toggle_mode_button.setText("Dark Mode")
            self.is_dark_mode = False
        else:
            enable_dark_mode(app)
            app.setStyleSheet(DARK_EXTRA_STYLES)
            self.toggle_mode_button.setText("Light Mode")
            self.is_dark_mode = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = QSettings("CardViewer", "Deluxe")
    is_dark_mode = settings.value("dark_mode", "1") == "1"
    if is_dark_mode:
        enable_dark_mode(app)
        app.setStyleSheet(DARK_EXTRA_STYLES)
    else:
        enable_light_mode(app)
        app.setStyleSheet(LIGHT_EXTRA_STYLES)
    viewer = CardViewer()
    viewer.show()
    sys.exit(app.exec())
