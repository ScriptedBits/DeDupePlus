"""
    DeDupe+
    Copyright (C) 2026 ScriptedBits
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
"""
   ===========================================================================================
                          DeDupe+
   ===========================================================================================
    This script is provided as-is without any warranty or
    guarantee of functionality.
    This script is for personal use only to automate the process of de deuplication of files on your own systems
   
    Author: ScriptedBits
    License: GPL3
    For any support or issues, Please visit the github respository
    ==========================================================================================
"""

import sys
import os
import re
import time
from collections import defaultdict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QDialog, QFormLayout, QMenuBar, QStatusBar,
    QCheckBox, QGroupBox, QComboBox, QTextEdit, QProgressBar, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QDateTime, QSize, QTimer
from PyQt6.QtGui import QColor, QMovie, QActionGroup

__version__ = "1.8.1"

def normalize_filename(filename: str) -> str:
    base = os.path.splitext(filename)[0]
    base = base.lower().strip()
    base = re.sub(r'\s*\(\d{4}\)\s*', ' ', base)
    base = re.sub(r'\s*\[\d{4}\]\s*', ' ', base)
    base = re.sub(r'\s*(4k|1080p|720p|2160p|hdr|remux|blu-?ray|web-dl|webrip)\s*', ' ', base, flags=re.I)
    base = re.sub(r'\s*[\(\[\{].*?[\)\]\}]\s*', ' ', base)
    base = re.sub(r'\s+', ' ', base).strip()
    return base

class ExtensionsDialog(QDialog):
    def __init__(self, parent=None, current_include="", current_exclude="", recursive=True):
        super().__init__(parent)
        self.setWindowTitle("Filter Extensions")
        self.setMinimumSize(620, 420)  # Clean size for content

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 12, 16, 12)

        # Top form: include + exclude fields + recursive
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.include_edit = QLineEdit(current_include)
        self.include_edit.setPlaceholderText("e.g. .mp4,.mkv,.avi (blank = all)")
        form_layout.addRow("Only include extensions:", self.include_edit)

        self.exclude_edit = QLineEdit(current_exclude)
        self.exclude_edit.setPlaceholderText("e.g. .srt,.jpg,.txt (optional)")
        form_layout.addRow("Exclude extensions:", self.exclude_edit)

        self.recursive_cb = QCheckBox("Search subfolders (recursive)")
        self.recursive_cb.setChecked(recursive)
        form_layout.addRow(self.recursive_cb)

        main_layout.addLayout(form_layout)

        # Include presets group
        presets_group = QGroupBox("Quick Include Presets")
        presets_layout = QVBoxLayout()
        presets_layout.setSpacing(6)

        self.video_cb = QCheckBox("Video files (.mp4, .mkv, .avi, .mov, ...)")
        self.rom_cb = QCheckBox("Retro ROMs (.gb, .gba, .nes, .sfc, .n64, .iso, .chd ...)")
        self.office_cb = QCheckBox("Office documents (.docx, .xlsx, .pptx, .odt, .pdf ...)")
        self.music_cb = QCheckBox("Music / Audio files (.mp3, .flac, .m4a, .wav, ...)")
        self.image_cb = QCheckBox("Images (.jpg, .png, .gif, .bmp, .tiff, .heic, ...)")
        self.ebook_cb = QCheckBox("Ebooks (.epub, .mobi, .pdf, .azw, ...)")
        self.archive_cb = QCheckBox("Archives / Zips (.zip, .rar, .7z, .tar.gz, ...)")

        presets_layout.addWidget(self.video_cb)
        presets_layout.addWidget(self.rom_cb)
        presets_layout.addWidget(self.office_cb)
        presets_layout.addWidget(self.music_cb)
        presets_layout.addWidget(self.image_cb)
        presets_layout.addWidget(self.ebook_cb)
        presets_layout.addWidget(self.archive_cb)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        apply_btn = QPushButton("Add Selected Presets")
        apply_btn.setStyleSheet("background: #28a745; color: white;")
        apply_btn.clicked.connect(self.apply_presets)
        btn_row.addWidget(apply_btn)

        clear_btn = QPushButton("Clear / Reset")
        clear_btn.setStyleSheet("color: #dc3545;")
        clear_btn.clicked.connect(self.clear_presets)
        btn_row.addWidget(clear_btn)

        presets_layout.addLayout(btn_row)
        presets_group.setLayout(presets_layout)
        main_layout.addWidget(presets_group)

        main_layout.addStretch()

        # Save/Cancel
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(cancel_btn)
        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

    def apply_presets(self):
        current = set()
        if self.video_cb.isChecked():
            current.update({
                ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
                ".mpg", ".mpeg", ".m4v", ".ts", ".m2ts", ".vob", ".divx",
                ".3gp", ".rm", ".rmvb", ".f4v"
            })
        if self.rom_cb.isChecked():
            current.update({
                ".a26", ".a52", ".a78", ".j64", ".lnx", ".col", ".iso",
                ".rvz", ".xci", ".nsp", ".wbfs", ".wua", ".chd", ".gg",
                ".sms", ".cso", ".3ds", ".gb", ".gbc", ".gba", ".nes",
                ".sfc", ".smc", ".n64", ".z64", ".v64", ".nds", ".rom",
                ".zip", ".bin", ".cue", ".gcm", ".dol", ".vpk", ".pkg"
            })
        if self.office_cb.isChecked():
            current.update({
                ".doc", ".docx", ".docm", ".xls", ".xlsx", ".xlsm", ".xltx",
                ".ppt", ".pptx", ".pptm", ".odt", ".ods", ".odp", ".rtf",
                ".pdf", ".csv", ".txt", ".md", ".pages", ".numbers", ".key"
            })
        if self.music_cb.isChecked():
            current.update({
                ".mp3", ".m4a", ".aac", ".flac", ".wav", ".aiff", ".aif",
                ".ogg", ".oga", ".wma", ".opus", ".dsf", ".dff", ".ape"
            })
        if self.archive_cb.isChecked():
            current.update({
                ".zip", ".zipx", ".rar", ".7z", ".tar", ".gz", ".tgz",
                ".tar.gz", ".bz2", ".tar.bz2", ".iso", ".zst", ".xz",
                ".cab", ".deb", ".rpm"
            })
        if self.image_cb.isChecked():
            current.update({
                ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
                ".webp", ".heic", ".heif", ".raw", ".cr2", ".nef", ".arw",
                ".dng", ".svg"
            })
        if self.ebook_cb.isChecked():
            current.update({
                ".epub", ".mobi", ".azw", ".azw3", ".fb2",
                ".djvu", ".cbz", ".cbr", ".pdf"
            })
        new_text = ", ".join(sorted(current)) if current else ""
        self.include_edit.setText(new_text)

    def clear_presets(self):
        self.video_cb.setChecked(False)
        self.rom_cb.setChecked(False)
        self.office_cb.setChecked(False)
        self.music_cb.setChecked(False)
        self.archive_cb.setChecked(False)
        self.image_cb.setChecked(False)
        self.ebook_cb.setChecked(False)
        self.include_edit.clear()

    def get_settings(self):
        inc = [e.strip().lower() for e in self.include_edit.text().split(",") if e.strip()]
        rec = self.recursive_cb.isChecked()
        return inc, rec  # No exclude returned
        
class ThemeDialog(QDialog):
    def __init__(self, parent=None, current_theme="light"):
        super().__init__(parent)
        self.setWindowTitle("Theme Settings")
        layout = QVBoxLayout(self)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Standard (Light)", "Dark"])
        self.theme_combo.setCurrentIndex(0 if current_theme == "light" else 1)
        layout.addWidget(QLabel("Application Theme:"))
        layout.addWidget(self.theme_combo)
        btn_layout = QHBoxLayout()
        ok = QPushButton("Save & Apply")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok)
        btn_layout.addWidget(cancel)
        layout.addLayout(btn_layout)

    def get_theme(self):
        return "dark" if self.theme_combo.currentIndex() == 1 else "light"

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DeDupe+ Help & Examples")
        self.resize(680, 520)
        layout = QVBoxLayout(self)
        text = QTextEdit()
        font = text.font()
        font.setPointSize(11)  # adjust this number to your preference
        text.setFont(font)
        text.setReadOnly(True)
        text.setMarkdown("""
