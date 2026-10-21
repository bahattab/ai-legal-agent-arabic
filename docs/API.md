# واجهة البرمجة

## `POST /api/chat`
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "كيف أحمي فكرتي التجارية قبل عرضها على المستثمرين؟"}'
```
**الاستجابة 200:**
```json
{
  "conversation_id": 4,
  "response": "الرأي…\n\n---\nتنبيه: …",
  "final_response": {"opinion": "…", "disclaimer": "…"},
  "stages": {"A": {…}, "B": {"hypotheses": […], "passed_count": 2, "total_count": 3}, "D": {…}}
}
```
مخطط `stages` الكامل في `skills/hakam-legal-analysis/references/output-formats.md`.

**الأخطاء:** `400` إن كان السؤال فارغاً · `500` مع `{"error": "حدث خطأ أثناء المعالجة: …"}` عند فشل المزود.

لمتابعة قضية قائمة مرّر `"conversation_id": 4`.

## `GET /api/conversations`
قائمة `[{id, title, created_at, first_message}]` مرتبة من الأحدث.

## `GET /api/conversations/<id>`
قائمة الرسائل؛ حقل `metadata` نص JSON يحوي المراحل لرسائل `assistant`.
