# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PalFriend Bootstrapper Launcher (palfriendlauncher.exe)

This spec file configures PyInstaller to create a standalone GUI bootstrapper
that installs and launches the main PalFriend application.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

# Get the base directory
block_cipher = None
base_dir = os.path.abspath(os.path.dirname(SPEC))

# Data files for bootstrapper (minimal - just the launcher itself)
datas = []

# Add VERSION file
version_path = os.path.join(base_dir, 'VERSION')
if os.path.exists(version_path):
    datas.append((version_path, '.'))

# In a production build, you would also bundle the palfriend executable here
# as a payload to be extracted during installation:
# palfriend_bundle = os.path.join(base_dir, 'dist', 'palfriend')
# if os.path.exists(palfriend_bundle):
#     datas.append((palfriend_bundle, 'palfriend_payload'))

# Hidden imports - minimal for the bootstrapper
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.scrolledtext',
    'tkinter.messagebox',
]

# Analysis
a = Analysis(
    ['bootstrap_launcher.py'],
    pathex=[base_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy dependencies not needed for the bootstrapper
        'numpy',
        'torch',
        'chromadb',
        'sentence_transformers',
        'transformers',
        'flask',
        'flask_cors',
        'flask_socketio',
        'socketio',
        'engineio',
        'TikTokLive',
        'websockets',
        'openai',
        'sounddevice',
        'soundfile',
        'aiosqlite',
        'tiktoken',
        'vaderSentiment',
        'pydantic',
        # Test dependencies
        'pytest',
        'black',
        'flake8',
        'mypy',
        # Other GUI libraries
        'matplotlib',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Post-analysis: Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable as onefile for easy distribution
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='palfriendlauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console - pure GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Can add icon file path here if available
)
