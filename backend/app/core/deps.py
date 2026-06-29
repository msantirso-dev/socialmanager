import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import TokenValidationError, has_min_role, validate_token
from app.models.enums import UserRole
from app.models.organization import OrganizationMember
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


async def _is_token_blacklisted(jti: str | None) -> bool:
    if not jti:
        return False
    redis = await get_redis()
    return bool(await redis.exists(f"token:blacklist:{jti}"))


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = validate_token(credentials.credentials, "access")
    except TokenValidationError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from None

    if await _is_token_blacklisted(payload.get("jti")):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    user_id = uuid.UUID(payload["sub"])
    user = await db.scalar(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.memberships).selectinload(OrganizationMember.organization))
    )
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


def require_role(min_role: UserRole):
    async def checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if not has_min_role(user.role, min_role):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"Requires {min_role.value} role or higher",
            )
        return user

    return checker
