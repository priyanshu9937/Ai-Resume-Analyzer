from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    content_type: str
    file_size: int
    created_at: datetime


class UploadResponse(BaseModel):
    resume: ResumeResponse
    metadata: dict[str, int | None] = Field(default_factory=dict)
    message: str = "Resume uploaded successfully"
