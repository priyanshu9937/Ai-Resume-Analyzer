from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db
from app.models.resume import Resume
from app.schemas.analysis import JobMatchRequest, JobMatchResponse
from app.services.analysis import match_resume_to_job

router = APIRouter(prefix="/api/v1", tags=["job matching"])


@router.post("/job-match", response_model=JobMatchResponse)
async def job_match(request: JobMatchRequest, session: AsyncSession = Depends(get_db)) -> JobMatchResponse:
    resume = await session.get(Resume, request.resume_id)
    if not resume:
        raise AppError(404, "resource_not_found", "Resume not found")
    return JobMatchResponse(**await match_resume_to_job(session, resume, request.job_description))
