"""Import all models so Alembic and SQLAlchemy metadata are complete."""

from app.models.ai import AIConfig, AIHistory, Prompt
from app.models.asset import Asset
from app.models.comment import Comment
from app.models.company import Company
from app.models.log import Log
from app.models.organization import Organization, OrganizationMember
from app.models.post import Post, PostAsset, PostMetrics
from app.models.scheduler import SchedulerJob
from app.models.social import SocialAccount, Token
from app.models.user import User

__all__ = [
    "User",
    "Organization",
    "OrganizationMember",
    "Company",
    "SocialAccount",
    "Token",
    "Post",
    "PostAsset",
    "PostMetrics",
    "Asset",
    "Comment",
    "Prompt",
    "AIHistory",
    "AIConfig",
    "SchedulerJob",
    "Log",
]
