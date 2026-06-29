import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ai import AIHistory
from app.models.comment import Comment
from app.models.enums import CommentStatus, PostStatus
from app.models.organization import Organization, OrganizationMember
from app.models.post import Post, PostMetrics
from app.models.social import SocialAccount
from app.models.user import User
from app.schemas.domain import DashboardResponse, PostResponse
from app.services.post_service import _post_to_response


async def get_dashboard(db: AsyncSession, user: User) -> DashboardResponse:
    org_ids = list((await db.scalars(select(OrganizationMember.organization_id).where(OrganizationMember.user_id == user.id))).all())
    if not org_ids:
        return DashboardResponse(
            scheduled_posts=0, published_posts=0, failed_posts=0, pending_comments=0,
            total_engagement=0, total_reach=0, ai_calls=0, ai_cost=0, credits_balance=0,
            followers=0, upcoming_posts=[],
        )

    from app.models.company import Company
    company_ids = list((await db.scalars(select(Company.id).where(Company.organization_id.in_(org_ids)))).all())

    scheduled = await db.scalar(select(func.count()).select_from(Post).where(Post.company_id.in_(company_ids), Post.status == PostStatus.SCHEDULED)) or 0
    published = await db.scalar(select(func.count()).select_from(Post).where(Post.company_id.in_(company_ids), Post.status == PostStatus.PUBLISHED)) or 0
    failed = await db.scalar(select(func.count()).select_from(Post).where(Post.company_id.in_(company_ids), Post.status == PostStatus.FAILED)) or 0

    pending_comments = await db.scalar(
        select(func.count()).select_from(Comment).join(Post).where(Post.company_id.in_(company_ids), Comment.status == CommentStatus.PENDING)
    ) or 0

    metrics = await db.execute(
        select(func.sum(PostMetrics.likes + PostMetrics.comments + PostMetrics.shares), func.sum(PostMetrics.reach))
        .join(Post).where(Post.company_id.in_(company_ids))
    )
    row = metrics.one()
    total_engagement = int(row[0] or 0)
    total_reach = int(row[1] or 0)

    ai_stats = await db.execute(
        select(func.count(), func.sum(AIHistory.cost)).where(AIHistory.company_id.in_(company_ids))
    )
    ai_row = ai_stats.one()
    ai_calls = int(ai_row[0] or 0)
    ai_cost = float(ai_row[1] or 0)

    credits = await db.scalar(select(func.sum(Organization.credits_balance)).where(Organization.id.in_(org_ids))) or 0

    followers = 0
    accounts = await db.scalars(select(SocialAccount).where(SocialAccount.company_id.in_(company_ids), SocialAccount.is_connected == True))
    for acc in accounts:
        if acc.metadata_ and acc.metadata_.get("followers_count"):
            followers += acc.metadata_["followers_count"]

    upcoming = await db.scalars(
        select(Post).where(Post.company_id.in_(company_ids), Post.status == PostStatus.SCHEDULED)
        .order_by(Post.scheduled_at.asc()).limit(5)
    )
    upcoming_list = [_post_to_response(p) for p in upcoming.all()]

    return DashboardResponse(
        scheduled_posts=scheduled, published_posts=published, failed_posts=failed,
        pending_comments=pending_comments, total_engagement=total_engagement, total_reach=total_reach,
        ai_calls=ai_calls, ai_cost=ai_cost, credits_balance=int(credits), followers=followers,
        upcoming_posts=upcoming_list,
    )


async def get_metrics_summary(db: AsyncSession, user: User, company_id: uuid.UUID | None = None) -> dict:
    from app.services.company_service import list_companies, get_company
    if company_id:
        await get_company(db, user, company_id)
        cids = [company_id]
    else:
        cids = [c.id for c in await list_companies(db, user)]

    posts = await db.scalars(
        select(Post).where(Post.company_id.in_(cids), Post.status == PostStatus.PUBLISHED)
        .options(selectinload(Post.metrics))
    )
    data = []
    for p in posts:
        m = p.metrics[-1] if p.metrics else None
        data.append({
            "post_id": str(p.id), "title": p.title, "published_at": p.published_at,
            "likes": m.likes if m else 0, "comments": m.comments if m else 0,
            "reach": m.reach if m else 0, "impressions": m.impressions if m else 0,
            "engagement_rate": float(m.engagement_rate or 0) if m else 0,
        })
    return {"posts": data, "totals": {
        "likes": sum(d["likes"] for d in data),
        "comments": sum(d["comments"] for d in data),
        "reach": sum(d["reach"] for d in data),
    }}
