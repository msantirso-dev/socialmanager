import uuid
from datetime import UTC, datetime, timedelta

from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decrypt_token, encrypt_token
from app.models.company import Company
from app.models.enums import SocialNetwork
from app.models.organization import Organization, OrganizationMember
from app.models.social import SocialAccount, Token
from app.models.user import User
from app.providers.social.instagram import InstagramProvider
from app.providers.social.registry import SocialProviderRegistry


def _oauth_state(company_id: uuid.UUID, user_id: uuid.UUID) -> str:
    payload = {
        "company_id": str(company_id),
        "user_id": str(user_id),
        "exp": datetime.now(UTC) + timedelta(minutes=15),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _parse_oauth_state(state: str) -> tuple[uuid.UUID, uuid.UUID]:
    payload = jwt.decode(state, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return uuid.UUID(payload["company_id"]), uuid.UUID(payload["user_id"])


async def _verify_company_access(db: AsyncSession, user: User, company_id: uuid.UUID) -> Company:
    company = await db.scalar(select(Company).where(Company.id == company_id))
    if not company:
        raise ValueError("Company not found")
    member = await db.scalar(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == company.organization_id,
            OrganizationMember.user_id == user.id,
        )
    )
    if not member:
        raise ValueError("Access denied")
    return company


async def get_instagram_connect_url(db: AsyncSession, user: User, company_id: uuid.UUID) -> str:
    await _verify_company_access(db, user, company_id)
    provider = InstagramProvider()
    state = _oauth_state(company_id, user.id)
    return provider.get_oauth_url(state)


async def handle_instagram_callback(db: AsyncSession, code: str, state: str) -> SocialAccount:
    company_id, user_id = _parse_oauth_state(state)
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise ValueError("Invalid state")
    await _verify_company_access(db, user, company_id)

    provider = InstagramProvider()
    token_data = await provider.handle_oauth_callback(code)
    access_token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 5184000)

    account_info = await provider.get_account_info(access_token)
    page_token = account_info.metadata.get("page_token", access_token)

    existing = await db.scalar(
        select(SocialAccount).where(
            SocialAccount.company_id == company_id,
            SocialAccount.network == SocialNetwork.INSTAGRAM,
        )
    )
    if existing:
        account = existing
    else:
        account = SocialAccount(company_id=company_id, network=SocialNetwork.INSTAGRAM)
        db.add(account)

    account.external_account_id = account_info.account_id
    account.username = account_info.username
    account.display_name = account_info.display_name
    account.profile_picture_url = account_info.profile_picture_url
    account.is_connected = True
    account.connected_at = datetime.now(UTC)
    account.metadata_ = {
        "page_id": account_info.metadata.get("page_id"),
        "followers_count": account_info.followers_count,
    }
    await db.flush()

    token_row = await db.scalar(select(Token).where(Token.social_account_id == account.id))
    if not token_row:
        token_row = Token(social_account_id=account.id)
        db.add(token_row)

    token_row.access_token_encrypted = encrypt_token(page_token)
    token_row.refresh_token_encrypted = encrypt_token(access_token)
    token_row.expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
    token_row.last_refreshed_at = datetime.now(UTC)
    await db.flush()
    return account


async def get_decrypted_token(db: AsyncSession, account: SocialAccount) -> str:
    token_row = await db.scalar(select(Token).where(Token.social_account_id == account.id))
    if not token_row:
        raise ValueError("No token stored")
    return decrypt_token(token_row.access_token_encrypted)


async def disconnect_instagram(db: AsyncSession, user: User, account_id: uuid.UUID) -> None:
    account = await db.scalar(select(SocialAccount).where(SocialAccount.id == account_id))
    if not account:
        raise ValueError("Account not found")
    await _verify_company_access(db, user, account.company_id)
    account.is_connected = False
    tokens = await db.scalars(select(Token).where(Token.social_account_id == account.id))
    for t in tokens:
        await db.delete(t)


async def list_social_accounts(db: AsyncSession, user: User, company_id: uuid.UUID) -> list[SocialAccount]:
    await _verify_company_access(db, user, company_id)
    result = await db.scalars(select(SocialAccount).where(SocialAccount.company_id == company_id))
    return list(result.all())


async def refresh_instagram_token(db: AsyncSession, account_id: uuid.UUID) -> None:
    account = await db.scalar(select(SocialAccount).where(SocialAccount.id == account_id))
    if not account or not account.is_connected:
        raise ValueError("Account not connected")
    token_row = await db.scalar(select(Token).where(Token.social_account_id == account.id))
    if not token_row or not token_row.refresh_token_encrypted:
        raise ValueError("No refresh token")
    provider = InstagramProvider()
    refresh = decrypt_token(token_row.refresh_token_encrypted)
    new_data = await provider.refresh_token(refresh)
    token_row.access_token_encrypted = encrypt_token(new_data["access_token"])
    token_row.last_refreshed_at = datetime.now(UTC)
    if "expires_in" in new_data:
        token_row.expires_at = datetime.now(UTC) + timedelta(seconds=new_data["expires_in"])
