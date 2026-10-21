# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — يبني نسختين: مجلد (للمثبّت) وملف واحد محمول.
# التشغيل من جذر المستودع:  pyinstaller desktop/hakam.spec --noconfirm
import os, re

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))
VERSION = re.search(r'__version__ = "([^"]+)"', open(os.path.join(ROOT, "version.py"), encoding="utf-8").read()).group(1)
ICON = os.path.join(ROOT, "desktop", "assets", "hakam.ico")

datas = [(os.path.join(ROOT, "templates"), "templates"), (os.path.join(ROOT, "static"), "static")]
hidden = ["waitress", "webview", "webview.platforms.edgechromium", "webview.platforms.winforms", "clr_loader"]

def make_analysis():
    return Analysis([os.path.join(ROOT, "desktop.py")], pathex=[ROOT], datas=datas, hiddenimports=hidden,
                    excludes=["tkinter", "pytest", "gunicorn"], noarchive=False)

# نسخة المجلد (يغلّفها Inno Setup) — إقلاع أسرع
a = make_analysis()
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="Hakam", icon=ICON, console=False,
          version=os.path.join(ROOT, "desktop", "version_info.txt"), upx=False)
COLLECT(exe, a.binaries, a.datas, name="Hakam", upx=False)

# النسخة المحمولة: ملف EXE واحد
b = make_analysis()
pyz_b = PYZ(b.pure)
EXE(pyz_b, b.scripts, b.binaries, b.datas, [], name=f"Hakam-{VERSION}-portable", icon=ICON, console=False,
    version=os.path.join(ROOT, "desktop", "version_info.txt"), upx=False, runtime_tmpdir=None)
