"""طبقة الاتصال بنموذج اللغة — نقطة واحدة يمكن استبدالها في الاختبارات."""
import json
import re

from openai import AsyncOpenAI

from config import API_TIMEOUT, OPENAI_API_KEY, OPENAI_BASE_URL

_client = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY غير مضبوط. أضفه إلى ملف .env")
        _client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL, timeout=API_TIMEOUT)
    return _client


async def complete(model: str, system: str, user: str, json_mode: bool = False) -> str:
    """يستدعي النموذج ويعيد النص. لا يمرَّر temperature لأن نماذج الاستدلال (o-series) ترفضه."""
    kwargs = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = await get_client().chat.completions.create(**kwargs)
    return (response.choices[0].message.content or "").strip()


def parse_json(text: str) -> dict:
    """يستخرج أول كائن JSON من الرد، متسامحاً مع أسوار ```json."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise
