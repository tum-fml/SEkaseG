# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['sekaseg_tool.py'],
    pathex=[],
    binaries=[],
    datas=[('Ionic-Ionicons-Home.32.png', '.'), ('Pictogrammers-Material-Forklift.ico', '.'), ('Microsoft-Fluentui-Emoji-Mono-New-Button.48.png', '.'), ('Ionic-Ionicons-Trash.32.png', '.'), ('Ionic-Ionicons-Eye-outline.32.png', '.'), ('Microsoft-Fluentui-Emoji-Mono-New-Button.32.png', '.'), ('Ionic-Ionicons-Megaphone-outline.32.png', '.'), ('Github-Octicons-Bell-24.32.png', '.'), ('Ionic-Ionicons-Save-outline.32.png', '.'), ('Github-Octicons-Bell-slash-24.32.png', '.'), ('Ionic-Ionicons-Enter-outline.32.png', '.'), ('Ionic-Ionicons-Pencil-outline.32.png', '.'), ('Ionic-Ionicons-Exit-outline.32.png', '.'), ('Ionic-Ionicons-Eye-off.32.png', '.'), ('Microsoft-Fluentui-Emoji-Mono-Open-File-Folder.32.png', '.'), ('Amitjakhu-Drip-Copy.32.png', '.'), ('Ionic-Ionicons-Trash.48.png', '.'), ('Ionic-Ionicons-Arrow-back.32.png', '.'), ('Ionic-Ionicons-Arrow-forward.32.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='sekaseg_tool',
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
)
