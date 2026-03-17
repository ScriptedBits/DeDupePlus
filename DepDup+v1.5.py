"""
    DeDupe+
    Copyright (C) 2026  ScriptedBits

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
	This script downloads the latest stable / dev releases of emulators 
    and their versions for Windows x86_64, Mac & Linux from their official websites or github.

    GitHub Repository: https://github.com/ScriptedBits/DeDupePlus

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
from collections import defaultdict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QProgressBar, QDialog, QFormLayout, QMenuBar, QStatusBar,
    QCheckBox, QGroupBox, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QColor


__version__ = "1.5"


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
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.include_edit = QLineEdit(current_include)
        self.include_edit.setPlaceholderText("e.g. .mp4,.mkv,.srt  (blank = all)")
        form.addRow("Only include these extensions:", self.include_edit)

        self.exclude_edit = QLineEdit(current_exclude)
        self.exclude_edit.setPlaceholderText("e.g. .jpg,.txt,.nfo,.db")
        form.addRow("Exclude these extensions:", self.exclude_edit)

        self.recursive_cb = QCheckBox("Search subfolders (recursive)")
        self.recursive_cb.setChecked(recursive)
        form.addRow(self.recursive_cb)

        layout.addLayout(form)

        # Presets
        presets_group = QGroupBox("Quick Presets")
        presets_layout = QVBoxLayout()

        self.video_cb = QCheckBox("Video files (.mp4, .mkv, .avi, .mov, ...)")
        self.rom_cb = QCheckBox("Retro ROMs (.gb, .gba, .nes, .sfc, .n64, ...)")
        presets_layout.addWidget(self.video_cb)
        presets_layout.addWidget(self.rom_cb)

        apply_presets_btn = QPushButton("Apply Selected Presets to Include")
        apply_presets_btn.clicked.connect(self.apply_presets)
        presets_layout.addWidget(apply_presets_btn)

        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)

        btn_layout = QHBoxLayout()
        ok = QPushButton("Save")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok)
        btn_layout.addWidget(cancel)
        layout.addLayout(btn_layout)

    def apply_presets(self):
        current = set(e.strip().lower() for e in self.include_edit.text().split(",") if e.strip())

        if self.video_cb.isChecked():
            video = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mpg", ".mpeg", ".m4v", ".ts", ".m2ts"}
            current.update(video)

        if self.rom_cb.isChecked():
            roms = {".gb", ".gbc", ".gba", ".nes", ".sfc", ".smc", ".n64", ".z64", ".nds", ".rom", ".zip"}
            current.update(roms)

        self.include_edit.setText(", ".join(sorted(current)) if current else "")

    def get_settings(self):
        inc = [e.strip().lower() for e in self.include_edit.text().split(",") if e.strip()]
        exc = [e.strip().lower() for e in self.exclude_edit.text().split(",") if e.strip()]
        rec = self.recursive_cb.isChecked()
        return inc, exc, rec


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
        text.setReadOnly(True)
        text.setMarkdown("""
**DeDupe+ – Quick Help & Examples**

**Main purpose**  
Find files with similar names (ignoring year tags, quality tags like 4K/1080p, etc.) and let you delete duplicates.

**How name matching works**  
- file1.mp4  &  file1.srt  → considered duplicates  
- movie (2025).mkv  &  movie 4k (2025).mp4  → considered duplicates  
- Ignores case, years in (), [], common video tags (4k, hdr, web-dl, etc.)

**Basic usage**  
1. Select folder/drive  
2. (optional) Set filters in **Options → Filter Extensions**  
3. Click **Start Scan**  
4. Check files to delete → **Delete Selected**

**Extension filtering examples**  
- Only videos: include `.mp4, .mkv, .avi, .mov`  
- Skip thumbnails & logs: exclude `.jpg, .png, .txt, .nfo, .log`  
- Scan everything except junk: leave include blank, exclude `.jpg,.png,.db,.tmp`

**Presets**  
Use the checkboxes in the extensions dialog for quick setup.

**Theme**  
Change in **Options → Theme** – setting saved for next launch.

