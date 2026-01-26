# حَكَم (Hakam) | Sovereign Legal Intelligence ⚖️

[![شرح مشروع حَكَم](https://img.youtube.com/vi/Xa93QZqtFvk/maxresdefault.jpg)](https://youtu.be/Xa93QZqtFvk)

> **اضغط على الصورة لمشاهدة فيديو الشرح التفصيلي للمشروع** 👆

---

**منظومة ذكاء اصطناعي قانوني سيادي متعددة الوكلاء (Multi-Agent) مصممة للتحليل الجنائي للنصوص، التنقيب عن النوايا، والتقاضي الصوري.**

## 🌟 نظرة عامة (Overview)

"حَكَم" ليس مجرد "بوت دردشة"، بل هو **محكمة صورية رقمية** تعمل في الخلفية لضمان دقة الاستشارة القانونية. يقوم النظام بتفكيك سؤال المستخدم، عرضه على ثلاثة مسارات تفكير متوازية (حرفية، مقاصدية، إجرائية)، ثم إجراء مداولة صارمة (Verification) قبل صياغة الحكم النهائي.

### المنهجية القانونية (Hakam Kernel v6.0)
يعمل النظام وفق بروتوكول "حَكَم" السيادي الذي يتضمن:
1.  **Forensic Deconstruction**: تشريح النص وفصل الوقائع عن الرغبات (Unreliable Narrator).
2.  **Context Lock**: تحديد النظام الحاكم بدقة (Context Lock Protocol).
3.  **Multi-Path Reasoning**: توليد فرضيات متوازية (Literal, Purpose, Procedural).
4.  **Internal Moot Court**: محكمة صورية داخلية تهاجم الفرضيات لكشف الثغرات.
5.  **Sovereign Verdict**: صياغة حكم نهائي متوازن بلغة قانونية رصينة.

---

## 🚀 المميزات (Features)

- **معمارية متعددة الوكلاء (Multi-Agent Architecture)**:
    - **Analyzer (GPT-5.2)**: المحقق الأول (تشريح الوقائع).
    - **Hypothesis Generators (o4-mini)**: 3 وكلاء (حرفي، مقاصدي، إجرائي).
    - **Verifier (GPT-5-mini)**: الادعاء العام (التدقيق ونسف الفرضيات الضعيفة).
    - **Synthesizer (GPT-5.2)**: كبير المستشارين (صياغة الحكم).
- **واجهة مستخدم احترافية**: تصميم RTL عربي بالكامل، داكن/ذهبي، يعكس الفخامة والسيادة.
- **تتبع مراحل التفكير**: إمكانية رؤية ما يدور في "عقل" النظام (التحليل، الفرضيات المرفوضة والمقبولة).
- **أرشيف القضايا**: تخزين محلي (SQLite) لكافة الاستشارات للرجوع إليها.

---

## 🛠️ التثبيت والتشغيل (Installation)

### المتطلبات المسبقة
- Python 3.10+
- مفتاح API صالح من OpenAI (يدعم `gpt-4o` وما بعدها).

### خطوات التثبيت

1. **استنسخ المستودع**:
   ```bash
   git clone https://github.com/your-username/hakam-legal-agent.git
   cd hakam-legal-agent
   ```

2. **أنشئ بيئة افتراضية**:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **ثبت المكتبات**:
   ```bash
   pip install -r requirements.txt
   ```

4. **إعداد المتغيرات البيئية**:
   - قم بإنشاء ملف `.env` في المجلد الرئيسي.
   - أضف مفتاحك:
     ```env
     OPENAI_API_KEY=sk-your-key-here
     ```

5. **تشغيل التطبيق**:
   ```bash
   python app.py
   ```
   - افتح المتصفح على: `http://localhost:5000`

---

## 🏗️ هيكلية المشروع (Project Structure)

```
hakam-legal-agent/
├── agents/                 # عقل النظام (الوكلاء)
│   ├── analyzer.py         # Stage A: التحليل الجنائي
│   ├── hypothesis.py       # Stage B: توليد الفرضيات
│   ├── verifier.py         # Stage B: المحكمة الصورية
│   └── synthesizer.py      # Stage D: الحكم النهائي
├── pipeline/
│   └── orchestrator.py     # المايسترو (إدارة التدفق)
├── static/
│   ├── css/                # التنسيقات (Tajawal Font)
│   └── js/                 # منطق الواجهة
├── templates/
│   └── index.html          # واجهة المستخدم
├── database.py             # إدارة SQLite
├── config.py               # إعدادات النماذج
└── app.py                  # خادم Flask
```

---

## ⚠️ إخلاء مسؤولية (Disclaimer)

نظام "حَكَم" يقدم رأياً استشارياً مبنياً على خوارزميات الذكاء الاصطناعي. رغم دقة المنهجية المتبعة، إلا أن مخرجات النظام **لا تغني بأي حال من الأحوال عن المشورة القانونية الرسمية** من محامٍ مرخص. المطورون غير مسؤولين عن أي استخدام للمعلومات الواردة في النظام أمام الجهات القضائية.

---

## 📄 الرخصة (License)

هذا المشروع مرخص بموجب [MIT License](LICENSE).
