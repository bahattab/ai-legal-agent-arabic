"""إعدادات منظومة حَكَم.

كل قيمة قابلة للتجاوز عبر متغيرات البيئة (ملف .env) دون تعديل الشيفرة.
"""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") or None  # لدعم OpenRouter أو بوابات متوافقة

MODELS = {
    "analyzer": os.getenv("HAKAM_MODEL_ANALYZER", "gpt-5.2"),
    "hypothesis": os.getenv("HAKAM_MODEL_HYPOTHESIS", "o4-mini"),
    "verifier": os.getenv("HAKAM_MODEL_VERIFIER", "gpt-5-mini"),
    "synthesizer": os.getenv("HAKAM_MODEL_SYNTHESIZER", "gpt-5.2"),
}

# الحد الأدنى لدرجة الفرضية (0.0–1.0) كي تُعدّ "مقبولة" بعد المداولة
VERIFICATION_THRESHOLD = float(os.getenv("HAKAM_VERIFICATION_THRESHOLD", "0.7"))

DATABASE_PATH = os.getenv("HAKAM_DATABASE_PATH", os.path.join("data", "legal_agent.db"))

API_TIMEOUT = int(os.getenv("HAKAM_API_TIMEOUT", "120"))

FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
PORT = int(os.getenv("PORT", "5000"))

DISCLAIMER_AR = "تنبيه: هذا رأي استشاري وليس بديلاً عن المشورة القانونية المتخصصة."
