# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import os, sys, pymediainfo

block_cipher = None

# Collect PyQt6 platform plugins
datas = collect_data_files("PyQt6", subdir="plugins/platforms")

# Include assets directory
assets_data = [(os.path.abspath('assets') + '/**', 'assets')]

# Bundle MediaInfo.dll from pymediainfo package
mi_dir = os.path.dirname(pymediainfo.__file__)
mi_dll = os.path.join(mi_dir, "MediaInfo.dll")
mediainfo_binaries = [(mi_dll, 'pymediainfo')] if os.path.exists(mi_dll) else []

a = Analysis(
    ['DeDupe+.py'],
    pathex=['.'],
    binaries=mediainfo_binaries,
    datas=assets_data + datas,
    hiddenimports=['pymediainfo'],
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
    console=False,
    icon='assets/DepDupe-icon.ico',
    version='version_info.txt',
)