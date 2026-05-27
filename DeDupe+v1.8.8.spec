# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect assets folder (images, icons, gifs, etc.)
assets_data = [(os.path.abspath('assets'), 'assets')]

a = Analysis(
    ['DeDupe+v1.8.8.py'],
    pathex=['.'],
    binaries=[],
    datas=collect_data_files('PySide6', subdir='plugins/platforms') + assets_data,
    hiddenimports=[
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.sip',
        'pymediainfo',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt6.QtBluetooth',
        'PyQt6.QtNfc',
        'PyQt6.QtSensors',
        'PyQt6.QtPositioning',
        'PyQt6.QtWebEngineCore',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    console=False,                    # Set to True for debugging
    icon='assets/DepDupe-icon.ico',   # Your Windows icon
    version='version_info.txt',
    onefile=True,                     # Single executable
)