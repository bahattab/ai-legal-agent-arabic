"""المايسترو: يدير التدفق A → B (توليد + مداولة) → D."""
import asyncio

import agents


class LegalPipeline:
    @staticmethod
    async def process(question: str) -> dict:
        stage_a = await agents.analyze(question)
        analysis = stage_a["analysis"]

        hypotheses = await agents.generate_all(question, analysis)
        evaluated = await asyncio.gather(*(agents.verify(question, analysis, h) for h in hypotheses))
        evaluated = list(evaluated)
        passed = [h for h in evaluated if h["passed"]]
        stage_b = {"hypotheses": evaluated, "passed_count": len(passed), "total_count": len(evaluated)}

        fallback = not passed
        selected = passed or sorted(evaluated, key=lambda h: h["evaluation"]["score"], reverse=True)[:1]
        stage_d = await agents.synthesize(question, analysis, selected, fallback=fallback)

        return {
            "stages": {"A": stage_a, "B": stage_b, "D": stage_d},
            "final_response": {"opinion": stage_d["final_opinion"], "disclaimer": stage_d["disclaimer"]},
        }
