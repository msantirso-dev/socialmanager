from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import PostStatus, PostType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Post(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "posts"
    __table_args__ = (
        Index("ix_posts_company_status_scheduled", "company_id", "status", "scheduled_at"),
        Index("ix_posts_social_account_status", "social_account_id", "status"),
    )

    company_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    social_account_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("social_accounts.id", ondelete="SET NULL"),
    )
    type: Mapped[PostType] = mapped_column(Enum(PostType, name="post_type"), nullable=False)
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status"),
        nullable=False,
        default=PostStatus.DRAFT,
    )
    title: Mapped[str | None] = mapped_column(String(500))
    caption: Mapped[str | None] = mapped_column(Text)
    hashtags: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=list)
    cta: Mapped[str | None] = mapped_column(String(500))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_post_id: Mapped[str | None] = mapped_column(String(255))
    permalink: Mapped[str | None] = mapped_column(String(500))
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_config: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    company: Mapped["Company"] = relationship(back_populates="posts")
    social_account: Mapped["SocialAccount | None"] = relationship(back_populates="posts")
    post_assets: Mapped[list["PostAsset"]] = relationship(back_populates="post")
    metrics: Mapped[list["PostMetrics"]] = relationship(back_populates="post")
    comments: Mapped[list["Comment"]] = relationship(back_populates="post")
    ai_history: Mapped[list["AIHistory"]] = relationship(back_populates="post")
    scheduler_jobs: Mapped[list["SchedulerJob"]] = relationship(back_populates="post")


class PostAsset(Base):
    __tablename__ = "post_assets"

    post_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    asset_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        primary_key=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    post: Mapped["Post"] = relationship(back_populates="post_assets")
    asset: Mapped["Asset"] = relationship(back_populates="post_assets")


class PostMetrics(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "post_metrics"

    post_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    reach: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float | None] = mapped_column()
    ctr: Mapped[float | None] = mapped_column()
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    post: Mapped["Post"] = relationship(back_populates="metrics")
