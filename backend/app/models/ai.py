from sqlalchemy import Float, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Prompt(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "prompts"

    company_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    category: Mapped[str | None] = mapped_column(String(100))

    company: Mapped["Company"] = relationship(back_populates="prompts")


class AIHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_history"
    __table_args__ = (Index("ix_ai_history_company_created", "company_id", "created_at"),)

    post_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="SET NULL"),
    )
    company_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    capability: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str | None] = mapped_column(Text)
    cost: Mapped[float | None] = mapped_column(Numeric(10, 6))
    duration_ms: Mapped[float | None] = mapped_column(Float)
    tokens_used: Mapped[int | None] = mapped_column(Integer)

    post: Mapped["Post | None"] = relationship(back_populates="ai_history")
    company: Mapped["Company"] = relationship(back_populates="ai_history")


class AIConfig(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "ai_configs"

    company_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    text_provider: Mapped[str | None] = mapped_column(String(50))
    text_model: Mapped[str | None] = mapped_column(String(100))
    image_provider: Mapped[str | None] = mapped_column(String(50))
    image_model: Mapped[str | None] = mapped_column(String(100))
    hashtag_provider: Mapped[str | None] = mapped_column(String(50))
    ideas_provider: Mapped[str | None] = mapped_column(String(50))

    company: Mapped["Company"] = relationship(back_populates="ai_configs")
