# -*- mode: python ; coding: utf-8 -*-


import os
import sys
from PyInstaller.utils.hooks import collect_data_files

legacy = sys.version_info < (3, 9)
runtime_hooks = []
if os.environ.get('GSR_WINDOWS_LANGUAGE') == 'es':
    runtime_hooks.append('packaging/windows-spanish-runtime-hook.py')
if legacy:
    runtime_hooks.append('packaging/windows7-runtime-hook.py')

a = Analysis(
    ['gold-silver-value-calculator-german-v2.2.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('tzdata'),
    hiddenimports=['backports.zoneinfo'] if legacy else [],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=runtime_hooks,
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Gold-Silber-Rechner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['gold-silber-icon.ico'],
    version='version-info.txt',
)
