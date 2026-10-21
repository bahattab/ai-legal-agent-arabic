"""عميل بسيط لواجهة حَكَم البرمجية.

الاستخدام:
    python examples/api_client.py "سؤالك"
    python examples/api_client.py --stages "سؤالك"
    python examples/api_client.py --batch examples/sample_questions.md
    python examples/api_client.py --url http://localhost:5000 --conversation 4 "سؤال متابعة"

يتطلب أن يكون التطبيق يعمل (python app.py). لا يحتاج مكتبات خارجية.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request


def ask(url, question, conversation_id=None, timeout=300):
    payload = {"question": question}
    if conversation_id:
        payload["conversation_id"] = conversation_id
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/chat",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            body = json.loads(body).get("error", body)
        except json.JSONDecodeError:
            pass
        raise SystemExit(f"خطأ {e.code}: {body}")
    except urllib.error.URLError as e:
        raise SystemExit(f"تعذّر الاتصال بـ {url} — هل التطبيق يعمل؟ ({e.reason})")


def print_stages(data):
    b = data["stages"]["B"]
    print(f"\nالمداولة: {b['passed_count']} من {b['total_count']} فرضيات مقبولة")
    print(f"{'المسار':<18}{'الدرجة':>8}  القرار     أبرز ثغرة")
    for h in b["hypotheses"]:
        ev = h["evaluation"]
        issue = (ev.get("issues") or ["—"])[0][:70]
        print(f"{h['hypothesis_type_ar']:<18}{ev['score']:>8.2f}  {'مقبولة ' if h['passed'] else 'مرفوضة'}   {issue}")
    if data["stages"]["D"].get("verified_hypotheses_count") == 0:
        print("⚠ لم تجتز أي فرضية الحد؛ الرأي مبني على الأعلى درجة — تعامل معه بحذر.")


def questions_from_file(path):
    """يقرأ الأسئلة من أسطر تبدأ بـ '- ' أو أرقام في ملف Markdown."""
    text = open(path, encoding="utf-8").read()
    return [m.group(1).strip() for m in re.finditer(r"^\s*(?:[-*]|\d+[.)])\s+(.+)$", text, re.M)]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="عميل واجهة حَكَم")
    p.add_argument("question", nargs="?")
    p.add_argument("--url", default="http://localhost:5000")
    p.add_argument("--conversation", type=int)
    p.add_argument("--stages", action="store_true", help="اطبع جدول الفرضيات ودرجاتها")
    p.add_argument("--batch", help="ملف Markdown فيه قائمة أسئلة")
    p.add_argument("--json", action="store_true", help="اطبع الرد كاملاً بصيغة JSON")
    a = p.parse_args()

    questions = questions_from_file(a.batch) if a.batch else [a.question]
    if not questions or not questions[0]:
        p.error("مرّر سؤالاً أو --batch")

    for i, q in enumerate(questions, 1):
        if len(questions) > 1:
            print(f"\n{'=' * 60}\n[{i}/{len(questions)}] {q}")
        data = ask(a.url, q, a.conversation)
        if a.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
            continue
        print(f"\n(القضية رقم {data['conversation_id']})\n")
        print(data["response"])
        if a.stages:
            print_stages(data)


if __name__ == "__main__":
    main()
