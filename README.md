# حَكَم (Hakam) | Sovereign Legal Intelligence ⚖️

[![شرح مشروع حَكَم](https://img.youtube.com/vi/Xa93QZqtFvk/maxresdefault.jpg)](https://youtu.be/Xa93QZqtFvk)

> **اضغط على الصورة لمشاهدة فيديو الشرح التفصيلي للمشروع** 👆

**منظومة ذكاء اصطناعي قانوني متعددة الوكلاء (Multi-Agent) بالعربية، للتحليل الجنائي للنصوص، والتنقيب عن النوايا، والتقاضي الصوري قبل إصدار الرأي.**

> **تعريف المستودع:** "حَكَم" محكمة صورية رقمية مفتوحة المصدر تجيب عن الأسئلة القانونية بالعربية. لا تكتفي بإجابة واحدة، بل تفكّك الوقائع، وتبني ثلاث فرضيات مستقلة (حرفية، مقاصدية، إجرائية)، ثم يهاجمها "ادعاء عام" آلي ويمنح كل منها درجة، ولا يدخل في الرأي النهائي إلا ما اجتاز حد القبول. يأتي المشروع في صورتين: **تطبيق ويب** (Flask + OpenAI) بواجهة عربية وأرشيف للقضايا، و**مهارة AHLA** تنقل البروتوكول نفسه إلى Claude أو ChatGPT أو أي وكيل ذكاء اصطناعي.
>
> *Hakam is an open-source Arabic legal-reasoning engine: a multi-agent "moot court" that deconstructs facts, generates literal, purposive and procedural hypotheses, scores them with an adversarial verifier, and synthesizes a balanced opinion. Ships as a Flask web app and as the agent-agnostic AHLA skill.*

**لمن هذا المشروع؟** الباحثون القانونيون، والمحامون الذين يريدون مسودة تحليل أولية منظمة، ومطورو تطبيقات الذكاء الاصطناعي القانوني بالعربية، والأفراد الذين يريدون فهم موقفهم قبل استشارة محامٍ.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-black) ![License](https://img.shields.io/badge/License-MIT-green) ![RTL](https://img.shields.io/badge/UI-Arabic%20RTL-c9a24b)

---

## المحتويات
- [نظرة عامة](#-نظرة-عامة)
- [كيف يعمل](#-كيف-يعمل-hakam-kernel-v60)
- [المميزات](#-المميزات)
- [التثبيت والتشغيل](#️-التثبيت-والتشغيل)
- [طريقة الاستخدام والأمثلة](#-طريقة-الاستخدام)
- [الإعدادات](#️-الإعدادات)
- [واجهة البرمجة (API)](#-واجهة-البرمجة-api)
- [هيكلية المشروع](#️-هيكلية-المشروع)
- [مهارة الوكلاء (Agent Skill)](#-مهارة-الوكلاء-agent-skill)
- [الاختبارات](#-الاختبارات)
- [خارطة الطريق](#️-خارطة-الطريق)
- [إخلاء المسؤولية](#️-إخلاء-مسؤولية)

---

## 🌟 نظرة عامة

"حَكَم" ليس بوت دردشة، بل **محكمة صورية رقمية** تعمل في الخلفية: تفكّك سؤال المستخدم، وتعرضه على ثلاثة مسارات تفكير متوازية (حرفي، مقاصدي، إجرائي)، ثم تُخضع كل فرضية لمداولة صارمة يتولاها "ادعاء عام" مستقل، ولا يصل إلى الرأي النهائي إلا ما اجتاز حد القبول.

النتيجة رأي متوازن يعالج الثغرات صراحة، مع إمكانية الاطلاع على "مراحل التفكير" كاملة: التحليل، والفرضيات المقبولة والمرفوضة، ودرجة كل منها.

## 🧠 كيف يعمل (Hakam Kernel v6.0)

```mermaid
flowchart TB
    Q[سؤال المستخدم] --> A["A · المحقق<br/>تشريح الوقائع + قفل السياق"]
    A --> L[فرضية حرفية]
    A --> P[فرضية مقاصدية]
    A --> R[فرضية إجرائية]
    L --> V{"B · الادعاء العام<br/>درجة 0–1 لكل فرضية"}
    P --> V
    R --> V
    V -- "≥ 0.7 مقبولة" --> D["D · كبير المستشارين<br/>الحكم السيادي"]
    V -- "لا شيء مقبول ← الأعلى درجة + تصريح بعدم اليقين" --> D
    D --> O[الرأي + التنبيه القانوني]
```

| المرحلة | الوكيل | النموذج الافتراضي | المخرج |
|---|---|---|---|
| **A** Forensic Deconstruction + Context Lock | المحقق (`agents/analyzer.py`) | `gpt-5.2` | الوقائع، الأطراف، النوايا، النظام الحاكم، بذور الفرضيات |
| **B1** Multi-Path Reasoning | 3 مولّدات متوازية (`agents/hypothesis.py`) | `o4-mini` | فرضية حرفية + مقاصدية + إجرائية |
| **B2** Internal Moot Court | الادعاء العام (`agents/verifier.py`) | `gpt-5-mini` | `score`, `issues`, `strengths`, `recommendation` لكل فرضية |
| **D** Sovereign Verdict | كبير المستشارين (`agents/synthesizer.py`) | `gpt-5.2` | الرأي النهائي + التنبيه |

تفصيل أعمق في [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## 🚀 المميزات
- **معمارية متعددة الوكلاء** مع تنفيذ متوازٍ (`asyncio.gather`) للفرضيات والمداولة.
- **بوابة تحقق قابلة للضبط** (`HAKAM_VERIFICATION_THRESHOLD`، الافتراضي 0.7) مع مسار احتياطي آمن عند رفض كل الفرضيات.
- **واجهة عربية RTL** داكنة/ذهبية بخط Tajawal، متجاوبة مع الجوال، تعرض مراحل التفكير ودرجات الفرضيات.
- **أرشيف قضايا محلي** في SQLite مع حفظ كامل مراحل المعالجة لكل رد.
- **مزود قابل للتبديل**: أي بوابة متوافقة مع OpenAI (مثل OpenRouter) عبر `OPENAI_BASE_URL`، وأي نموذج لكل وكيل عبر متغيرات البيئة.
- **مهارة وكلاء مستقلة** تنفّذ البروتوكول نفسه داخل Claude أو أي وكيل آخر دون تشغيل التطبيق.

## 🛠️ التثبيت والتشغيل

**المتطلبات:** Python 3.10+ ومفتاح API لمزود متوافق مع OpenAI.

```bash
git clone https://github.com/bahattab/ai-legal-agent-arabic.git
cd ai-legal-agent-arabic

python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
# حرّر .env وضع OPENAI_API_KEY

python app.py
```
ثم افتح `http://localhost:5000`.

## 📘 طريقة الاستخدام

| الطريقة | ابدأ هكذا |
|---|---|
| **تطبيق الويب** | `python app.py` ثم افتح `http://localhost:5000`، اكتب الوقائع والسؤال، واضغط **عرض على المحكمة**. افتح "مراحل التفكير" لترى الفرضيات ودرجاتها. |
| **واجهة البرمجة** | `python examples/api_client.py --stages "سؤالك"` |
| **مهارة AHLA في أي وكيل** | `AHLA: سؤالك` · `AHLA full: سؤالك` (مع المراحل) · `AHLA json: سؤالك` (مخرج آلي) |

### مثال سريع
```text
AHLA full: في عقد عملي غير محدد المدة بند يمنعني من أي عمل لدى الغير حتى بدون أجر،
وتعويضي عن الفصل غير المشروع راتب شهر بينما تعويض الشركة ثلاثة أشهر. هل البندان صحيحان؟ (السعودية)
```
| المسار | الدرجة | القرار |
|---|---|---|
| الحرفي | 0.55 | مرفوضة — "لا نص يحظره ← صحيح مطلقاً" قفز منطقي |
| المقاصدي | 0.80 | مقبولة |
| الإجرائي | 0.65 | مرفوضة (تحتاج مراجعة) |

> على الرغم من أن لصاحب العمل أن يشترط التفرغ ويمنع تعارض المصالح أثناء العقد، إلا أن الصياغة المطلقة التي تحظر حتى المشورة غير المنافسة تُوزن بميزان المصلحة المشروعة والتناسب…

*(مقتطف توضيحي لشكل المخرج، وليس رأياً قانونياً معتمداً.)*

📖 **الدليل الكامل:** [`docs/USAGE.md`](docs/USAGE.md) — خطوات الواجهة، أمثلة curl وPowerShell وPython، تثبيت المهارة لكل وكيل، أربعة أمثلة مشروحة، واستكشاف الأخطاء.
🧪 **أمثلة جاهزة:** [`examples/`](examples/) — [`api_client.py`](examples/api_client.py)، [`sample_questions.md`](examples/sample_questions.md)، [`sample_response.json`](examples/sample_response.json).

## ⚙️ الإعدادات

كل الإعدادات في `.env` (انظر [`.env.example`](.env.example)):

| المتغير | الافتراضي | الوصف |
|---|---|---|
| `OPENAI_API_KEY` | — (مطلوب) | مفتاح المزود |
| `OPENAI_BASE_URL` | فارغ | بوابة متوافقة، مثل `https://openrouter.ai/api/v1` |
| `HAKAM_MODEL_ANALYZER` | `gpt-5.2` | نموذج المرحلة A |
| `HAKAM_MODEL_HYPOTHESIS` | `o4-mini` | نموذج الفرضيات |
| `HAKAM_MODEL_VERIFIER` | `gpt-5-mini` | نموذج الادعاء |
| `HAKAM_MODEL_SYNTHESIZER` | `gpt-5.2` | نموذج الحكم |
| `HAKAM_VERIFICATION_THRESHOLD` | `0.7` | حد قبول الفرضية |
| `HAKAM_DATABASE_PATH` | `data/legal_agent.db` | مسار قاعدة البيانات |
| `HAKAM_API_TIMEOUT` | `120` | مهلة الطلب بالثواني |
| `FLASK_DEBUG` / `PORT` | `0` / `5000` | وضع التطوير والمنفذ |

> ⚠️ لا تفعّل `FLASK_DEBUG=1` على خادم مكشوف للشبكة.

## 🔌 واجهة البرمجة (API)

| الطريقة | المسار | الوصف |
|---|---|---|
| `POST` | `/api/chat` | `{"question": "...", "conversation_id": 1?}` ← الرأي + المراحل |
| `GET` | `/api/conversations` | قائمة القضايا المؤرشفة |
| `GET` | `/api/conversations/<id>` | رسائل قضية مع `metadata` المراحل |

أمثلة كاملة ومخطط الاستجابة في [`docs/API.md`](docs/API.md).

## 🏗️ هيكلية المشروع

```
ai-legal-agent-arabic/
├── app.py                      # خادم Flask ونقاط الـ API
├── config.py                   # الإعدادات (قابلة للتجاوز من .env)
├── database.py                 # أرشيف SQLite
├── agents/                     # عقل النظام
│   ├── prompts.py              # موجّهات بروتوكول Hakam Kernel v6.0
│   ├── base.py                 # طبقة الاتصال بالنموذج
│   ├── analyzer.py             # A: التحليل الجنائي
│   ├── hypothesis.py           # B1: الفرضيات الثلاث
│   ├── verifier.py             # B2: المحكمة الصورية
│   └── synthesizer.py          # D: الحكم النهائي
├── pipeline/
│   └── orchestrator.py         # المايسترو: A → B → D
├── templates/index.html        # الواجهة
├── static/{css,js}/            # التنسيق ومنطق الواجهة
├── skills/0 - arabic-hakam-legal-analysis  # مهارة AHLA لأي وكيل
├── examples/                   # عميل API، أسئلة تجريبية، نموذج رد
├── docs/                       # التوثيق التقني
├── tests/                      # اختبارات بلا استدعاء نماذج حقيقية
├── data/                       # قاعدة البيانات المحلية (مستبعدة من git)
├── .env.example
└── requirements.txt
```

## 🧩 مهارة الوكلاء (AHLA)

المجلد [`skills/0 - arabic-hakam-legal-analysis`](skills/0%20-%20arabic-hakam-legal-analysis/SKILL.md) ينقل البروتوكول إلى أي وكيل ذكاء اصطناعي، ويُشغَّل بكلمة **`AHLA`** (Arabic Hakam Legal Analysis).

- **وكلاء يدعمون المهارات** (Claude Code، Claude، Codex، Gemini CLI، OpenCode، Cursor…): انسخ المجلد إلى مجلد المهارات.
  ```bash
  cp -r "skills/0 - arabic-hakam-legal-analysis" ~/.claude/skills/
  ```
- **وكلاء بلا مهارات** (ChatGPT، Custom GPT، API): الصق [`AGENTS.md`](skills/0%20-%20arabic-hakam-legal-analysis/AGENTS.md) في التعليمات النظامية.

التفاصيل والفروق بين المهارة والتطبيق في [`docs/USAGE.md`](docs/USAGE.md#3-مهارة-ahla-لأي-وكيل-ذكاء-اصطناعي).

## 🧪 الاختبارات

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```
تستبدل الاختبارات طبقة النموذج بدالة وهمية وتتحقق من: مخطط المراحل، حد القبول، المسار الاحتياطي، والتعامل مع رد JSON تالف من الادعاء.

## 🗺️ خارطة الطريق
- [ ] استرجاع نصوص الأنظمة (RAG) من مصادر رسمية لتقليل خطر المواد غير المتحقق منها.
- [ ] بث المراحل للواجهة لحظياً (SSE) بدل الانتظار حتى نهاية المعالجة.
- [ ] تمرير سياق المحادثة السابقة إلى الوكلاء في الأسئلة المتتابعة.
- [ ] مصادقة المستخدمين قبل أي نشر عام.

## ⚠️ إخلاء مسؤولية

نظام "حَكَم" يقدم رأياً استشارياً مبنياً على نماذج الذكاء الاصطناعي، وقد تخطئ هذه النماذج في أرقام المواد أو نصوصها. مخرجات النظام **لا تغني بأي حال عن المشورة القانونية الرسمية** من محامٍ مرخص، والمطورون غير مسؤولين عن أي استخدام لها أمام الجهات القضائية.

## 📄 الرخصة

مرخص بموجب [MIT License](LICENSE).
