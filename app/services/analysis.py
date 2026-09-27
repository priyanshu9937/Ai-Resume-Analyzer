from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.models.job_match import JobMatch
from app.models.resume import Resume
from app.parsers.text import detect_sections
from app.schemas.analysis import ATSBreakdown, ResumeAnalysis
from app.core.errors import AppError
from app.services.feedback import generate_resume_feedback
from app.services.llm import LLMProvider
from app.services.scoring import ats_score, job_match


class ResourceNotFoundError(AppError):
    def __init__(self, message: str = "Resume not found") -> None:
        super().__init__(404, "resource_not_found", message)


class AnalysisNotFoundError(AppError):
    def __init__(self) -> None:
        super().__init__(404, "analysis_not_found", "Analysis not found")


async def analyze_resume(session: AsyncSession, resume_id: str, provider: LLMProvider, regenerate: bool = False) -> tuple[ResumeAnalysis, str]:
    resume = await session.get(Resume, resume_id)
    if not resume:
        raise ResourceNotFoundError("Resume not found")
    stored = await session.scalar(select(Analysis).where(Analysis.resume_id == resume_id))
    if stored and not regenerate:
        return ResumeAnalysis.model_validate(stored.result), "stored"
    result = await provider.analyze_resume(resume.extracted_text)
    sections = detect_sections(resume.extracted_text)
    result.sections = sections
    result.strengths, result.improvements = generate_resume_feedback(resume.extracted_text, sections, result.skills)
    calculated_ats = ats_score(resume.extracted_text)
    result.ats_score = max(result.ats_score, calculated_ats)
    result.ats = ATSBreakdown(
        section_score=min(100, len(sections) * 15),
        keyword_score=result.ats_score,
        contact_score=20 if result.candidate.email or result.candidate.phone else 0,
        formatting_score=min(100, 40 + len(sections) * 10),
        issues=[] if result.ats_score >= 60 else ["Add clearer sections and measurable achievements"],
    )
    result.overall_score = max(result.overall_score, result.ats_score)
    if stored:
        stored.result = result.model_dump()
    else:
        session.add(Analysis(resume_id=resume_id, result=result.model_dump()))
    await session.commit()
    return result, "llm"


async def get_stored_analysis(session: AsyncSession, resume_id: str) -> tuple[ResumeAnalysis, str]:
    if not await session.get(Resume, resume_id):
        raise ResourceNotFoundError()
    stored = await session.scalar(select(Analysis).where(Analysis.resume_id == resume_id))
    if not stored:
        raise AnalysisNotFoundError()
    return ResumeAnalysis.model_validate(stored.result), "stored"


def match_job(resume: Resume, job_description: str) -> dict:
    score, matched, missing = job_match(resume.extracted_text, job_description)
    return {"resume_id": resume.id, "match_score": score, "matched_keywords": matched, "missing_keywords": missing, "matched_skills": matched, "missing_skills": missing, "recommendations": [f"Consider adding evidence for: {', '.join(missing[:5])}"] if missing else ["Your resume covers the main job-description terms"]}


async def match_resume_to_job(session: AsyncSession, resume: Resume, job_description: str) -> dict:
    result = match_job(resume, job_description)
    session.add(JobMatch(resume_id=resume.id, job_description=job_description, match_score=result["match_score"], matched_keywords=result["matched_keywords"], missing_keywords=result["missing_keywords"]))
    await session.commit()
    return result
