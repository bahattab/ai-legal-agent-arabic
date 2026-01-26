import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODELS = {
    "analyzer": "gpt-5.2",
    "hypothesis": "o4-mini",
    "verifier": "gpt-5-mini",
    "synthesizer": "gpt-5.2"
}

VERIFICATION_THRESHOLD = 0.7

DATABASE_PATH = "legal_agent.db"

API_TIMEOUT = 120

DISCLAIMER_AR = "تنبيه: هذا رأي استشاري وليس بديلاً عن المشورة القانونية المتخصصة."
