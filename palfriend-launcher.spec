# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PalFriend Windows Launcher

This spec file configures PyInstaller to create a Windows executable
that includes all necessary dependencies and data files.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Get the base directory
block_cipher = None
base_dir = os.path.abspath(os.path.dirname(SPEC))

# Collect all necessary data files
datas = []

# Add frontend build directory if it exists
frontend_build = os.path.join(base_dir, 'frontend', 'build')
if os.path.exists(frontend_build):
    datas.append((frontend_build, 'frontend/build'))

# Add example configuration files
for config_file in ['settings.yaml.example', '.env.example']:
    config_path = os.path.join(base_dir, config_file)
    if os.path.exists(config_path):
        datas.append((config_path, '.'))

# Add documentation files
for doc_file in ['README.md', 'WEB_INTERFACE_README.md', 'TTS_README.md']:
    doc_path = os.path.join(base_dir, doc_file)
    if os.path.exists(doc_path):
        datas.append((doc_path, '.'))

# Collect data files from packages that need them
try:
    datas += collect_data_files('chromadb')
except Exception:
    pass

try:
    datas += collect_data_files('sentence_transformers')
except Exception:
    pass

try:
    datas += collect_data_files('tiktoken')
except Exception:
    pass

try:
    datas += collect_data_files('vaderSentiment')
except Exception:
    pass

# Hidden imports - modules that PyInstaller might miss
hiddenimports = [
    # Core modules
    'settings',
    'memory',
    'speech',
    'events',
    'utils',
    'response',
    'outbox',
    'gui',
    # Submodules
    'modules.audio',
    'modules.tts',
    'modules.personality_bias',
    # Flask and related
    'flask',
    'flask_cors',
    'flask_socketio',
    'socketio',
    'engineio',
    # TikTok
    'TikTokLive',
    'TikTokLive.events',
    'TikTokLive.client',
    # WebSocket
    'websockets',
    'websockets.legacy',
    'websockets.legacy.client',
    # OpenAI
    'openai',
    # Audio
    'sounddevice',
    'soundfile',
    # AI/ML libraries
    'chromadb',
    'sentence_transformers',
    'transformers',
    'torch',
    'numpy',
    'tiktoken',
    # Database
    'aiosqlite',
    'sqlite3',
    # YAML
    'yaml',
    # Other
    'dotenv',
    'vaderSentiment',
    'Levenshtein',
    'pydantic',
    'pydantic_core',
]

# Collect all submodules for complex packages
try:
    hiddenimports += collect_submodules('flask_socketio')
except Exception:
    pass

try:
    hiddenimports += collect_submodules('socketio')
except Exception:
    pass

try:
    hiddenimports += collect_submodules('engineio')
except Exception:
    pass

try:
    hiddenimports += collect_submodules('TikTokLive')
except Exception:
    pass

# Analysis
a = Analysis(
    ['launcher.py'],
    pathex=[base_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test and dev dependencies
        'pytest',
        'black',
        'flake8',
        'mypy',
        # Exclude GUI libraries we don't need
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

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='palfriend-launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console window for logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Can add icon file path here if available
)