**Need help?**  
Report issues or suggest features on GitHub:  
https://github.com/ScriptedBits/DeDupePlus
        """)
        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About DeDupe+")
        self.setMinimumWidth(480)
        self.setMinimumHeight(280)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("DeDupe+")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        version_label = QLabel(f"Version {__version__}")
        version_label.setStyleSheet("font-size: 14px; color: #555;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        layout.addSpacing(16)

        created = QLabel("Created by ScriptedBits")
        created.setStyleSheet("font-size: 15px; font-weight: bold;")
        created.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(created)

        desc = QLabel("Created to help find duplicate files across Windows, Linux and Mac.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        layout.addSpacing(20)

        link = QLabel('<a href="https://github.com/ScriptedBits/DeDupePlus">https://github.com/ScriptedBits/DeDupePlus</a>')
        link.setOpenExternalLinks(True)
        link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(link)

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedWidth(120)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

class ScanThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)

    def __init__(self, root_dir: str, include_exts: list, exclude_exts: list, recursive: bool):
        super().__init__()
        self.root_dir = root_dir
        self.include_exts = include_exts
        self.exclude_exts = exclude_exts
        self.recursive = recursive

    def run(self):
            groups = defaultdict(list)
            total_files = 0

            def should_include(name: str) -> bool:
                ext = os.path.splitext(name)[1].lower()
                if self.include_exts:
                    return ext in self.include_exts
                if self.exclude_exts:
                    return ext not in self.exclude_exts
                return True

            for root, dirs, files in os.walk(self.root_dir):
                if not self.recursive and root != self.root_dir:
                    break

                # Emit before processing files in this folder
                self.progress.emit(total_files, root)

                for f in files:
                    total_files += 1

                    # Update more frequently (every 50–100 files)
                    if total_files % 100 == 0:
                        self.progress.emit(total_files, root)

                    if should_include(f):
                        key = normalize_filename(f)
                        fullpath = os.path.join(root, f)
                        try:
                            size = os.path.getsize(fullpath)
                        except:
                            size = 0
                        groups[key].append((fullpath, size, f))

                # Optional: emit again after finishing a folder
                # self.progress.emit(total_files, root)

            duplicates = {k: v for k, v in groups.items() if len(v) > 1}
            self.finished.emit(duplicates)

class DuplicateFinder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"🗂️ DeDupe+ v{__version__}")
        self.resize(1100, 700)

        self.settings = QSettings("ScriptedBits", "DeDupePlus")

        # Load saved settings
        self.include_exts = self.settings.value("include_exts", [], type=list)
        self.exclude_exts = self.settings.value("exclude_exts", [], type=list)
        self.recursive = self.settings.value("recursive", True, type=bool)
        self.theme = self.settings.value("theme", "light", type=str)
        last_path = self.settings.value("last_path", os.getcwd(), type=str)

        # UI
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top = QHBoxLayout()
        lbl = QLabel("Search in:")
        self.path_edit = QLineEdit(last_path)
        browse = QPushButton("📁 Browse")
        browse.clicked.connect(self.browse)
        options = QPushButton("⚙️ Options")


        scan = QPushButton("🔍 Start Scan")
        scan.clicked.connect(self.start_scan)
        scan.setStyleSheet("background: #28a745; color: white; font-weight: bold;")

        top.addWidget(lbl)
        top.addWidget(self.path_edit, 1)
        top.addWidget(browse)
        top.addWidget(scan)
        layout.addLayout(top)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["✓", "Filename", "Full Path", "Size (MB)"])
        self.tree.setColumnWidth(0, 50)
        self.tree.setColumnWidth(1, 300)
        self.tree.setColumnWidth(2, 400)
        self.tree.setAlternatingRowColors(True)
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

        btn_row.addWidget(select_all)
        btn_row.addWidget(deselect_all)
        btn_row.addStretch()
        btn_row.addWidget(delete_btn)
        btn_row.addWidget(refresh)
        layout.addLayout(btn_row)

        # Menu
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        file_menu.addAction("Open folder", self.browse)
        file_menu.addAction("Exit", self.close)

        options_menu = menubar.addMenu("Options")
        options_menu.addAction("Filter Extensions...", self.show_extensions_dialog)
        options_menu.addAction("Theme...", self.show_theme_dialog)

        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Help / Examples", self.show_help)
        help_menu.addAction("About DeDupe+", self.show_about)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.scan_status_label = QLabel("Ready")
        self.statusBar.addPermanentWidget(self.scan_status_label)   # right side

        self.thread = None
        self.current_groups = {}

        # Apply loaded theme
        self.apply_theme()

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
            dark_sheet = """
                QMainWindow, QDialog { background: #2b2b2b; color: #ddd; }
                QWidget { background: #2b2b2b; color: #ddd; }
                QTreeWidget { background: #1e1e1e; alternate-background-color: #282828; color: #ddd; }
                QTreeWidget::item:selected { background: #4a90d9; }
                QLineEdit, QComboBox, QCheckBox { background: #353535; color: #ddd; border: 1px solid #555; padding: 4px; }
                QPushButton { background: #404040; color: #ddd; border: 1px solid #555; padding: 6px; }
                QPushButton:hover { background: #505050; }
                QProgressBar { background: #353535; color: #ddd; border: 1px solid #555; text-align: center; }
                QProgressBar::chunk { background: #4a90d9; }
                QStatusBar { background: #353535; color: #ddd; }
                QMenuBar, QMenu { background: #2b2b2b; color: #ddd; }
                QMenu::item:selected { background: #4a90d9; }
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
            ", ".join(self.exclude_exts),
            self.recursive
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.include_exts, self.exclude_exts, self.recursive = dlg.get_settings()
            self.update_filter_status()

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
        elif self.exclude_exts:
            msg.append(f"Excl. {len(self.exclude_exts)} ext(s)")
        else:
            msg.append("All files")
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
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)

        # Reset status before starting
        self.statusBar.showMessage("Scan started...")
        self.scan_status_label.setText("Starting scan...")

        self.thread = ScanThread(path, self.include_exts, self.exclude_exts, self.recursive)

        # Connect both signals
        self.thread.progress.connect(self.on_scan_progress)
        self.thread.finished.connect(self.on_scan_finished)

        self.thread.start()

    def on_scan_progress(self, count: int, current_folder: str):
        display_folder = current_folder.replace(self.path_edit.text(), "").lstrip(os.sep)
        if not display_folder:
            display_folder = "(root)"

        self.scan_status_label.setText(
            f"Scanning... {count:,} files  →  {display_folder}"
        )

    def on_scan_finished(self, duplicates: dict):
        self.progress.setVisible(False)
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

            # Group header styling
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

                # Force readable text colors for all columns in both themes
                text_color = QColor("#000000") if not is_dark else QColor("#e8e8e8")   # black in light, light gray-white in dark
                dim_color  = QColor("#333333") if not is_dark else QColor("#bbbbbb")   # darker gray in light, medium gray in dark

                item.setForeground(1, text_color)   # Filename column
                item.setForeground(2, dim_color)    # Full path column (slightly dimmer)
                item.setForeground(3, dim_color)    # Size column (slightly dimmer)

                group_item.addChild(item)

            group_item.setExpanded(True)

        self.statusBar.showMessage(
            f"Found {count} duplicate groups "
            f"({sum(len(v) for v in duplicates.values())} files)"
        )

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