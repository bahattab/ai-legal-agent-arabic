# قوالب المخرجات

## المرحلة A
```markdown
### 1. الوقائع المجردة (Raw Facts)
- ...
> ما لم يُذكر: ...

### 2. خريطة الأطراف (Parties Map)
- **الطرف**: الصفة والمصلحة

### 3. النوايا المكتشفة (Discovered Intent)
- الهدف المصرّح به: ...
- الهدف الضمني المحتمل: ...

### 4. النظام الحاكم (Governing Law Lock)
**النظام الأساسي**: ...
**أنظمة متقاطعة**: ...
**الافتراض المعتمد** (إن لم تُحدَّد الدولة): ...

### 5. بذور الفرضيات (Hypothesis Seeds)
- للمسار الحرفي: ...
- للمسار المقاصدي: ...
- للمسار الإجرائي: ...
```

## المرحلة B1 — لكل فرضية
```markdown
### الفرضية (الرؤية الحرفية | المقاصدية | الإجرائية)
**النظام المطبق**: ...
**المواد/القواعد الحاكمة**: ... (مع درجة اليقين إن لم يُتحقق من الرقم)
**التحليل**: 1. ... 2. ...
**الحكم وفق هذا المسار**: ...
**قوة الفرضية**: قوية | متوسطة | ضعيفة — السبب
```

## المرحلة B2 — تقييم الادعاء (JSON)
```json
{"score": 0.0, "issues": ["..."], "strengths": ["..."], "recommendation": "Accept | Revise | Reject"}
```

## المخطط الكامل (مطابق لحقل `metadata` في التطبيق)
```json
{
  "A": {"analysis": "markdown", "model": "string", "stage": "A"},
  "B": {
    "hypotheses": [{
      "hypothesis_type": "literal | purpose | procedural",
      "hypothesis_type_ar": "الرؤية الحرفية",
      "hypothesis": "markdown",
      "evaluation": {"score": 0.55, "issues": [], "strengths": [], "recommendation": "Reject"},
      "passed": false,
      "model": "string"
    }],
    "passed_count": 1,
    "total_count": 3
  },
  "D": {"final_opinion": "markdown", "disclaimer": "string", "verified_hypotheses_count": 1, "model": "string", "stage": "D"}
}
```
