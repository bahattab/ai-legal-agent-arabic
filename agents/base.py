"""طبقة الاتصال بمزودي الذكاء الاصطناعي — نقطة واحدة يمكن استبدالها في الاختبارات.

الأنواع المدعومة:
- openai    : أي مزود متوافق مع OpenAI Chat Completions (OpenAI، OpenRouter، Gemini، DeepSeek،
              Groq، Mistral، xAI، Together، Ollama، LM Studio، أو خادمك الخاص).
- anthropic : واجهة Anthropic Messages الأصلية (Claude).
"""
import json
import re

import httpx
from openai import AsyncOpenAI, BadRequestError

import settings
from config import API_TIMEOUT

def _openai_client(provider: dict) -> AsyncOpenAI:
    """عميل جديد لكل استدعاء: كل طلب HTTP يشغّل حلقة asyncio جديدة، ولا يجوز إعادة استخدام
    اتصالات مرتبطة بحلقة أُغلقت."""
    key = settings.resolve_key(provider.get("api_key", "")) or "not-needed"  # المزودات المحلية لا تحتاج مفتاحاً
    return AsyncOpenAI(api_key=key, base_url=provider["base_url"], timeout=API_TIMEOUT)


async def _openai_complete(provider, model, system, user, json_mode):
    async with _openai_client(provider) as client:
        return await _openai_call(client, model, system, user, json_mode)


async def _openai_call(client, model, system, user, json_mode):
    kwargs = {"model": model,
              "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    try:
        response = await client.chat.completions.create(**kwargs)
    except BadRequestError:
        if not json_mode:
            raise
        # بعض المزودات لا تدعم response_format؛ الموجّه نفسه يطلب JSON فنعيد المحاولة بدونه
        kwargs.pop("response_format")
        response = await client.chat.completions.create(**kwargs)
    return (response.choices[0].message.content or "").strip()


async def _anthropic_complete(provider, model, system, user, json_mode):
    key = settings.resolve_key(provider.get("api_key", ""))
    if not key:
        raise RuntimeError(f"لم يُضبط مفتاح API للمزود {provider['name']}")
    if json_mode:
        system += "\n\nأعد كائن JSON صالحاً فقط، دون أي نص قبله أو بعده."
    url = provider["base_url"].rstrip("/") + "/v1/messages"
    payload = {"model": model, "max_tokens": 8192, "system": system,
               "messages": [{"role": "user", "content": user}]}
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        r = await client.post(url, json=payload, headers=headers)
    if r.status_code >= 400:
        raise RuntimeError(f"Anthropic {r.status_code}: {r.text[:300]}")
    return "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text").strip()


_DISPATCH = {"openai": _openai_complete, "anthropic": _anthropic_complete}


async def complete(role: str, system: str, user: str, json_mode: bool = False) -> str:
    """يستدعي النموذج المعيّن للوكيل `role` ويعيد النص."""
    provider, model = settings.agent_target(role)
    return await _DISPATCH[provider["type"]](provider, model, system, user, json_mode)


async def test_provider(provider: dict, model: str) -> str:
    """اختبار اتصال سريع من صفحة الإعدادات."""
    return await _DISPATCH[provider["type"]](provider, model, "Reply with the single word: OK", "ping", False)


async def list_models(provider: dict) -> list:
    """يجلب قائمة النماذج من المزود إن كان يدعم ذلك."""
    key = settings.resolve_key(provider.get("api_key", ""))
    base = provider["base_url"].rstrip("/")
    if provider["type"] == "anthropic":
        url, headers = base + "/v1/models", {"x-api-key": key, "anthropic-version": "2023-06-01"}
    else:
        url, headers = base + "/models", ({"Authorization": f"Bearer {key}"} if key else {})
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=headers)
    r.raise_for_status()
    items = r.json().get("data", [])
    return sorted({i.get("id", "") for i in items if i.get("id")})


def parse_json(text: str) -> dict:
    """يستخرج أول كائن JSON من الرد، متسامحاً مع أسوار ```json."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise
