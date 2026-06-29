import asyncio
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.logging import LogCategory, log_event
from app.models.enums import PostStatus, SchedulerJobStatus
from app.models.post import Post, PostAsset
from app.models.scheduler import SchedulerJob
from app.models.social import SocialAccount, Token
from app.services.post_service import publish_post_now


async def _process_due_posts() -> dict:
    now = datetime.now(UTC)
    processed = 0
    failed = 0

    async with AsyncSessionLocal() as db:
        due_jobs = await db.scalars(
            select(SchedulerJob)
            .where(SchedulerJob.status == SchedulerJobStatus.PENDING, SchedulerJob.scheduled_for <= now)
            .limit(20)
        )
        for job in due_jobs.all():
            job.status = SchedulerJobStatus.RUNNING
            job.started_at = now
            await db.flush()
            try:
                post = await db.scalar(
                    select(Post).where(Post.id == job.post_id).options(selectinload(Post.post_assets))
                )
                if not post:
                    job.status = SchedulerJobStatus.FAILED
                    job.error = "Post not found"
                    failed += 1
                    continue

                if post.social_account_id:
                    account = await db.scalar(select(SocialAccount).where(SocialAccount.id == post.social_account_id))
                    token_row = await db.scalar(select(Token).where(Token.social_account_id == account.id)) if account else None
                    if token_row and token_row.expires_at and token_row.expires_at <= now:
                        from app.services.social_service import refresh_instagram_token
                        await refresh_instagram_token(db, account.id)

                await publish_post_now(db, post.id)
                job.status = SchedulerJobStatus.COMPLETED
                job.completed_at = datetime.now(UTC)
                processed += 1
            except Exception as exc:
                job.status = SchedulerJobStatus.FAILED
                job.error = str(exc)[:500]
                job.completed_at = datetime.now(UTC)
                failed += 1
                post = await db.scalar(select(Post).where(Post.id == job.post_id))
                if post and post.status == PostStatus.FAILED and post.retry_count < 3:
                    post.status = PostStatus.SCHEDULED
                    post.retry_count += 1
                    retry_job = SchedulerJob(
                        post_id=post.id,
                        scheduled_for=datetime.now(UTC),
                        status=SchedulerJobStatus.PENDING,
                    )
                    db.add(retry_job)
            await db.flush()
        await db.commit()

    await log_event(LogCategory.SCHEDULER, "process_scheduled_posts", metadata={"processed": processed, "failed": failed})
    return {"processed": processed, "failed": failed}


@celery_app.task(name="app.tasks.scheduler.process_scheduled_posts", bind=True, max_retries=3)
def process_scheduled_posts(self):
    return asyncio.run(_process_due_posts())


@celery_app.task(name="app.tasks.scheduler.retry_failed_post", bind=True, max_retries=5)
def retry_failed_post(self, post_id: str):
    async def _retry():
        async with AsyncSessionLocal() as db:
            try:
                await publish_post_now(db, __import__("uuid").UUID(post_id))
                await db.commit()
                return {"post_id": post_id, "status": "published"}
            except Exception as exc:
                await db.rollback()
                return {"post_id": post_id, "status": "failed", "error": str(exc)}

    return asyncio.run(_retry())
