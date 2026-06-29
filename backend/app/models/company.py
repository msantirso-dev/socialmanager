from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Company(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "companies"

    organization_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(500))
    website: Mapped[str | None] = mapped_column(String(500))
    brand_description: Mapped[str | None] = mapped_column(Text)
    tone: Mapped[str | None] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(10), default="es", nullable=False)
    colors: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    target_audience: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    products: Mapped[list | None] = mapped_column(JSONB, default=list)
    services: Mapped[list | None] = mapped_column(JSONB, default=list)
    custom_hashtags: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    forbidden_words: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)

    organization: Mapped["Organization"] = relationship(back_populates="companies")
    social_accounts: Mapped[list["SocialAccount"]] = relationship(back_populates="company")
    posts: Mapped[list["Post"]] = relationship(back_populates="company")
    assets: Mapped[list["Asset"]] = relationship(back_populates="company")
    prompts: Mapped[list["Prompt"]] = relationship(back_populates="company")
    ai_configs: Mapped[list["AIConfig"]] = relationship(back_populates="company")
    ai_history: Mapped[list["AIHistory"]] = relationship(back_populates="company")
    logs: Mapped[list["Log"]] = relationship(back_populates="company")
