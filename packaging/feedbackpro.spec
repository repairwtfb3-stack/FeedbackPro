# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

ROOT = Path(SPECPATH).parent
SRC = ROOT / "src"
PKG = SRC / "feedbackpro"

datas = [
    (str(PKG / "Main.qml"), "feedbackpro"),
    (str(PKG / "build_meta.json"), "feedbackpro"),
]
for path in (PKG / "qml").rglob("*.qml"):
    relative_parent = path.parent.relative_to(PKG)
    datas.append((str(path), str(Path("feedbackpro") / relative_parent)))

a = Analysis(
    [str(ROOT / "packaging" / "windows" / "feedbackpro_entry.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FeedbackPro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    manifest=str(ROOT / "packaging" / "windows" / "app.manifest"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="FeedbackPro",
)
