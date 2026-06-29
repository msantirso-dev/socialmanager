import uuid

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.logging import LogCategory, log_event
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    slugify,
    validate_token,
    verify_password,
)
from app.models.enums import OrganizationPlan, UserRole
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.schemas.auth import OrganizationSummary, RegisterRequest, TokenResponse, UserResponse


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def _unique_slug(db: AsyncSession, base: str) -> str:
    slug = slugify(base)
    candidate = slug
    counter = 1
    while await db.scalar(select(Organization.id).where(Organization.slug == candidate)):
        candidate = f"{slug}-{counter}"
        counter += 1
    return candidate


def _user_response(user: User) -> UserResponse:
    orgs = [
        OrganizationSummary(
            id=m.organization.id,
            name=m.organization.name,
            slug=m.organization.slug,
            role=m.role,
        )
        for m in user.memberships
        if m.organization
    ]
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        organizations=orgs,
    )


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id, user.email, user.role),
        refresh_token=create_refresh_token(user.id),
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


async def register_user(db: AsyncSession, data: RegisterRequest) -> tuple[UserResponse, TokenResponse]:
    existing = await db.scalar(select(User.id).where(User.email == data.email.lower()))
    if existing:
        raise AuthError("Email already registered", 409)

    org = Organization(
        name=data.organization_name,
        slug=await _unique_slug(db, data.organization_name),
        plan=OrganizationPlan.FREE,
        credits_balance=100,
    )
    db.add(org)
    await db.flush()

    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    membership = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role=UserRole.ADMIN,
    )
    db.add(membership)
    await db.flush()

    await db.refresh(user, ["memberships"])
    for m in user.memberships:
        await db.refresh(m, ["organization"])

    await log_event(LogCategory.AUTH, "register", user_id=str(user.id), metadata={"email": user.email})

    return _user_response(user), _token_response(user)


async def login_user(db: AsyncSession, email: str, password: str) -> tuple[UserResponse, TokenResponse]:
    user = await db.scalar(
        select(User)
        .where(User.email == email.lower())
        .options(selectinload(User.memberships).selectinload(OrganizationMember.organization))
    )
    if not user or not verify_password(password, user.password_hash):
        raise AuthError("Invalid email or password", 401)

    if not user.is_active:
        raise AuthError("Account is disabled", 403)

    await log_event(LogCategory.AUTH, "login", user_id=str(user.id))

    return _user_response(user), _token_response(user)


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenResponse:
    from app.core.security import TokenValidationError

    try:
        payload = validate_token(refresh_token, "refresh")
    except TokenValidationError as exc:
        raise AuthError("Invalid refresh token", 401) from exc

    user_id = uuid.UUID(payload["sub"])
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user or not user.is_active:
        raise AuthError("User not found or inactive", 401)

    return _token_response(user)


async def get_user_profile(db: AsyncSession, user_id: uuid.UUID) -> UserResponse:
    user = await db.scalar(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.memberships).selectinload(OrganizationMember.organization))
    )
    if not user:
        raise AuthError("User not found", 404)
    return _user_response(user)
