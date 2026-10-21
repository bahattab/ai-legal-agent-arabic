"""Stage A — التحليل الجنائي وقفل السياق."""
from config import MODELS

from . import base
from .prompts import ANALYZER_SYSTEM


async def analyze(question: str) -> dict:
    model = MODELS["analyzer"]
    analysis = await base.complete(model, ANALYZER_SYSTEM, f"سؤال المستخدم:\n{question}")
    return {"analysis": analysis, "model": model, "stage": "A"}
