"""إدارة مزودي الذكاء الاصطناعي وتعيين نموذج لكل وكيل.

مصدر الإعدادات بالترتيب (الأعلى يغلب):
1. متغير البيئة HAKAM_SETTINGS_JSON (كائن JSON كامل — مناسب للاستضافة).
2. ملف providers.json في مجلد البيانات (تكتبه صفحة الإعدادات).
3. القيم الافتراضية المبنية من متغيرات البيئة القديمة (OPENAI_API_KEY، HAKAM_MODEL_*).

يمكن الإشارة لمفتاح API عبر متغير بيئة بكتابة "env:اسم_المتغير" بدل المفتاح نفسه،
فلا يُحفظ المفتاح في الملف.
"""
import copy
import json
import os
import re
import tempfile
import threading

from config import SETTINGS_PATH

AGENT_ROLES = ("analyzer", "hypothesis", "verifier", "synthesizer")
AGENT_LABELS_AR = {
    "analyzer": "المحقق (المرحلة A)",
    "hypothesis": "مولّدو الفرضيات (B1)",
    "verifier": "الادعاء العام (B2)",
    "synthesizer": "كبير المستشارين (D)",
}

PROVIDER_TYPES = ("openai", "anthropic")

# قوالب جاهزة تظهر في صفحة الإعدادات؛ أي مزود متوافق مع OpenAI يمكن إضافته كـ "custom"
PRESETS = [
    {"id": "openai", "name": "OpenAI", "type": "openai", "base_url": "https://api.openai.com/v1",
     "models": ["gpt-5.2", "gpt-5-mini", "o4-mini"]},
    {"id": "openrouter", "name": "OpenRouter", "type": "openai", "base_url": "https://openrouter.ai/api/v1",
     "models": ["anthropic/claude-sonnet-4.5", "openai/gpt-5-mini", "google/gemini-2.5-pro"]},
    {"id": "anthropic", "name": "Anthropic (Claude)", "type": "anthropic", "base_url": "https://api.anthropic.com",
     "models": ["claude-sonnet-4-5", "claude-haiku-4-5"]},
    {"id": "gemini", "name": "Google Gemini", "type": "openai",
     "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "models": ["gemini-2.5-pro", "gemini-2.5-flash"]},
    {"id": "deepseek", "name": "DeepSeek", "type": "openai", "base_url": "https://api.deepseek.com",
     "models": ["deepseek-chat", "deepseek-reasoner"]},
    {"id": "groq", "name": "Groq", "type": "openai", "base_url": "https://api.groq.com/openai/v1", "models": []},
    {"id": "mistral", "name": "Mistral", "type": "openai", "base_url": "https://api.mistral.ai/v1",
     "models": ["mistral-large-latest"]},
    {"id": "xai", "name": "xAI (Grok)", "type": "openai", "base_url": "https://api.x.ai/v1", "models": []},
    {"id": "together", "name": "Together AI", "type": "openai", "base_url": "https://api.together.xyz/v1", "models": []},
    {"id": "ollama", "name": "Ollama (محلي)", "type": "openai", "base_url": "http://localhost:11434/v1", "models": []},
    {"id": "lmstudio", "name": "LM Studio (محلي)", "type": "openai", "base_url": "http://localhost:1234/v1", "models": []},
    {"id": "custom", "name": "مزود مخصص متوافق مع OpenAI", "type": "openai", "base_url": "", "models": []},
]

_lock = threading.Lock()
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,39}$")


def _env_defaults() -> dict:
    """إعدادات افتراضية متوافقة مع الإصدارات السابقة (OPENAI_API_KEY + HAKAM_MODEL_*)."""
    return {
        "providers": [{
            "id": "openai",
            "name": "OpenAI" if not os.getenv("OPENAI_BASE_URL") else "OpenAI-compatible",
            "type": "openai",
            "base_url": os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1",
            "api_key": "env:OPENAI_API_KEY",
        }],
        "agents": {
            "analyzer": {"provider": "openai", "model": os.getenv("HAKAM_MODEL_ANALYZER", "gpt-5.2")},
            "hypothesis": {"provider": "openai", "model": os.getenv("HAKAM_MODEL_HYPOTHESIS", "o4-mini")},
            "verifier": {"provider": "openai", "model": os.getenv("HAKAM_MODEL_VERIFIER", "gpt-5-mini")},
            "synthesizer": {"provider": "openai", "model": os.getenv("HAKAM_MODEL_SYNTHESIZER", "gpt-5.2")},
        },
        "verification_threshold": float(os.getenv("HAKAM_VERIFICATION_THRESHOLD", "0.7")),
    }


def source() -> str:
    if os.getenv("HAKAM_SETTINGS_JSON"):
        return "env"
    if os.path.exists(SETTINGS_PATH):
        return "file"
    return "defaults"


def load() -> dict:
    """يعيد الإعدادات كاملة (مع المفاتيح كما هي — للاستخدام الداخلي فقط)."""
    raw = os.getenv("HAKAM_SETTINGS_JSON")
    if raw:
        data = json.loads(raw)
    elif os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    else:
        data = _env_defaults()
    return validate(data)


