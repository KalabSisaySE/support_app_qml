# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the Macrosoft Support desktop application.

The version-info file is rendered by build_project.py before PyInstaller runs.
Build with: pyinstaller --noconfirm --distpath output --workpath build MacrosoftSupport.spec
"""

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('qml', 'qml'),
        ('images', 'images'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MacrosoftSupport',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/icon.ico',
    version='build/version_info_main.txt',
    uac_admin=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MacrosoftSupport',
)
