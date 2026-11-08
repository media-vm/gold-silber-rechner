# -*- mode: python ; coding: utf-8 -*-


import sys
from PyInstaller.utils.hooks import collect_data_files

legacy = sys.version_info < (3, 9)

a = Analysis(
    ['gold-silver-value-calculator-german-v2.2.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('tzdata'),
    hiddenimports=['backports.zoneinfo'] if legacy else [],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['packaging/windows7-runtime-hook.py'] if legacy else [],
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
