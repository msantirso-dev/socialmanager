from sqlalchemy import Enum, Float, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import LogCategory
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Log(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "logs"
    __table_args__ = (Index("ix_logs_created_category", "created_at", "category"),)

    category: Mapped[LogCategory] = mapped_column(
        Enum(LogCategory, name="log_category"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    company_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL"),
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    error: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[float | None] = mapped_column(Float)
    cost: Mapped[float | None] = mapped_column(Numeric(10, 6))

    user: Mapped["User | None"] = relationship(back_populates="logs")
    company: Mapped["Company | None"] = relationship(back_populates="logs")
