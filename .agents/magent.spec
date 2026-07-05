# Codex-only Multi-Agent Orchestration Framework
# PyInstaller spec for building standalone executable

import sys
from pathlib import Path

block_cipher = None

# Get base directory
base_dir = Path('.').resolve()

# Collect data files (only what exists)
data_files = [
    ('scripts', 'scripts'),
    ('ui', 'ui'),
]

# Add optional directories if they exist
import os
if os.path.exists('../skills'):
    data_files.append(('../skills', 'skills'))

a = Analysis(
    ['magent.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        'yaml',
        'psutil',
        'config_manager',
        'error_handler',
        'manual_execution',
        'checkpoint_executor',
        'streaming_executor',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='magent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
)
