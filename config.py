"""إعدادات منظومة حَكَم العامة (المسارات، التشغيل، الأمان).

إعدادات المزودين والنماذج تُدار في settings.py (ملف providers.json + متغيرات البيئة).
"""
import os
import sys

from dotenv import load_dotenv

FROZEN = getattr(sys, "frozen", False)  # True داخل ملف EXE المبني بـ PyInstaller

# مجلد الموارد (templates/static): داخل حزمة PyInstaller أو بجانب الشيفرة
RESOURCE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def _default_data_dir() -> str:
    if os.getenv("HAKAM_DATA_DIR"):
        return os.getenv("HAKAM_DATA_DIR")
    if FROZEN or os.getenv("HAKAM_DESKTOP") == "1":
        base = os.getenv("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
        return os.path.join(base, "Hakam")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


DATA_DIR = _default_data_dir()
os.makedirs(DATA_DIR, exist_ok=True)

# .env بجانب الشيفرة أو داخل مجلد البيانات (مفيد لنسخة سطح المكتب)
load_dotenv()
load_dotenv(os.path.join(DATA_DIR, ".env"))

DESKTOP_MODE = FROZEN or os.getenv("HAKAM_DESKTOP") == "1"

DATABASE_PATH = os.getenv("HAKAM_DATABASE_PATH", os.path.join(DATA_DIR, "legal_agent.db"))
SETTINGS_PATH = os.getenv("HAKAM_SETTINGS_PATH", os.path.join(DATA_DIR, "providers.json"))

API_TIMEOUT = int(os.getenv("HAKAM_API_TIMEOUT", "120"))

# رمز المسؤول لصفحة الإعدادات في نسخة الويب. بدونه تكون الإعدادات للقراءة من متغيرات البيئة فقط.
ADMIN_TOKEN = os.getenv("HAKAM_ADMIN_TOKEN", "")
# رمز اختياري لحماية التطبيق كله على الويب (يطلبه المتصفح مرة واحدة)
ACCESS_TOKEN = os.getenv("HAKAM_ACCESS_TOKEN", "")

FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))
SECRET_KEY = os.getenv("HAKAM_SECRET_KEY") or os.urandom(24).hex()

DISCLAIMER_AR = "تنبيه: هذا رأي استشاري وليس بديلاً عن المشورة القانونية المتخصصة."
