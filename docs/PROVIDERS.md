# إضافة مزودي الذكاء الاصطناعي

يعمل حَكَم مع **أي مزود** من نوعين:

| النوع | يشمل |
|---|---|
| `openai` — متوافق مع OpenAI | OpenAI، OpenRouter، Google Gemini، DeepSeek، Groq، Mistral، xAI (Grok)، Together AI، Ollama، LM Studio، vLLM، LiteLLM، Azure عبر بوابة متوافقة، أو أي خادم يقدّم `/v1/chat/completions` |
| `anthropic` — أصلي | Claude عبر `api.anthropic.com/v1/messages` |

## من الواجهة (الأسهل)
1. افتح **⚙ مزودو الذكاء الاصطناعي والنماذج** من الشريط الجانبي (أو `/settings`).
   - على الويب: أدخل `HAKAM_ADMIN_TOKEN` أولاً.
2. اختر قالباً من القائمة (أو "مزود مخصص") ثم **+ إضافة مزود**.
3. أدخل مفتاح API، واضغط **جلب النماذج** لتظهر النماذج المتاحة كاقتراحات.
4. في **تعيين النماذج للوكلاء** اختر لكل وكيل مزوداً ونموذجاً.
5. **اختبار الاتصال** ثم **حفظ الإعدادات**. التغيير يسري من السؤال التالي دون إعادة تشغيل.

أسماء النماذج في القوالب اقتراحات فقط وقد تتغير لدى المزود؛ "جلب النماذج" يعرض القائمة الفعلية لحسابك.

## مثال توزيع عملي
| الوكيل | الدور | اقتراح |
|---|---|---|
| المحقق (A) | تشريح الوقائع | نموذج قوي متوسط الكلفة |
| الفرضيات (B1) | 3 استدعاءات متوازية | نموذج سريع ورخيص |
| الادعاء (B2) | 3 تقييمات JSON | نموذج من **مزود مختلف** عن الفرضيات ليكون النقد مستقلاً |
| كبير المستشارين (D) | الرأي النهائي | أقوى نموذج متاح |

## مزودات محلية (بلا إنترنت ولا مفاتيح)
- **Ollama:** `ollama serve` ثم أضف قالب Ollama (`http://localhost:11434/v1`) واترك المفتاح فارغاً.
- **LM Studio:** شغّل Local Server ثم قالب LM Studio (`http://localhost:1234/v1`).
- النماذج المحلية الصغيرة قد لا تلتزم بصيغة JSON للادعاء؛ عندها تُرفض الفرضية بدرجة 0 بدل أن يتعطل الطلب.

## من متغيرات البيئة (للاستضافة والحاويات)
### حفظ المفتاح خارج الملف
في حقل المفتاح اكتب `env:ANTHROPIC_API_KEY` بدل المفتاح، واضبط المتغير في الاستضافة. هكذا لا يُكتب أي سر في `providers.json`.

### الإعدادات كاملة في متغير واحد
`HAKAM_SETTINGS_JSON` يغلب ملف الإعدادات ويقفل صفحة الإعدادات (للقراءة فقط):
```json
{
  "providers": [
    {"id": "openrouter", "name": "OpenRouter", "type": "openai",
     "base_url": "https://openrouter.ai/api/v1", "api_key": "env:OPENROUTER_API_KEY"},
    {"id": "claude", "name": "Anthropic", "type": "anthropic",
     "base_url": "https://api.anthropic.com", "api_key": "env:ANTHROPIC_API_KEY"}
  ],
  "agents": {
    "analyzer":    {"provider": "openrouter", "model": "openai/gpt-5-mini"},
    "hypothesis":  {"provider": "openrouter", "model": "deepseek/deepseek-chat"},
    "verifier":    {"provider": "openrouter", "model": "google/gemini-2.5-flash"},
    "synthesizer": {"provider": "claude",     "model": "claude-sonnet-4-5"}
  },
  "verification_threshold": 0.7
}
```

### التوافق مع الإصدارات السابقة
إن لم توجد إعدادات محفوظة، تُبنى تلقائياً من `OPENAI_API_KEY` و`OPENAI_BASE_URL` و`HAKAM_MODEL_*`.

## ترتيب الأولوية
`HAKAM_SETTINGS_JSON` ← ملف `providers.json` (صفحة الإعدادات) ← القيم الافتراضية من متغيرات البيئة.

## مزود جديد كلياً
إن كان المزود يقدّم واجهة متوافقة مع OpenAI فلا حاجة لأي شيفرة: أضفه كـ "مخصص". لنوع واجهة مختلف، أضف دالة في `agents/base.py` على نمط `_anthropic_complete` وسجّلها في `_DISPATCH` وفي `PROVIDER_TYPES` داخل `settings.py`.