**Main Purpose**
Find files with similar names and let you safely delete duplicates. Intelligently ignores year tags, quality tags (4K, HDR, WEB-DL, etc.), case differences, and bracket/parentheses noise when comparing filenames.

---

**How Name Matching Works**
- `file1.mp4` & `file1.srt` → considered duplicates
- `movie (2025).mkv` & `movie 4K (2025).mp4` → considered duplicates
- Ignores case, years in () or [], common video tags (4k, hdr, web-dl, remux, etc.)

---

**Basic Usage**
1. Select a folder or drive using **Browse** or type a path directly
2. Optionally set filters via **Options → Filter Extensions**
3. Click **🔍 Start Scan** — use **⏹️ Stop Scan** to cancel at any time
4. Review duplicate groups in the results tree
5. Check files to delete, then click **🗑️ Delete Selected**

---

**Results Tree**
- Each group shows files that are considered duplicates of each other
- **Double-click** any file to open its location in Explorer / Finder
- **Right-click** any file for a context menu with:
  - Open File Location
  - File Properties (size, dates, video resolution & duration if applicable)
  - Check / Uncheck shortcuts

---

**Buttons**
- **✅ Select All** / **❌ Deselect All** — check or uncheck all files at once
- **🗑️ Delete Selected** — permanently deletes checked files (confirmation required)
- **💾 Save Results** — export duplicate report as HTML or CSV
- **🔄 Clear Results** — clears the results tree without deleting anything

---

**Extension Filtering**
Use **Options → Filter Extensions** to control which files are scanned:
- Only videos: include `.mp4, .mkv, .avi, .mov`
- Skip thumbnails & logs: exclude `.jpg, .png, .txt, .nfo, .log`
- Scan everything except junk: leave include blank, exclude `.jpg, .png, .db, .tmp`

Use the **Quick Include Presets** checkboxes for fast setup:
- Video, Retro ROMs, Office Documents, Music/Audio, Archives

---

**Progress Animation**
Choose your preferred scan indicator via **Options → Progress Animation**:
- Default bar — standard Qt progress bar
- Animated folder — animated GIF
- Emoji rotation — 📁📂 cycling icons
- Retro ASCII bar — scrolling `[████░░░░]` bar
- None — text only

---

**Theme**
Change between Dark and Light via **Options → Theme** — saved automatically for next launch.

---

**Need Help?**
Report issues or suggest features on GitHub:
https://github.com/ScriptedBits/DeDupePlus
        """)
        layout.addWidget(text)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About DeDupe+")
        self.setMinimumSize(540, 420)
       
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("DeDupe+")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        version = QLabel(f"Version {__version__}")
        version.setStyleSheet("font-size: 15px; color: #888888;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        layout.addSpacing(16)

        desc = QLabel(
            "A fast duplicate file finder that intelligently matches files\n"
            "by ignoring years, quality tags (4K, HDR, WEB-DL, etc.),\n"
            "case sensitivity and common brackets/parentheses noise.\n\n"
            "Great for cleaning up movies, TV shows, music, ROMs,\n"
            "photos and general file clutter."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 16px;")
        layout.addWidget(desc)

        layout.addSpacing(20)

        copy_label = QLabel(
            "© 2026 ScriptedBits\n"
            "Released under the GNU General Public License v3\n"
            "This program is provided AS-IS with NO WARRANTY."
        )
        copy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copy_label.setStyleSheet("color: #999999; font-size: 13px;")
        layout.addWidget(copy_label)

        layout.addSpacing(18)

        gh_container = QWidget()
        gh_layout = QHBoxLayout(gh_container)
        gh_layout.setContentsMargins(0, 0, 0, 0)
        gh_layout.setSpacing(0)

        gh_label = QLabel(
            '<a href="https://github.com/ScriptedBits/DeDupePlus" '
            'style="color: #58a6ff; text-decoration: none;">'
            'github.com/ScriptedBits/DeDupePlus'
            '</a>'
        )
        gh_label.setOpenExternalLinks(True)
        gh_label.setStyleSheet("""
            font-size: 17px;
            font-weight: bold;
            padding: 10px 18px;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #58a6ff;
        """)
        gh_label.setCursor(Qt.CursorShape.PointingHandCursor)
        gh_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        gh_layout.addStretch()
        gh_layout.addWidget(gh_label)
        gh_layout.addStretch()

        layout.addWidget(gh_container)

        layout.addSpacing(20)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(120)
        close_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        if parent and parent.isVisible():
            self.move(
                parent.x() + (parent.width() - self.width()) // 2,
                parent.y() + (parent.height() - self.height()) // 2
            )

class ScanThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(object)

    def __init__(self, root_dir: str, include_exts: list, exclude_exts: list = None, recursive: bool = True):
        super().__init__()
        self.root_dir = root_dir
        self.include_exts = include_exts
        self.exclude_exts = exclude_exts or []
        self.recursive = recursive

    def run(self):
        groups = defaultdict(list)
        total_files = 0

        def scan_dir(path):
            nonlocal total_files
            if self.isInterruptionRequested():
                return
            try:
                entries = list(os.scandir(path))
            except PermissionError:
                return

            for entry in entries:
                if self.isInterruptionRequested():
                    return

                if entry.is_file(follow_symlinks=False):
                    total_files += 1

                    if total_files % 20 == 0:
                        self.progress.emit(total_files, path)
                        QThread.msleep(1)

                    f = entry.name
                    if f.startswith('.'):
                        ext = f.lower() if '.' not in f[1:] else os.path.splitext(f)[1].lower()
                    else:
                        ext = os.path.splitext(f)[1].lower()

                    include = (
                        (not self.include_exts and not self.exclude_exts) or
                        (self.include_exts and ext in self.include_exts) or
                        (not self.include_exts and self.exclude_exts and ext not in self.exclude_exts)
                    )

                    if include:
                        key = normalize_filename(f)
                        try:
                            size = entry.stat().st_size
                        except:
                            size = 0
                        groups[key].append((entry.path, size, f))

                elif self.recursive and entry.is_dir(follow_symlinks=False):
                    scan_dir(entry.path)

        scan_dir(self.root_dir)

        if self.isInterruptionRequested():
            self.finished.emit(None)
        else:
            duplicates = {k: v for k, v in groups.items() if len(v) > 1}
            self.finished.emit(duplicates)
            
class DuplicateFinder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"🗂️ DeDupe+ v{__version__}")
        self.resize(1100, 700)
        self.checkmark_svg = self._write_checkmark_svg()
        
        self.settings = QSettings("ScriptedBits", "DeDupePlus")
        # Progress style choices (stored in settings)
        self.progress_style = self.settings.value("progress_style", "ascii_bar", type=str)
        # Possible values: "default_bar", "animated_gif", "emoji", "none"

        self.include_exts = self.settings.value("include_exts", [], type=list)
        self.exclude_exts = self.settings.value("exclude_exts", [], type=list)
        self.recursive = self.settings.value("recursive", True, type=bool)
        self.theme = self.settings.value("theme", "dark", type=str)
        last_path = self.settings.value("last_path", "", type=str)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top = QHBoxLayout()
        lbl = QLabel("Search in:")
        self.path_edit = QLineEdit(last_path)
        browse = QPushButton("📁 Browse")
        browse.clicked.connect(self.browse)
 
        self.scan_btn = QPushButton("🔍 Start Scan")
        self.scan_btn.clicked.connect(self.start_scan)
        self.scan_btn.setStyleSheet("background: #28a745; color: white; font-weight: bold;")
        
        # Stop Scan button (hidden by default)
        self.stop_btn = QPushButton("⏹️ Stop Scan")
        self.stop_btn.setStyleSheet("background: #dc3545; color: white; font-weight: bold;")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setVisible(False)  # hidden until scan starts

        top.addWidget(lbl)
        top.addWidget(self.path_edit, 1)
        top.addWidget(browse)
        top.addWidget(self.scan_btn)
        top.addWidget(self.stop_btn)

        layout.addLayout(top)

        # Container for progress indicators
        self.progress_container = QWidget()
        self.progress_layout = QHBoxLayout(self.progress_container)
        self.progress_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.progress_container)

        # Default bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # indeterminate
        self.progress_layout.addWidget(self.progress_bar)

        # Animated GIF
        self.scan_movie = QMovie("folder.gif")  # or folder.jpg if it's animated
        self.scan_movie.setScaledSize(QSize(48, 48))
        self.scan_animation = QLabel()
        self.scan_animation.setMovie(self.scan_movie)
        self.scan_animation.setVisible(False)
        self.progress_layout.addWidget(self.scan_animation, alignment=Qt.AlignmentFlag.AlignCenter)

        # Emoji rotation label
        self.emoji_label = QLabel()
        self.emoji_label.setVisible(False)
        self.progress_layout.addWidget(self.emoji_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.emoji_timer = QTimer(self)
        self.emoji_timer.timeout.connect(self.update_emoji_animation)
        self.emoji_icons = ["📁", "📂", "📁📂", "📂📁"]
        self.emoji_index = 0
        
        # ascii label
        self.ascii_label = QLabel()
        self.ascii_label.setStyleSheet("font-family: monospace; font-size: 13px; letter-spacing: 1px; color: #007bff;")
        self.ascii_label.setVisible(False)
        self.progress_layout.addWidget(self.ascii_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.ascii_bar_timer = QTimer(self)
        self.ascii_bar_timer.timeout.connect(self.update_ascii_bar)
        self.ascii_bar_pos = 0
        self.ascii_bar_direction = 1
        self.ascii_bar_width = 80
        self.ascii_bar_chunk = 6

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Select files", "Filename", "Full Path", "Size (MB)"])
        self.tree.setColumnWidth(0, 170)
        self.tree.setColumnWidth(1, 250)
        self.tree.setColumnWidth(2, 450)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        self.tree.sortItems(3, Qt.SortOrder.DescendingOrder)
        
        self.tree.itemDoubleClicked.connect(self.open_file_location)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.tree)

        btn_row = QHBoxLayout()
        select_all = QPushButton("✅ Select All")
        select_all.clicked.connect(self.select_all)
        deselect_all = QPushButton("❌ Deselect All")
        deselect_all.clicked.connect(self.deselect_all)
        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.clicked.connect(self.delete_selected)
        delete_btn.setStyleSheet("background: #dc3545; color: white; font-weight: bold;")
        refresh = QPushButton("🔄 Clear Results")
        refresh.clicked.connect(lambda: self.tree.clear())
        refresh.setStyleSheet("background: #17a2b8; color: white; font-weight: bold;")
        save_btn = QPushButton("💾 Save Results")
        save_btn.clicked.connect(self.save_results)
        save_btn.setStyleSheet("background: #007bff; color: white; font-weight: bold;")

        btn_row.addWidget(select_all)
        btn_row.addWidget(deselect_all)
        btn_row.addStretch()
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(refresh)
        layout.addLayout(btn_row)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Open folder", self.browse)
        file_menu.addAction("Exit", self.close)

        options_menu = menubar.addMenu("Options")
        options_menu.addAction("Filter Extensions...", self.show_extensions_dialog)
        options_menu.addAction("Theme...", self.show_theme_dialog)
        progress_menu = options_menu.addMenu("Progress Animation")
        
        progress_action_group = QActionGroup(self)
        progress_action_group.setExclusive(True)

        actions = {
            "Default bar": "default_bar",
            "Animated GIF (Animated folder)": "animated_gif",
            "Emoji rotation (📁📂)": "emoji",
            "Retro ASCII bar [████░░░░]": "ascii_bar",
            "None (text only)": "none"
        }
        for label, value in actions.items():
            action = progress_menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(self.progress_style == value)
            action.triggered.connect(lambda checked, v=value: self.set_progress_style(v))
            progress_action_group.addAction(action)
        
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Help / Examples", self.show_help)
        help_menu.addAction("About DeDupe+", self.show_about)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.scan_status_label = QLabel("Ready")
        self.statusBar.addPermanentWidget(self.scan_status_label)

        self.thread = None
        self.current_groups = {}

        self.apply_theme()
        self.update_filter_status()

    def show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item or not item.text(2):  # ignore group headers
            return

        fullpath = item.text(2)
        if not os.path.exists(fullpath):
            return

        menu = QMenu(self)
        menu.addAction("📂 Open File Location", lambda: self.open_file_location(item, 0))
        menu.addAction("ℹ️ Properties", lambda: self.show_file_properties(fullpath))
        menu.addSeparator()
        menu.addAction("✅ Check", lambda: item.setCheckState(0, Qt.CheckState.Checked))
        menu.addAction("❌ Uncheck", lambda: item.setCheckState(0, Qt.CheckState.Unchecked))
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def show_file_properties(self, fullpath):
        try:
            stat = os.stat(fullpath)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not read file:\n{e}")
            return

        from datetime import datetime
        size_bytes = stat.st_size
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        size_gb = size_mb / 1024

        if size_gb >= 1:
            size_str = f"{size_gb:.2f} GB"
        elif size_mb >= 1:
            size_str = f"{size_mb:.2f} MB"
        else:
            size_str = f"{size_kb:.2f} KB"

        created  = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        accessed = datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S")

        ext = os.path.splitext(fullpath)[1].lower()
        video_exts = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
                      ".mpg", ".mpeg", ".m4v", ".ts", ".m2ts"}
        is_video = ext in video_exts

        dlg = QDialog(self)
        dlg.setWindowTitle("File Properties")
        dlg.setMinimumWidth(520)
        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Filename header
        name_label = QLabel(os.path.basename(fullpath))
        name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Details form
        form = QFormLayout()
        form.setSpacing(6)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        def add_row(label, value):
            val_label = QLabel(value)
            val_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            val_label.setWordWrap(True)
            form.addRow(f"<b>{label}</b>", val_label)

        add_row("Full path:",  fullpath)
        add_row("Size:",       f"{size_str}  ({size_bytes:,} bytes)")
        add_row("Type:",       ext.upper().lstrip(".") if ext else "Unknown")
        add_row("Modified:",   modified)
        add_row("Created:",    created)
        add_row("Accessed:",   accessed)

        layout.addLayout(form)

        # Video metadata section
        if is_video:
            layout.addWidget(QLabel(""))
            video_header = QLabel("Video Info")
            video_header.setStyleSheet("font-weight: bold; font-size: 13px;")
            layout.addWidget(video_header)

            video_form = QFormLayout()
            video_form.setSpacing(6)

            # Try to get resolution via pymediainfo
            resolution_str = "Install pymediainfo for video details"
            duration_str = ""
            codec_str = ""
            try:
                from pymediainfo import MediaInfo
                lib = self._get_mediainfo_library()
                info = MediaInfo.parse(fullpath, library_file=lib)
                for track in info.tracks:
                    if track.track_type == "Video":
                        w = track.width or ""
                        h = track.height or ""
                        if w and h:
                            resolution_str = f"{w} × {h}"
                        codec_str = track.codec_id or track.format or "Unknown"
                    if track.track_type == "General":
                        ms = track.duration
                        if ms:
                            secs = int(ms) // 1000
                            mins, secs = divmod(secs, 60)
                            hrs, mins = divmod(mins, 60)
                            duration_str = f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs else f"{mins:02d}:{secs:02d}"
            except ImportError:
                pass
            except Exception:
                resolution_str = "Could not read video info"

            def add_video_row(label, value):
                if not value:
                    return
                val_label = QLabel(value)
                val_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                video_form.addRow(f"<b>{label}</b>", val_label)

            add_video_row("Resolution:", resolution_str)
            add_video_row("Duration:",   duration_str)
            add_video_row("Codec:",      codec_str)
            layout.addLayout(video_form)

        layout.addStretch()

        # Close button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(dlg.accept)
        btn_row.addWidget(close_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        dlg.exec()

    def _get_mediainfo_library(self):
        if getattr(sys, 'frozen', False):
            # Running as compiled PyInstaller bundle
            base = sys._MEIPASS
            if sys.platform == "win32":
                dll_path = os.path.join(base, "pymediainfo", "MediaInfo.dll")
                if os.path.exists(dll_path):
                    return dll_path
                # Fallback — check root bundle dir
                dll_path = os.path.join(base, "MediaInfo.dll")
                if os.path.exists(dll_path):
                    return dll_path
            elif sys.platform.startswith("linux"):
                return os.path.join(base, "libmediainfo.so.0")
            elif sys.platform == "darwin":
                return os.path.join(base, "libmediainfo.dylib")
        return None  # Not frozen — pymediainfo finds it automatically

    def open_file_location(self, item, column):
        # Group header rows have no path — ignore them
        fullpath = item.text(2)
        if not fullpath or not os.path.exists(fullpath):
            return

        if sys.platform == "win32":
            # Opens Explorer and highlights the specific file
            import subprocess
            subprocess.run(["explorer", "/select,", fullpath.replace("/", "\\")])
        elif sys.platform == "darwin":
            # Opens Finder and highlights the file
            import subprocess
            subprocess.run(["open", "-R", fullpath])
        else:
            # Linux — open the containing folder (can't highlight the file portably)
            import subprocess
            subprocess.run(["xdg-open", os.path.dirname(fullpath)])

    def _write_checkmark_svg(self):
        import tempfile
        path = os.path.join(tempfile.gettempdir(), "dedupe_plus_checkmark.svg")
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14">'
            '<rect width="14" height="14" rx="2" fill="#4a90d9"/>'
            '<polyline points="2,7 6,11 12,3" '
            'style="fill:none;stroke:white;stroke-width:2.5;'
            'stroke-linecap:round;stroke-linejoin:round"/>'
            '</svg>'
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        return path.replace(os.sep, '/')

    def update_ascii_bar(self):
        bar = ['░'] * self.ascii_bar_width
        for i in range(self.ascii_bar_chunk):
            idx = self.ascii_bar_pos + i
            if 0 <= idx < self.ascii_bar_width:
                bar[idx] = '█'
        filled = ''.join(bar)
        count_text = self.scan_status_label.text()
        self.ascii_label.setText(f"[{filled}] {count_text}")

        self.ascii_bar_pos += self.ascii_bar_direction
        if self.ascii_bar_pos + self.ascii_bar_chunk >= self.ascii_bar_width:
            self.ascii_bar_direction = -1
        elif self.ascii_bar_pos <= 0:
            self.ascii_bar_direction = 1

    def stop_scan(self):
        if self.thread and self.thread.isRunning():
            self.thread.requestInterruption()  # Tell thread to stop
            self.scan_status_label.setText("Stopping scan... please wait")
            self.stop_btn.setEnabled(False)    # prevent multiple clicks
            self.scan_btn.setEnabled(True)
            QTimer.singleShot(10000, lambda: self.scan_status_label.setText("Scan stop timeout - restarting UI") if self.thread.isRunning() else None)

    def update_emoji_animation(self):
        self.emoji_index = (self.emoji_index + 1) % len(self.emoji_icons)
        self.emoji_label.setText(f"{self.emoji_icons[self.emoji_index]} Scanning...")

    def set_progress_style(self, style: str):
        self.progress_style = style
        self.settings.setValue("progress_style", style)
        self.update_filter_status()  # optional: refresh status if needed

    def closeEvent(self, event):
        # Save settings on close
        self.settings.setValue("include_exts", self.include_exts)
        self.settings.setValue("exclude_exts", self.exclude_exts)
        self.settings.setValue("recursive", self.recursive)
        self.settings.setValue("theme", self.theme)
        self.settings.setValue("last_path", self.path_edit.text())
        super().closeEvent(event)

    def apply_theme(self):
        app = QApplication.instance()
        if self.theme == "dark":
            app.setStyle("Fusion")
            dark_sheet = f"""
                QMainWindow, QDialog {{ background: #2b2b2b; color: #ddd; }}
                QWidget {{ background: #2b2b2b; color: #ddd; }}
                QTreeWidget {{ background: #1e1e1e; alternate-background-color: #282828; color: #ddd; }}
                QTreeWidget::item:selected {{ background: #4a90d9; }}
                QLineEdit, QComboBox, QCheckBox {{ background: #353535; color: #ddd; border: 1px solid #555; padding: 4px; }}
                QPushButton {{ background: #404040; color: #ddd; border: 1px solid #555; padding: 6px; }}
                QPushButton:hover {{ background: #505050; }}
                QProgressBar {{ background: #353535; color: #ddd; border: 1px solid #555; text-align: center; }}
                QProgressBar::chunk {{ background: #4a90d9; }}
                QStatusBar {{ background: #353535; color: #ddd; }}
                QMenuBar, QMenu {{ background: #2b2b2b; color: #ddd; }}
                QMenu::item:selected {{ background: #4a90d9; }}
                QTreeWidget::indicator {{
                    width: 18px;
                    height: 18px;
                }}
                QTreeWidget::indicator:unchecked {{
                    background: #555555;
                    border: 2px solid #aaaaaa;
                    border-radius: 3px;
                }}
                QTreeWidget::indicator:unchecked:hover {{
                    background: #666666;
                    border: 2px solid #cccccc;
                    border-radius: 3px;
                }}
                QTreeWidget::indicator:checked {{
                    image: url("{self.checkmark_svg}");
                    border: none;
                }}
                QTreeWidget::indicator:checked:hover {{
                    image: url("{self.checkmark_svg}");
                    border: none;
                }}
            """
            app.setStyleSheet(dark_sheet)
            palette = app.palette()
            palette.setColor(palette.ColorRole.Window, Qt.GlobalColor.darkGray)
            palette.setColor(palette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(palette.ColorRole.Base, Qt.GlobalColor.black)
            palette.setColor(palette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(palette.ColorRole.Button, Qt.GlobalColor.darkGray)
            palette.setColor(palette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(palette.ColorRole.Highlight, QColor(74, 144, 217))
            palette.setColor(palette.ColorRole.HighlightedText, Qt.GlobalColor.white)
            app.setPalette(palette)
        else:
            app.setStyle("Fusion")
            app.setStyleSheet("")
            app.setPalette(app.style().standardPalette())

    def show_extensions_dialog(self):
        dlg = ExtensionsDialog(
            self,
            ", ".join(self.include_exts),
            ", ".join(self.exclude_exts),  # pre-fill exclude field (optional)
            self.recursive
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            # Unpack only 2 values (include + recursive)
            self.include_exts, self.recursive = dlg.get_settings()
    
            # Manually parse exclude from the text field (user may have typed exclusions)
            exclude_text = dlg.exclude_edit.text().strip()
            self.exclude_exts = [e.strip().lower() for e in exclude_text.split(",") if e.strip()]
    
            self.update_filter_status()

    def save_results(self):
        """Export current duplicate results to HTML and/or CSV"""
        if not self.current_groups:
            QMessageBox.information(self, "No Results", "Run a scan first to generate results.")
            return

        # Let user choose base filename and location
        default_name = f"DeDupe+_results_{QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')}"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Results As...",
            default_name,
            "HTML File (*.html);;CSV File (*.csv);;All Files (*.*)"
        )

        if not file_path:
            return  # user canceled

        # Determine format from chosen extension
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".html":
            self._export_html(file_path)
        elif ext == ".csv":
            self._export_csv(file_path)
        else:
            # If user picked "All Files" or no extension → default to HTML
            file_path = file_path if file_path.endswith(".html") else file_path + ".html"
            self._export_html(file_path)

        QMessageBox.information(self, "Export Complete", f"Results saved to:\n{file_path}")

    def _export_html(self, path):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DeDupe+ Results</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .group {{ background-color: #e6f3ff; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>DeDupe+ Duplicate Report</h1>
            <p>Generated: {timestamp}</p>
            <table>
                <tr><th>Group Key</th><th>Filename</th><th>Full Path</th><th>Size (MB)</th></tr>
        """

        for key, files in self.current_groups.items():
            if len(files) < 2:
                continue
            html += f'<tr class="group"><td colspan="4">{key}</td></tr>'
            for fullpath, size, basename in sorted(files, key=lambda x: x[1], reverse=True):
                mb = round(size / (1024 * 1024), 2)
                html += f"<tr><td></td><td>{basename}</td><td>{fullpath}</td><td>{mb:.2f}</td></tr>"

        html += """
            </table>
        </body>
        </html>
        """

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    def _export_csv(self, path):
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Group Key", "Filename", "Full Path", "Size (MB)"])

            for key, files in self.current_groups.items():
                if len(files) < 2:
                    continue
                for fullpath, size, basename in files:
                    mb = round(size / (1024 * 1024), 2)
                    writer.writerow([key, basename, fullpath, f"{mb:.2f}"])

    def show_theme_dialog(self):
        dlg = ThemeDialog(self, self.theme)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_theme = dlg.get_theme()
            if new_theme != self.theme:
                self.theme = new_theme
                self.apply_theme()
                self.update_filter_status()

    def update_filter_status(self):
        msg = []
        if self.include_exts:
            msg.append(f"Only {len(self.include_exts)} ext(s)")
        else:
            msg.append("All files")
        if self.exclude_exts:
            msg.append(f"Excl. {len(self.exclude_exts)} ext(s)")
        msg.append(f"Recursive: {'Yes' if self.recursive else 'No'}")
        msg.append(f"Theme: {self.theme.capitalize()}")
        self.statusBar.showMessage(" | ".join(msg))

    def browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select folder", self.path_edit.text())
        if path:
            self.path_edit.setText(path)

    def start_scan(self):
        path = self.path_edit.text().strip()
        if not os.path.isdir(path):
            QMessageBox.warning(self, "Error", "Invalid folder!")
            return

        self.tree.clear()
        self.progress_container.setVisible(True)

        # Hide ALL indicators first, then show only the selected one
        self.progress_bar.setVisible(False)
        self.scan_animation.setVisible(False)
        self.scan_movie.stop()
        self.emoji_label.setVisible(False)
        self.emoji_timer.stop()
        self.ascii_label.setVisible(False)
        self.ascii_bar_timer.stop()
        
        if self.progress_style == "default_bar":
            self.progress_bar.setVisible(True)
        elif self.progress_style == "animated_gif":
            self.scan_animation.setVisible(True)
            self.scan_movie.start()
        elif self.progress_style == "emoji":
            self.emoji_label.setVisible(True)
            self.emoji_timer.start(400)
        elif self.progress_style == "ascii_bar":
            self.ascii_label.setVisible(True)
            self.ascii_bar_pos = 0
            self.ascii_bar_direction = 1
            self.ascii_bar_timer.start(40)

        # Show Stop button, disable Start button
        self.stop_btn.setVisible(True)
        self.stop_btn.setEnabled(True)
        self.scan_btn.setEnabled(False)          # ← use self.scan_btn

        self.statusBar.showMessage("Scan started...")
        self.scan_status_label.setText("Starting scan...")

        self.thread = ScanThread(path, self.include_exts, self.exclude_exts, self.recursive)
        self.thread.progress.connect(self.on_scan_progress)
        self.thread.finished.connect(self.on_scan_finished)
        self.thread.start()

    def on_scan_progress(self, count: int, current_folder: str):
        self.scan_status_label.setText(
            f"Scanning... {count:,} files"
        )
        
    def on_scan_finished(self, duplicates: dict):
        # Stop and hide any active progress indicator
        self.progress_container.setVisible(False)

        if self.progress_style == "default_bar":
            self.progress_bar.setVisible(False)
        elif self.progress_style == "animated_gif":
            self.scan_movie.stop()
            self.scan_animation.setVisible(False)
        elif self.progress_style == "emoji":
            self.emoji_timer.stop()
            self.emoji_label.setVisible(False)
        elif self.progress_style == "ascii_bar":
            self.ascii_bar_timer.stop()
            self.ascii_label.setVisible(False)

        # Handle the case where scan was interrupted/cancelled
        if duplicates is None:  # explicitly cancelled
            self.scan_status_label.setText("Scan cancelled")
            self.statusBar.showMessage("Scan cancelled by user")
        else:
            # Normal completion
            self.scan_status_label.setText("Scan complete")
            self.current_groups = duplicates

            self.tree.clear()
            count = 0
            is_dark = (self.theme == "dark")

            for key, files in duplicates.items():
                if len(files) < 2:
                    continue
                count += 1
                group_item = QTreeWidgetItem([key[:60] + "..." if len(key) > 60 else key, "", "", ""])
                group_bg = QColor("#444444" if is_dark else "#d0d0d0")
                group_fg = QColor("#ffffff" if is_dark else "#000000")
                group_item.setBackground(0, group_bg)
                group_item.setForeground(0, group_fg)
                group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.tree.addTopLevelItem(group_item)

                for fullpath, size, basename in sorted(files, key=lambda x: x[1], reverse=True):
                    mb = round(size / (1024 * 1024), 2)
                    item = QTreeWidgetItem(["", basename, fullpath, f"{mb:.2f} MB"])
                    item.setCheckState(0, Qt.CheckState.Unchecked)
                    item.setTextAlignment(3, Qt.AlignmentFlag.AlignCenter)
                    item.setToolTip(2, fullpath)

                    text_color = QColor("#000000") if not is_dark else QColor("#e8e8e8")
                    dim_color = QColor("#333333") if not is_dark else QColor("#bbbbbb")

                    item.setForeground(1, text_color)
                    item.setForeground(2, dim_color)
                    item.setForeground(3, dim_color)

                    group_item.addChild(item)

                group_item.setExpanded(True)

            self.statusBar.showMessage(
                f"Found {count} duplicate groups "
                f"({sum(len(v) for v in duplicates.values())} files)"
            )

        # Always clean up buttons when scan ends (normal or cancelled)
        self.stop_btn.setVisible(False)
        self.scan_btn.setEnabled(True)
        
    def select_all(self):
        for i in range(self.tree.topLevelItemCount()):
            group = self.tree.topLevelItem(i)
            for j in range(group.childCount()):
                child = group.child(j)
                child.setCheckState(0, Qt.CheckState.Checked)

    def deselect_all(self):
        for i in range(self.tree.topLevelItemCount()):
            group = self.tree.topLevelItem(i)
            for j in range(group.childCount()):
                child = group.child(j)
                child.setCheckState(0, Qt.CheckState.Unchecked)

    def delete_selected(self):
        to_delete = []
        for i in range(self.tree.topLevelItemCount()):
            group = self.tree.topLevelItem(i)
            for j in range(group.childCount()):
                child = group.child(j)
                if child.checkState(0) == Qt.CheckState.Checked:
                    to_delete.append(child.text(2))  # full path column

        if not to_delete:
            QMessageBox.information(self, "Nothing selected", "Select files with the checkboxes first.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {len(to_delete)} file(s) permanently?\n\nThis cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        deleted = 0
        errors = []
        for path in to_delete:
            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                errors.append(f"{path}: {e}")

        QMessageBox.information(self, "Done", f"Deleted {deleted} file(s).\nErrors: {len(errors)}")
        if errors:
            print("Delete errors:", errors)

        self.tree.clear()

    def show_help(self):
        dlg = HelpDialog(self)
        dlg.exec()

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DuplicateFinder()
    window.show()
    sys.exit(app.exec())