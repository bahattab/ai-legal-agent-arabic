"""Stage A — التحليل الجنائي وقفل السياق."""
import settings

from . import base
from .prompts import ANALYZER_SYSTEM


async def analyze(question: str) -> dict:
    analysis = await base.complete("analyzer", ANALYZER_SYSTEM, f"سؤال المستخدم:\n{question}")
    return {"analysis": analysis, "model": settings.model_name("analyzer"), "stage": "A"}
