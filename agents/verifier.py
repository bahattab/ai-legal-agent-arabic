"""Stage B (2/2) — المحكمة الصورية: تقييم كل فرضية ونسف الضعيف منها."""
from config import MODELS, VERIFICATION_THRESHOLD

from . import base
from .prompts import VERIFIER_SYSTEM


async def verify(question: str, analysis: str, hypothesis: dict) -> dict:
    model = MODELS["verifier"]
    user = (
        f"سؤال المستخدم:\n{question}\n\nالتحليل الجنائي:\n{analysis}\n\n"
        f"الفرضية المعروضة ({hypothesis['hypothesis_type_ar']}):\n{hypothesis['hypothesis']}"
    )
    try:
        evaluation = base.parse_json(await base.complete(model, VERIFIER_SYSTEM, user, json_mode=True))
        score = max(0.0, min(1.0, float(evaluation.get("score", 0))))
    except (ValueError, TypeError) as exc:
        evaluation, score = {"issues": [f"تعذّر تحليل تقييم الادعاء: {exc}"], "strengths": [],
                             "recommendation": "Reject"}, 0.0
    evaluation["score"] = score
    evaluation.setdefault("issues", [])
    evaluation.setdefault("strengths", [])
    evaluation.setdefault("recommendation", "Accept" if score >= VERIFICATION_THRESHOLD else "Reject")
    return {**hypothesis, "evaluation": evaluation, "passed": score >= VERIFICATION_THRESHOLD, "model": model}
