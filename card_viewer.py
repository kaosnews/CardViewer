import sys
import os
import json
import base64
import shutil
from PIL import Image, ImageQt, PngImagePlugin
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QLabel, QPushButton, QListWidget, QVBoxLayout,
    QMessageBox, QScrollArea, QListWidgetItem, QSplitter, QLineEdit, QHBoxLayout, QStatusBar, QMenu
)
from PySide6.QtCore import Qt, QEvent, QSettings
from PySide6.QtGui import QPixmap, QPalette, QColor, QDesktopServices, QAction, QCursor
__version__ = "1.4"

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

def get_creator_from_png(filepath):
    try:
        with PngImagePlugin.PngImageFile(filepath) as im:
            text_chunks = im.text
            b64 = text_chunks.get('chara') or text_chunks.get('ccv3')
            if b64:
                data = json.loads(base64.b64decode(b64).decode('utf-8'))
                if "data" in data and isinstance(data["data"], dict):
                    data = {**data, **data["data"]}
                creator = data.get("creator", "")
                return creator or "Unknown"
    except Exception:
        pass
    return "Unknown"

def extract_card_metadata(filepath):
    try:
        with PngImagePlugin.PngImageFile(filepath) as im:
            text_chunks = im.text
            b64 = text_chunks.get('chara') or text_chunks.get('ccv3')
            if b64:
                data = json.loads(base64.b64decode(b64).decode('utf-8'))
                if "data" in data and isinstance(data["data"], dict):
                    data = {**data, **data["data"]}
                return data, None
    except Exception as e:
        return None, str(e)
    return None, "No character card metadata found"

def get_tags_from_png(filepath):
    try:
        with PngImagePlugin.PngImageFile(filepath) as im:
            text_chunks = im.text
            b64 = text_chunks.get('chara') or text_chunks.get('ccv3')
            if b64:
                data = json.loads(base64.b64decode(b64).decode('utf-8'))
                if "data" in data and isinstance(data["data"], dict):
                    data = {**data, **data["data"]}
                tags = data.get("tags", [])
                return tags if isinstance(tags, list) else []
    except Exception:
        pass
    return []


