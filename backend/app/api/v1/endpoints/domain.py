from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.enums import CommentStatus, PostStatus, UserRole
from app.models.user import User
from app.schemas.domain import (
    CommentReplyRequest,
    CommentResponse,
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    DashboardResponse,
    GenerateContentRequest,
    GenerateImageRequest,
    PostCreate,
    PostResponse,
    PostUpdate,
    SocialAccountResponse,
)
from app.services.ai_service import generate_content, generate_image
from app.services.comment_service import list_comments, reply_comment, sync_comments_from_instagram
from app.services.company_service import create_company, delete_company, get_company, list_companies, update_company
from app.services.dashboard_service import get_dashboard, get_metrics_summary
from app.services.post_service import create_post, list_posts, publish_post_now, update_post
from app.services.social_service import (
    disconnect_instagram,
    get_instagram_connect_url,
    handle_instagram_callback,
    list_social_accounts,
    refresh_instagram_token,
)

router = APIRouter()


def _err(exc: Exception):
    raise HTTPException(400, detail=str(exc)) from exc


# --- Companies ---
@router.get("/companies", response_model=list[CompanyResponse])
async def companies_list(user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    return await list_companies(db, user)


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def companies_get(company_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await get_company(db, user, company_id)
    except ValueError as e:
        _err(e)


@router.post("/companies", response_model=CompanyResponse)
async def companies_create(
    data: CompanyCreate,
    user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
    org_id: UUID | None = Query(None),
):
    try:
        return await create_company(db, user, data, org_id)
    except ValueError as e:
        _err(e)


@router.delete("/companies/{company_id}")
async def companies_delete(
    company_id: UUID,
    user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        await delete_company(db, user, company_id)
        return {"message": "Company deleted"}
    except ValueError as e:
        _err(e)


@router.patch("/companies/{company_id}", response_model=CompanyResponse)
async def companies_update(company_id: UUID, data: CompanyUpdate, user: Annotated[User, Depends(require_role(UserRole.EDITOR))], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await update_company(db, user, company_id, data)
    except ValueError as e:
        _err(e)


# --- Instagram ---
@router.get("/social/instagram/connect")
async def instagram_connect(company_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        url = await get_instagram_connect_url(db, user, company_id)
        return {"oauth_url": url}
    except ValueError as e:
        _err(e)


@router.get("/social/instagram/callback")
async def instagram_callback(code: str, state: str, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        await handle_instagram_callback(db, code, state)
        return RedirectResponse(f"{settings.frontend_url}/social?connected=true")
    except Exception as e:
        return RedirectResponse(f"{settings.frontend_url}/social?error={str(e)[:100]}")


@router.get("/social/accounts", response_model=list[SocialAccountResponse])
async def social_accounts(company_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await list_social_accounts(db, user, company_id)
    except ValueError as e:
        _err(e)


@router.delete("/social/accounts/{account_id}")
async def social_disconnect(account_id: UUID, user: Annotated[User, Depends(require_role(UserRole.ADMIN))], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        await disconnect_instagram(db, user, account_id)
        return {"message": "Disconnected"}
    except ValueError as e:
        _err(e)


@router.post("/social/accounts/{account_id}/refresh")
async def social_refresh(account_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        await refresh_instagram_token(db, account_id)
        return {"message": "Token refreshed"}
    except ValueError as e:
        _err(e)


# --- Posts ---
@router.get("/posts", response_model=list[PostResponse])
async def posts_list(user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)], company_id: UUID | None = None, status: PostStatus | None = None):
    return await list_posts(db, user, company_id, status)


@router.post("/posts", response_model=PostResponse)
async def posts_create(data: PostCreate, user: Annotated[User, Depends(require_role(UserRole.EDITOR))], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await create_post(db, user, data)
    except ValueError as e:
        _err(e)


@router.patch("/posts/{post_id}", response_model=PostResponse)
async def posts_update(post_id: UUID, data: PostUpdate, user: Annotated[User, Depends(require_role(UserRole.EDITOR))], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await update_post(db, user, post_id, data)
    except ValueError as e:
        _err(e)


@router.post("/posts/{post_id}/publish", response_model=PostResponse)
async def posts_publish(post_id: UUID, user: Annotated[User, Depends(require_role(UserRole.OPERATOR))], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await publish_post_now(db, post_id)
    except ValueError as e:
        _err(e)


# --- AI ---
@router.post("/ai/generate/content")
async def ai_generate_content(data: GenerateContentRequest, user: Annotated[User, Depends(require_role(UserRole.EDITOR))], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await generate_content(db, user, data)
    except Exception as e:
        _err(e)


@router.post("/ai/generate/image")
async def ai_generate_image(data: GenerateImageRequest, user: Annotated[User, Depends(require_role(UserRole.EDITOR))], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await generate_image(db, user, data)
    except Exception as e:
        _err(e)


# --- Dashboard & Metrics ---
@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_dashboard(db, user)


@router.get("/metrics")
async def metrics(user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)], company_id: UUID | None = None):
    return await get_metrics_summary(db, user, company_id)


# --- Comments ---
@router.get("/comments", response_model=list[CommentResponse])
async def comments_list(user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)], company_id: UUID | None = None, status: CommentStatus | None = None):
    return await list_comments(db, user, company_id, status)


@router.post("/comments/{comment_id}/reply", response_model=CommentResponse)
async def comments_reply(comment_id: UUID, data: CommentReplyRequest, user: Annotated[User, Depends(require_role(UserRole.OPERATOR))], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await reply_comment(db, user, comment_id, data.message, data.use_ai)
    except ValueError as e:
        _err(e)


@router.post("/comments/sync/{post_id}")
async def comments_sync(post_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        count = await sync_comments_from_instagram(db, user, post_id)
        return {"synced": count}
    except ValueError as e:
        _err(e)
