from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import SchedulerJobStatus
from app.models.mixins import UUIDPrimaryKeyMixin


class SchedulerJob(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "scheduler_jobs"

    post_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[SchedulerJobStatus] = mapped_column(
        Enum(SchedulerJobStatus, name="scheduler_job_status"),
        nullable=False,
        default=SchedulerJobStatus.PENDING,
    )
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)

    post: Mapped["Post"] = relationship(back_populates="scheduler_jobs")
