# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import os, PySide6

block_cipher = None

# Collect PySide6 platform plugins
datas = collect_data_files("PySide6", subdir="plugins/platforms")

# Include assets directory
assets_data = [(os.path.abspath('assets') + '/**', 'assets')]

a = Analysis(
    ['DeDupe+.py'],
    pathex=['.'],
    binaries=[],
    datas=assets_data + datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DeDupe+',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application, no console
    icon='assets/DepDupe-icon.ico',  # Windows requires .ico
	version='version_info.txt',
)