from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.db.session import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse, UploadResponse
from app.services.upload import parse_upload, save_upload, validate_upload

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...), session: AsyncSession = Depends(get_db)) -> UploadResponse:
    settings = get_settings()
    content = await file.read(settings.max_upload_size_bytes + 1)
    extension, stored_filename = validate_upload(file.filename, file.content_type, content, settings)
    parsed_document = await run_in_threadpool(parse_upload, content, extension)
    path = await run_in_threadpool(save_upload, stored_filename, content, settings)
    resume = Resume(original_filename=file.filename or "resume", stored_filename=stored_filename, content_type=file.content_type or "", file_size=len(content), file_path=str(path), extracted_text=parsed_document.text)
    session.add(resume)
    await session.commit()
    await session.refresh(resume)
    return UploadResponse(resume=ResumeResponse.model_validate(resume), metadata={"page_count": parsed_document.page_count, "paragraph_count": parsed_document.paragraph_count})
