"""Stage D — صياغة الحكم السيادي النهائي."""
import settings
from config import DISCLAIMER_AR

from . import base
from .prompts import SYNTHESIZER_SYSTEM


def _render(h: dict) -> str:
    ev = h["evaluation"]
    issues = "\n".join(f"- {i}" for i in ev.get("issues", [])) or "- لا يوجد"
    return f"#### {h['hypothesis_type_ar']} (درجة {ev['score']:.2f})\n{h['hypothesis']}\n\nملاحظات الادعاء:\n{issues}"


async def synthesize(question: str, analysis: str, verified: list, fallback: bool) -> dict:
    model = settings.model_name("synthesizer")
    note = ("\n\nتنبيه داخلي: لم تجتز أي فرضية حد القبول؛ هذه أعلى الفرضيات درجة. "
            "صرّح للسائل بدرجة عدم اليقين واطلب المعلومات الناقصة.") if fallback else ""
    user = (f"سؤال المستخدم:\n{question}\n\nالتحليل الجنائي:\n{analysis}\n\n"
            "الفرضيات المعتمدة:\n" + "\n\n".join(_render(h) for h in verified) + note)
    opinion = await base.complete("synthesizer", SYNTHESIZER_SYSTEM, user)
    return {"final_opinion": opinion, "disclaimer": DISCLAIMER_AR,
            "verified_hypotheses_count": 0 if fallback else len(verified), "model": model, "stage": "D"}
