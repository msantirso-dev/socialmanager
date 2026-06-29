from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import SocialNetwork
from app.models.mixins import UUIDPrimaryKeyMixin


class SocialAccount(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "social_accounts"

    company_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    network: Mapped[SocialNetwork] = mapped_column(
        Enum(SocialNetwork, name="social_network"),
        nullable=False,
    )
    external_account_id: Mapped[str | None] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255))
    profile_picture_url: Mapped[str | None] = mapped_column(String(500))
    is_connected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)

    company: Mapped["Company"] = relationship(back_populates="social_accounts")
    tokens: Mapped[list["Token"]] = relationship(back_populates="social_account")
    posts: Mapped[list["Post"]] = relationship(back_populates="social_account")


class Token(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "tokens"

    social_account_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("social_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_refreshed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    social_account: Mapped["SocialAccount"] = relationship(back_populates="tokens")
