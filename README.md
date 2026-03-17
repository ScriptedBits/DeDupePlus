# DeDupe+ – Smart Duplicate File Finder

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-orange)](https://www.riverbankcomputing.com/software/pyqt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
-
[![GitHub release](https://img.shields.io/github/v/release/ScriptedBits/DeDupePlus?color=green)](https://github.com/ScriptedBits/DeDupePlus/releases)
![GitHub All Releases](https://img.shields.io/github/downloads/ScriptedBits/DeDupePlus/total)
![GitHub issues](https://img.shields.io/github/issues/ScriptedBits/DeDupePlus)

**DeDupe+** is a cross-platform desktop application that helps you find and remove **duplicate files** by intelligently matching filenames — even when they have different extensions, quality tags (4K, HDR, WEB-DL), years in parentheses/brackets, or minor variations.

Perfect for cleaning up movie collections, subtitle mismatches, ROM libraries, photo backups, and more.

https://github.com/ScriptedBits/DeDupePlus

## Features

- **Smart name-based duplicate detection**  
  Recognizes `movie (2025).mp4` and `movie 4k (2025).mkv` or `file1.mp4` and `file1.srt` as duplicates

- **Flexible extension filtering**  
  - Include only specific types (e.g. videos + subtitles)  
  - Exclude unwanted files (e.g. `.jpg`, `.nfo`, `.txt`)  
  - Quick presets: **Video files** & **Retro ROMs**

- **Light & Dark theme support** (saved between sessions)

- **Recursive folder scanning** (toggleable)

- **Visual tree view** with checkboxes to select what to delete

- **Size preview** (MB) – largest files sorted first

- **Safe deletion** with confirmation dialog

- **Cross-platform**: Windows, macOS, Linux

- **Portable** – no installation required (just run the `.py` or compiled executable)

## Screenshots

### Dark Mode
 
<img width="824" height="547" alt="DeDupe+ main screen" src="https://github.com/user-attachments/assets/542db951-9306-4763-bf06-6917253c1c64" />


## Requirements

- Python 3.8+
- PyQt6 (`pip install PyQt6`)

## Installation

### Option 1: Run from source (recommended for development)

```bash
git clone https://github.com/ScriptedBits/DeDupePlus.git
cd DeDupePlus
pip install -r requirements.txt    # if you create one, otherwise:
pip install PyQt6
python DepDup+v1.5.py              # or whatever your main file is named