def get_png_files(folder):
    return sorted([f for f in os.listdir(folder) if f.lower().endswith('.png')])

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
        for i in reversed(range(self.meta_layout.count())):
            widget = self.meta_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Style: error gets red, info gets italic gray
        color = "red" if error else "#888"
        label = QLabel(f"<span style='color:{color}'><i>{text}</i></span>")
        label.setWordWrap(True)
        self.meta_layout.addWidget(label)
        self.delete_btn.setEnabled(False)
    
    def show_image(self, filepath):
        try:
            im = Image.open(filepath)
            im = im.resize((180, 220), Image.LANCZOS)
            qtimg = ImageQt.ImageQt(im)
            pix = QPixmap.fromImage(qtimg)
            self.image_label.setPixmap(pix)
        except Exception:
            self.image_label.clear()

    def show_metadata(self, meta):
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
            v = QLabel(str(value))
            v.setWordWrap(True)
            self.meta_layout.addWidget(v)
        if not meta:
            l = QLabel("<span style='color:red'>Could not load card metadata.</span>")
            self.meta_layout.addWidget(l)
            self.delete_btn.setEnabled(False)
            return
        add_field("Name", meta.get("name"))
        add_field("Creator", meta.get("creator"))
        add_field("Description", meta.get("description"))
        add_field("Personality", meta.get("personality"))
        add_field("Scenario", meta.get("scenario"))
        add_field("First Message", meta.get("first_mes"))
        add_field("Example Dialogue", meta.get("mes_example"))
        add_field("Tags", ", ".join(meta.get("tags", [])))
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
        self.folder = ""
        self.cards_index = []
        self.file_index_map = {}
        self.settings = QSettings("CardViewer", "Deluxe")
        self.last_folder = self.settings.value("last_folder", "")
        self.sort_mode = self.settings.value("sort_mode", "name")
        self.last_search = self.settings.value("last_search", "")
        self.is_dark_mode = self.settings.value("dark_mode", "1") == "1"
        if self.settings.value("window_geometry"):
            self.restoreGeometry(self.settings.value("window_geometry"))
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
        self.sort_by_name_btn = QPushButton("Sort by Name")
        self.sort_by_creator_btn = QPushButton("Sort by Creator")
        self.sort_by_name_btn.clicked.connect(lambda: self.set_sort_mode('name'))
        self.sort_by_creator_btn.clicked.connect(lambda: self.set_sort_mode('creator'))
        if self.sort_mode == "name":
            self.left_panel.addWidget(self.sort_by_creator_btn)
        else:
            self.left_panel.addWidget(self.sort_by_name_btn)
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
        self.details.delete_btn.clicked.connect(self.delete_card)
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
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
        if self.last_folder and os.path.isdir(self.last_folder):
            self.folder = self.last_folder
            self.folder_label.setText(self.folder)
            self.load_or_update_index_cache()
            self.update_listbox()
    def closeEvent(self, event):
        self.settings.setValue("last_folder", self.folder)
        self.settings.setValue("sort_mode", self.sort_mode)
        self.settings.setValue("last_search", self.search_bar.text())
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("dark_mode", "1" if self.is_dark_mode else "0")
        super().closeEvent(event)
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
    def set_sort_mode(self, mode):
        if mode == 'name':
            self.sort_mode = 'name'
            self.sort_by_name_btn.setParent(None)
            self.left_panel.insertWidget(3, self.sort_by_creator_btn)
        else:
            self.sort_mode = 'creator'
            self.sort_by_creator_btn.setParent(None)
            self.left_panel.insertWidget(3, self.sort_by_name_btn)
        self.update_listbox()
    def eventFilter(self, obj, event):
        if obj is self.listbox and hasattr(event, "type") and callable(event.type):
            if event.type() == QEvent.KeyPress:
                if hasattr(event, "key") and callable(event.key):
                    if event.key() == Qt.Key_Delete:
                        self.delete_card()
                        return True
                    if event.key() in (Qt.Key_Down, Qt.Key_Up):
                        self._fix_selection(force=True)
                        return False
        return super().eventFilter(obj, event)
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Card Folder")
        if not folder:
            return
        self.folder = folder
        self.folder_label.setText(folder)
        self.settings.setValue("last_folder", folder)
        self.load_or_update_index_cache()   # <- correct call here!
        self.update_listbox()

    def refresh_folder(self):
        if not self.folder:
            return
        self.statusbar.showMessage("Scanning cards and building cache...")
        self.details.show_info_message("Scanning cards and building cache...")
        QApplication.processEvents()
        self.load_or_update_index_cache(force_refresh=True)
        self.update_listbox()
        self.statusbar.clearMessage()

    def load_or_update_index_cache(self, force_refresh=False):
        pngs = get_png_files(self.folder)
        cache_file = os.path.join(self.folder, "cards.json")
        need_resave = force_refresh
        if os.path.exists(cache_file) and not force_refresh:
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
            except Exception:
                cached = []
        else:
            cached = []
        cached_lookup = {entry['filename']: entry for entry in cached if 'filename' in entry and 'mtime' in entry}
        new_cards_index = []
        for fname in pngs:
            fpath = os.path.join(self.folder, fname)
            mtime = int(os.path.getmtime(fpath))
            cached_entry = cached_lookup.get(fname)
            if cached_entry and cached_entry['mtime'] == mtime and 'tags' in cached_entry:
                new_cards_index.append(cached_entry)
            else:
                creator = get_creator_from_png(fpath)
                tags = get_tags_from_png(fpath)
                new_cards_index.append({
                    "filename": fname,
                    "mtime": mtime,
                    "creator": creator,
                    "tags": tags
                })
                need_resave = True
        if len(new_cards_index) != len(cached):
            need_resave = True
        self.cards_index = new_cards_index
        if need_resave or not os.path.exists(cache_file):
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(self.cards_index, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print("Failed to save cards.json:", e)

    def update_listbox(self):
        filter_text = self.search_bar.text().strip().lower()
        self.file_index_map = {}
        self.listbox.clear()
        items_added = 0
        if self.sort_mode == 'name':
            for i, entry in enumerate(self.cards_index):
                fname = entry['filename']
                creator = entry.get('creator', 'Unknown')
                tags = entry.get('tags', [])
                # ------ Tag-aware filter! ------
                meta_match = (
                    filter_text in fname.lower()
                    or filter_text in creator.lower()
                    or any(filter_text in tag.lower() for tag in tags)
                ) if filter_text else True
                if not meta_match:
                    continue
                item = QListWidgetItem(fname)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.listbox.addItem(item)
                self.file_index_map[self.listbox.count() - 1] = i
                items_added += 1
        else:
            # Group by creator
            creator_map = {}
            for i, entry in enumerate(self.cards_index):
                creator = entry.get("creator", "Unknown") or "Unknown"
                fname = entry['filename']
                tags = entry.get('tags', [])
                # ------ Tag-aware filter! ------
                meta_match = (
                    filter_text in fname.lower()
                    or filter_text in creator.lower()
                    or any(filter_text in tag.lower() for tag in tags)
                ) if filter_text else True
                if not meta_match:
                    continue
                creator_map.setdefault(creator, []).append((fname, i))
            for creator in sorted(creator_map, key=lambda s: s.lower()):
                if not creator_map[creator]:
                    continue
                header = QListWidgetItem(creator)
                header.setFlags(header.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled)
                font = header.font()
                font.setBold(True)
                header.setFont(font)
                header.setData(Qt.UserRole, "header")
                self.listbox.addItem(header)
                for fname, idx in sorted(creator_map[creator], key=lambda x: x[0].lower()):
                    item = QListWidgetItem("    " + fname)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    self.listbox.addItem(item)
                    self.file_index_map[self.listbox.count() - 1] = idx
                    items_added += 1
        # Auto-select first selectable item (skip headers)
        self._fix_selection()
        self.statusbar.showMessage(f"{items_added} card(s) | Mode: {'Sort by Name' if self.sort_mode == 'name' else 'Group by Creator'}")


    def _fix_selection(self, force=False):
        # Only keep selection on selectable items (not headers)
        row = self.listbox.currentRow()
        if row == -1:
            return
        item = self.listbox.item(row)
        if item and (item.flags() & Qt.ItemFlag.ItemIsSelectable):
            self.show_card()
            return
        # Not selectable: move selection to nearest real card
        next_row = row + 1
        while next_row < self.listbox.count():
            item = self.listbox.item(next_row)
            if item and (item.flags() & Qt.ItemFlag.ItemIsSelectable):
                self.listbox.setCurrentRow(next_row)
                self.show_card()
                return
            next_row += 1
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
        self.details.show_image(fpath)
        card, error = extract_card_metadata(fpath)
        self.details.show_metadata(card)
        self.statusbar.showMessage(f"{fname} | {entry.get('creator', 'Unknown')}")

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
                del self.cards_index[meta_idx]
                cache_file = os.path.join(self.folder, "cards.json")
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(self.cards_index, f, ensure_ascii=False, indent=2)
                # Always fully refresh list and mappings after delete
                self.update_listbox()
                self.details.show_image(None)
                self.details.show_metadata(None)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete file:\n{e}")


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
        if idx == -1 or idx not in self.file_index_map:
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
        about_action = QAction("About", self)

        def do_open():
            QDesktopServices.openUrl(f"file:///{os.path.abspath(fpath)}")

        def do_export():
            card, error = extract_card_metadata(fpath)
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

        def do_about():
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("About")
            msg.setText(f"Character Card Viewer\nVersion: {__version__}\n\ngithub.com/kaosnews/CardViewer")
            if self.is_dark_mode:
                apply_messagebox_dark(msg)
            msg.exec()

        open_action.triggered.connect(do_open)
        export_action.triggered.connect(do_export)
        save_as_action.triggered.connect(do_save_as)
        about_action.triggered.connect(do_about)

        menu.addAction(open_action)
        menu.addAction(export_action)
        menu.addAction(save_as_action)
        menu.addSeparator()
        menu.addAction(about_action)

        menu.exec(QCursor.pos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Start in dark mode or light mode based on saved settings (default dark)
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