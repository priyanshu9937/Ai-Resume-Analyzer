from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_id: Mapped[str] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), unique=True)
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resume: Mapped["Resume"] = relationship(back_populates="analysis")
