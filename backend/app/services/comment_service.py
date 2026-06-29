import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.models.enums import CommentStatus
from app.models.post import Post
from app.models.user import User
from app.providers.ai.base import AIProviderType
from app.providers.ai.registry import AIProviderRegistry
from app.providers.social.instagram import InstagramProvider
from app.schemas.domain import CommentResponse
from app.services.company_service import get_company
from app.services.social_service import get_decrypted_token


async def list_comments(db: AsyncSession, user: User, company_id: uuid.UUID | None = None, status: CommentStatus | None = None) -> list[CommentResponse]:
    from app.services.company_service import list_companies
    cids = [company_id] if company_id else [c.id for c in await list_companies(db, user)]
    if company_id:
        await get_company(db, user, company_id)
    q = select(Comment).join(Post).where(Post.company_id.in_(cids))
    if status:
        q = q.where(Comment.status == status)
    q = q.order_by(Comment.created_at.desc())
    comments = (await db.scalars(q)).all()
    return [CommentResponse.model_validate(c) for c in comments]


async def sync_comments_from_instagram(db: AsyncSession, user: User, post_id: uuid.UUID) -> int:
    post = await db.scalar(select(Post).where(Post.id == post_id))
    if not post or not post.external_post_id or not post.social_account_id:
        raise ValueError("Post not published on Instagram")
    await get_company(db, user, post.company_id)
    from app.models.social import SocialAccount
    account = await db.scalar(select(SocialAccount).where(SocialAccount.id == post.social_account_id))
    token = await get_decrypted_token(db, account)
    provider = InstagramProvider()
    ig_comments = await provider.get_comments(token, post.external_post_id)
    count = 0
    for ic in ig_comments:
        existing = await db.scalar(select(Comment).where(Comment.external_comment_id == ic["id"]))
        if not existing:
            db.add(Comment(
                post_id=post.id, external_comment_id=ic["id"],
                author_username=ic.get("username") or ic.get("from", {}).get("username"),
                text=ic.get("text", ""), status=CommentStatus.PENDING,
            ))
            count += 1
    await db.flush()
    return count


async def reply_comment(db: AsyncSession, user: User, comment_id: uuid.UUID, message: str, use_ai: bool = False) -> CommentResponse:
    comment = await db.scalar(select(Comment).where(Comment.id == comment_id).options(selectinload(Comment.post)))
    if not comment:
        raise ValueError("Comment not found")
    post = comment.post
    await get_company(db, user, post.company_id)

    if use_ai and not message:
        provider = AIProviderRegistry.get(AIProviderType.ANTHROPIC)
        resp = await provider.generate_text(
            f"Genera una respuesta profesional y amable a este comentario de Instagram: '{comment.text}'",
            system_prompt="Respuesta corta (max 200 chars), en español, tono de marca profesional.",
            max_tokens=150,
        )
        message = str(resp.content)

    if post.external_post_id and comment.external_comment_id:
        from app.models.social import SocialAccount
        account = await db.scalar(select(SocialAccount).where(SocialAccount.id == post.social_account_id))
        token = await get_decrypted_token(db, account)
        provider = InstagramProvider()
        await provider.reply_comment(token, comment.external_comment_id, message)

    comment.reply_text = message
    comment.replied_at = datetime.now(UTC)
    comment.status = CommentStatus.REPLIED
    comment.ai_replied = use_ai
    await db.flush()
    return CommentResponse.model_validate(comment)
