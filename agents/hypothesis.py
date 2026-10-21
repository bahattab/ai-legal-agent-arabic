"""Stage B (1/2) — توليد ثلاث فرضيات متوازية: حرفية، مقاصدية، إجرائية."""
import asyncio

from config import MODELS

from . import base
from .prompts import HYPOTHESIS_SYSTEM, HYPOTHESIS_TRACKS


async def generate_one(track: str, question: str, analysis: str) -> dict:
    spec = HYPOTHESIS_TRACKS[track]
    system = HYPOTHESIS_SYSTEM.format(instruction=spec["instruction"], track_ar=spec["ar"])
    user = f"سؤال المستخدم:\n{question}\n\nالتحليل الجنائي (Stage A):\n{analysis}"
    text = await base.complete(MODELS["hypothesis"], system, user)
    return {"hypothesis_type": track, "hypothesis_type_ar": spec["ar"], "hypothesis": text}


async def generate_all(question: str, analysis: str) -> list:
    return await asyncio.gather(*(generate_one(t, question, analysis) for t in HYPOTHESIS_TRACKS))
