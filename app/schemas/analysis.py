from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    summary: str = ""


class ATSBreakdown(BaseModel):
    section_score: int = Field(default=0, ge=0, le=100)
    keyword_score: int = Field(default=0, ge=0, le=100)
    contact_score: int = Field(default=0, ge=0, le=100)
    formatting_score: int = Field(default=0, ge=0, le=100)
    issues: list[str] = Field(default_factory=list)


class ResumeAnalysis(BaseModel):
    candidate: CandidateProfile = Field(default_factory=CandidateProfile)
    skills: list[str] = Field(default_factory=list)
    experience_years: float = Field(default=0, ge=0, le=80)
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    ats_score: int = Field(default=0, ge=0, le=100)
    overall_score: int = Field(default=0, ge=0, le=100)
    sections: dict[str, str] = Field(default_factory=dict)
    ats: ATSBreakdown = Field(default_factory=ATSBreakdown)


class AnalysisResponse(BaseModel):
    resume_id: str
    analysis: ResumeAnalysis
    source: str = "llm"


class JobMatchRequest(BaseModel):
    resume_id: str = Field(min_length=1, max_length=36)
    job_description: str = Field(min_length=20, max_length=30_000)


class JobMatchResponse(BaseModel):
    resume_id: str
    match_score: int = Field(ge=0, le=100)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
