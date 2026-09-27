from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class JobMatch(Base):
    __tablename__ = "job_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_id: Mapped[str] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"))
    job_description: Mapped[str] = mapped_column(Text)
    match_score: Mapped[int] = mapped_column(Integer)
    matched_keywords: Mapped[list[str]] = mapped_column(JSON)
    missing_keywords: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resume: Mapped["Resume"] = relationship()