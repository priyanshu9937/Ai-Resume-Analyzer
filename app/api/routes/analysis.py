from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_llm_provider
from app.db.session import get_db
from app.schemas.analysis import AnalysisResponse
from app.services.analysis import analyze_resume, get_stored_analysis
from app.services.llm import LLMProvider

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.post("/{resume_id}", response_model=AnalysisResponse)
async def create_analysis(resume_id: str, regenerate: bool = Query(False), session: AsyncSession = Depends(get_db), provider: LLMProvider = Depends(get_llm_provider)) -> AnalysisResponse:
    result, source = await analyze_resume(session, resume_id, provider, regenerate)
    return AnalysisResponse(resume_id=resume_id, analysis=result, source=source)


@router.get("/{resume_id}", response_model=AnalysisResponse)
async def get_analysis(resume_id: str, session: AsyncSession = Depends(get_db)) -> AnalysisResponse:
    result, source = await get_stored_analysis(session, resume_id)
    return AnalysisResponse(resume_id=resume_id, analysis=result, source=source)
