from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.logging import LogCategory, log_event
from app.core.redis import get_redis
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthError, get_user_profile, login_user, refresh_tokens, register_user

router = APIRouter()


@router.post("/register", response_model=dict)
async def register(data: RegisterRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        user, tokens = await register_user(db, data)
    except AuthError as exc:
        raise HTTPException(exc.status_code, detail=exc.message) from exc
    return {"user": user, **tokens.model_dump()}


@router.post("/login", response_model=dict)
async def login(data: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        user, tokens = await login_user(db, data.email, data.password)
    except AuthError as exc:
        raise HTTPException(exc.status_code, detail=exc.message) from exc
    return {"user": user, **tokens.model_dump()}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await refresh_tokens(db, data.refresh_token)
    except AuthError as exc:
        raise HTTPException(exc.status_code, detail=exc.message) from exc


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await get_user_profile(db, current_user.id)


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    authorization: Annotated[str | None, Header()] = None,
):
    """Revoca el access token actual (blacklist en Redis hasta su expiración)."""
    import time

    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        try:
            payload = decode_token(token)
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                redis = await get_redis()
                ttl = max(int(exp - time.time()), 1)
                await redis.setex(f"token:blacklist:{jti}", ttl, "1")
        except Exception:
            pass

    await log_event(LogCategory.AUTH, "logout", user_id=str(current_user.id))
    return {"message": "Logged out successfully"}
