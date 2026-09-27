import json
import re
from collections.abc import Mapping
from typing import Protocol

import httpx

from app.core.config import Settings
from app.core.errors import AIUnavailableError
from app.schemas.analysis import ResumeAnalysis


class LLMProvider(Protocol):
    async def analyze_resume(self, text: str) -> ResumeAnalysis: ...


class GeminiProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def analyze_resume(self, text: str) -> ResumeAnalysis:
        if not self.settings.gemini_api_key:
            return fallback_analysis(text)
        prompt = "Return only valid JSON matching this schema: " + json.dumps(ResumeAnalysis.model_json_schema()) + "\nResume:\n" + text[:40_000]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.settings.gemini_model}:generateContent"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, params={"key": self.settings.gemini_api_key}, json={"contents": [{"parts": [{"text": prompt}]}]})
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
            raise AIUnavailableError("The AI analysis service is unavailable") from exc
        raw = payload["candidates"][0]["content"]["parts"][0]["text"]
        return parse_llm_response(raw, text)


def parse_llm_response(raw: str, source_text: str) -> ResumeAnalysis:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return fallback_analysis(source_text)
    try:
        return ResumeAnalysis.model_validate(json.loads(match.group(0)))
    except (json.JSONDecodeError, ValueError, TypeError):
        return fallback_analysis(source_text)


def fallback_analysis(text: str) -> ResumeAnalysis:
    skills = sorted({word.lower() for word in re.findall(r"\b[A-Za-z][A-Za-z+#.-]{2,}\b", text) if word.lower() in {"python", "sql", "fastapi", "django", "java", "javascript", "typescript", "aws", "docker", "git", "react", "postgresql"}})
    score = min(100, len(skills) * 8 + (20 if len(text) > 500 else 0))
    return ResumeAnalysis(skills=skills, strengths=["Resume text was successfully extracted"], improvements=["Add measurable outcomes to experience bullets"], ats_score=score, overall_score=score)
