import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import LogCategory, log_event
from app.models.asset import Asset
from app.models.enums import AssetType, PostStatus, PostType, SchedulerJobStatus
from app.models.post import Post, PostAsset
from app.models.scheduler import SchedulerJob
from app.models.social import SocialAccount
from app.providers.social.instagram import InstagramProvider
from app.schemas.domain import PostCreate, PostResponse, PostUpdate
from app.services.company_service import get_company
from app.services.social_service import get_decrypted_token
from app.models.user import User


def _post_to_response(post: Post, media_urls: list[str] | None = None) -> PostResponse:
    return PostResponse(
        id=post.id,
        company_id=post.company_id,
        social_account_id=post.social_account_id,
        type=post.type,
        status=post.status,
        title=post.title,
        caption=post.caption,
        hashtags=post.hashtags,
        cta=post.cta,
        scheduled_at=post.scheduled_at,
        published_at=post.published_at,
        external_post_id=post.external_post_id,
        permalink=post.permalink,
        error_message=post.error_message,
        media_urls=media_urls or [],
    )


async def list_posts(
    db: AsyncSession, user: User, company_id: uuid.UUID | None = None, status: PostStatus | None = None
) -> list[PostResponse]:
    q = select(Post).options(selectinload(Post.post_assets).selectinload(PostAsset.asset))
    if company_id:
        await get_company(db, user, company_id)
        q = q.where(Post.company_id == company_id)
    else:
        from app.services.company_service import list_companies
        companies = await list_companies(db, user)
        q = q.where(Post.company_id.in_([c.id for c in companies]))
    if status:
        q = q.where(Post.status == status)
    q = q.order_by(Post.scheduled_at.desc().nullslast(), Post.created_at.desc())
    posts = list((await db.scalars(q)).all())
    result = []
    for p in posts:
        urls = [pa.asset.url for pa in sorted(p.post_assets, key=lambda x: x.sort_order) if pa.asset]
        result.append(_post_to_response(p, urls))
    return result


async def create_post(db: AsyncSession, user: User, data: PostCreate) -> PostResponse:
    await get_company(db, user, data.company_id)
    status = PostStatus.SCHEDULED if data.scheduled_at else PostStatus.DRAFT
    post = Post(
        company_id=data.company_id,
        social_account_id=data.social_account_id,
        type=data.type,
        status=status,
        title=data.title,
        caption=data.caption,
        hashtags=data.hashtags,
        cta=data.cta,
        scheduled_at=data.scheduled_at,
        ai_config=data.ai_config,
    )
    db.add(post)
    await db.flush()
    for i, url in enumerate(data.media_urls):
        asset = Asset(company_id=data.company_id, type=AssetType.IMAGE, url=url)
        db.add(asset)
        await db.flush()
        db.add(PostAsset(post_id=post.id, asset_id=asset.id, sort_order=i))
    if data.scheduled_at:
        db.add(SchedulerJob(post_id=post.id, scheduled_for=data.scheduled_at, status=SchedulerJobStatus.PENDING))
    await db.flush()
    return _post_to_response(post, data.media_urls)


async def update_post(db: AsyncSession, user: User, post_id: uuid.UUID, data: PostUpdate) -> PostResponse:
    post = await db.scalar(select(Post).where(Post.id == post_id).options(selectinload(Post.post_assets)))
    if not post:
        raise ValueError("Post not found")
    await get_company(db, user, post.company_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "media_urls":
            continue
        setattr(post, k, v)
    if data.media_urls is not None:
        for pa in list(post.post_assets):
            await db.delete(pa)
        for i, url in enumerate(data.media_urls):
            asset = Asset(company_id=post.company_id, type=AssetType.IMAGE, url=url)
            db.add(asset)
            await db.flush()
            db.add(PostAsset(post_id=post.id, asset_id=asset.id, sort_order=i))
    await db.flush()
    urls = data.media_urls or []
    return _post_to_response(post, urls)


async def publish_post_now(db: AsyncSession, post_id: uuid.UUID) -> PostResponse:
    post = await db.scalar(
        select(Post).where(Post.id == post_id).options(selectinload(Post.post_assets).selectinload(PostAsset.asset))
    )
    if not post or not post.social_account_id:
        raise ValueError("Post or social account missing")
    account = await db.scalar(select(SocialAccount).where(SocialAccount.id == post.social_account_id))
    if not account or not account.is_connected:
        raise ValueError("Social account not connected")
    token = await get_decrypted_token(db, account)
    provider = InstagramProvider()
    caption = post.caption or ""
    if post.hashtags:
        caption += "\n\n" + " ".join(post.hashtags)
    urls = [pa.asset.url for pa in sorted(post.post_assets, key=lambda x: x.sort_order) if pa.asset]
    post.status = PostStatus.PUBLISHING
    await db.flush()

    if post.type == PostType.CAROUSEL and len(urls) > 1:
        result = await provider.publish_carousel(token, account.external_account_id, urls, caption)
    elif post.type == PostType.REEL and urls:
        result = await provider.publish_reel(token, account.external_account_id, urls[0], caption)
    elif urls:
        result = await provider.publish_image(token, account.external_account_id, urls[0], caption)
    else:
        post.status = PostStatus.FAILED
        post.error_message = "No media URLs attached"
        await db.flush()
        raise ValueError("No media URLs attached")

    if result.success:
        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.now(UTC)
        post.external_post_id = result.external_id
        post.permalink = result.permalink
        post.error_message = None
    else:
        post.status = PostStatus.FAILED
        post.error_message = result.error
        post.retry_count += 1
    await db.flush()
    await log_event(LogCategory.SOCIAL, "publish", company_id=str(post.company_id), metadata={"post_id": str(post.id), "success": result.success})
    return _post_to_response(post, urls)