def validate(data: dict) -> dict:
    """يتحقق من البنية ويرمي ValueError برسالة عربية واضحة عند الخطأ."""
    if not isinstance(data, dict):
        raise ValueError("الإعدادات يجب أن تكون كائن JSON")
    providers = data.get("providers") or []
    if not isinstance(providers, list) or not all(isinstance(p, dict) for p in providers):
        raise ValueError("قائمة المزودين غير صالحة")
    agents_raw = data.get("agents") or {}
    if not isinstance(agents_raw, dict) or not all(isinstance(a, dict) for a in agents_raw.values()):
        raise ValueError("تعيين الوكلاء غير صالح")
    ids = set()
    for p in providers:
        pid = str(p.get("id", "")).strip()
        if not _ID_RE.match(pid):
            raise ValueError(f"معرّف مزود غير صالح: '{pid}' (أحرف إنجليزية صغيرة وأرقام و - _ فقط)")
        if pid in ids:
            raise ValueError(f"معرّف المزود مكرر: {pid}")
        if p.get("type") not in PROVIDER_TYPES:
            raise ValueError(f"نوع مزود غير مدعوم: {p.get('type')} (المدعوم: {', '.join(PROVIDER_TYPES)})")
        if not str(p.get("base_url", "")).startswith(("http://", "https://")):
            raise ValueError(f"عنوان Base URL للمزود {pid} يجب أن يبدأ بـ http:// أو https://")
        ids.add(pid)
    agents = data.get("agents") or {}
    for role in AGENT_ROLES:
        a = agents.get(role)
        if not a or not a.get("provider") or not a.get("model"):
            raise ValueError(f"لم يُحدَّد مزود ونموذج للوكيل: {AGENT_LABELS_AR[role]}")
        if a["provider"] not in ids:
            raise ValueError(f"الوكيل {AGENT_LABELS_AR[role]} يشير لمزود غير موجود: {a['provider']}")
    try:
        t = float(data.get("verification_threshold", 0.7))
    except (TypeError, ValueError):
        raise ValueError("حد القبول يجب أن يكون رقماً") from None
    if not 0.0 <= t <= 1.0:
        raise ValueError("حد القبول يجب أن يكون بين 0 و 1")
    data["verification_threshold"] = t
    return data


def resolve_key(value: str) -> str:
    value = value or ""
    if value.startswith("env:"):
        return os.getenv(value[4:], "")
    return value


def mask(value: str) -> str:
    if not value:
        return ""
    if value.startswith("env:"):
        return value  # مرجع متغير بيئة، ليس سراً
    return "••••" + value[-4:] if len(value) > 8 else "••••"


def public_view() -> dict:
    """نسخة آمنة للعرض في المتصفح: المفاتيح مخفية."""
    data = copy.deepcopy(load())
    for p in data["providers"]:
        p["api_key_set"] = bool(resolve_key(p.get("api_key", "")))
        p["api_key"] = mask(p.get("api_key", ""))
    return data


def save(new: dict) -> dict:
    """يحفظ الإعدادات. المفتاح المخفي (يبدأ بـ ••••) أو الفارغ يعني: احتفظ بالمفتاح القديم."""
    if os.getenv("HAKAM_SETTINGS_JSON"):
        raise PermissionError("الإعدادات مضبوطة عبر متغير البيئة HAKAM_SETTINGS_JSON ولا يمكن تعديلها من الواجهة")
    with _lock:
        if not isinstance(new, dict) or not isinstance(new.get("providers", []), list):
            raise ValueError("الإعدادات يجب أن تكون كائن JSON")
        old = {p["id"]: p for p in load()["providers"]}
        for p in new.get("providers", []):
            if not isinstance(p, dict):
                continue
            # original_id يسمح بإعادة تسمية المعرّف دون فقدان المفتاح المحفوظ
            prev = old.get(p.pop("original_id", None) or p.get("id"), {})
            key = (p.get("api_key") or "").strip()
            if not key or key.startswith("••••"):
                # لا يُعاد استخدام المفتاح المحفوظ إلا لنفس العنوان (يمنع إرساله لخادم آخر)
                p["api_key"] = prev.get("api_key", "") if prev.get("base_url") == p.get("base_url") else ""
            p.pop("api_key_set", None)
        data = validate(new)
        folder = os.path.dirname(SETTINGS_PATH) or "."
        os.makedirs(folder, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".providers-", suffix=".tmp", dir=folder)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, SETTINGS_PATH)
        try:
            os.chmod(SETTINGS_PATH, 0o600)
        except OSError:
            pass
    return data


def agent_target(role: str) -> tuple:
    """يعيد (إعدادات المزود، اسم النموذج) لوكيل معين."""
    data = load()
    a = data["agents"][role]
    provider = next(p for p in data["providers"] if p["id"] == a["provider"])
    return provider, a["model"]


def threshold() -> float:
    return load()["verification_threshold"]


def model_name(role: str) -> str:
    try:
        provider, model = agent_target(role)
        return f"{provider['id']}/{model}"
    except Exception:  # noqa: BLE001 — للعرض فقط
        return "unknown"
