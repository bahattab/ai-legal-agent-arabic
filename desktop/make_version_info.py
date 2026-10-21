"""يولّد desktop/version_info.txt (بيانات ملف EXE في Windows) من version.py."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v = re.search(r'__version__ = "([^"]+)"', open(os.path.join(ROOT, "version.py"), encoding="utf-8").read()).group(1)
t = tuple(int(x) for x in (v.split(".") + ["0"] * 4)[:4])
open(os.path.join(ROOT, "desktop", "version_info.txt"), "w", encoding="utf-8").write(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={t}, prodvers={t}, mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'Hakam Project'),
      StringStruct('FileDescription', 'Hakam - Arabic Legal Intelligence'),
      StringStruct('FileVersion', '{v}'),
      StringStruct('InternalName', 'Hakam'),
      StringStruct('LegalCopyright', 'MIT License - Python Arabic Community, Bahattab'),
      StringStruct('OriginalFilename', 'Hakam.exe'),
      StringStruct('ProductName', 'Hakam'),
      StringStruct('ProductVersion', '{v}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""")
print(v)
