"""اختبار خط المعالجة كاملاً دون استدعاء أي نموذج حقيقي."""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("OPENAI_API_KEY", "test")

import agents.base as base  # noqa: E402
from pipeline import LegalPipeline  # noqa: E402


def fake_llm(scores):
    async def _complete(model, system, user, json_mode=False):
        if json_mode:
            for track, score in scores.items():
                if track in user:
                    return json.dumps({"score": score, "issues": ["ثغرة"], "strengths": [], "recommendation": "Accept"})
            return "{}"
        if "المحقق الأول" in system:
            return "### 1. الوقائع المجردة (Raw Facts)\n- واقعة"
        if "مولّد فرضيات" in system:
            return "فرضية"
        return "على الرغم من ... إلا أن ..."
    return _complete


def run(scores):
    base.complete = fake_llm(scores)
    return asyncio.run(LegalPipeline.process("سؤال تجريبي"))


def test_schema_and_threshold():
    r = run({"الرؤية الحرفية": 0.55, "الرؤية المقاصدية": 0.85, "الرؤية الإجرائية": 0.6})
    assert set(r["stages"]) == {"A", "B", "D"}
    assert r["stages"]["B"]["passed_count"] == 1 and r["stages"]["B"]["total_count"] == 3
    assert r["stages"]["D"]["verified_hypotheses_count"] == 1
    assert r["final_response"]["opinion"].startswith("على الرغم")
    assert "تنبيه" in r["final_response"]["disclaimer"]


def test_fallback_when_none_pass():
    r = run({"الرؤية الحرفية": 0.2, "الرؤية المقاصدية": 0.3, "الرؤية الإجرائية": 0.1})
    assert r["stages"]["B"]["passed_count"] == 0
    assert r["stages"]["D"]["verified_hypotheses_count"] == 0


def test_bad_verifier_json_is_rejected_not_crash():
    async def broken(model, system, user, json_mode=False):
        return "ليس JSON" if json_mode else "نص"
    base.complete = broken
    r = asyncio.run(LegalPipeline.process("س"))
    assert all(not h["passed"] for h in r["stages"]["B"]["hypotheses"])
