import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai import AIConfig
from app.models.company import Company
from app.models.organization import OrganizationMember
from app.models.user import User
from app.schemas.domain import CompanyCreate, CompanyUpdate


async def _verify_org_access(db: AsyncSession, user: User, organization_id: uuid.UUID) -> None:
    member = await db.scalar(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user.id,
        )
    )
    if not member:
        raise ValueError("Access denied")


async def _default_org_id(db: AsyncSession, user: User) -> uuid.UUID:
    org_id = await db.scalar(
        select(OrganizationMember.organization_id).where(OrganizationMember.user_id == user.id).limit(1)
    )
    if not org_id:
        raise ValueError("No organization membership")
    return org_id


async def list_companies(db: AsyncSession, user: User) -> list[Company]:
    org_ids = await db.scalars(
        select(OrganizationMember.organization_id).where(OrganizationMember.user_id == user.id)
    )
    result = await db.scalars(select(Company).where(Company.organization_id.in_(list(org_ids.all()))))
    return list(result.all())


async def get_company(db: AsyncSession, user: User, company_id: uuid.UUID) -> Company:
    company = await db.scalar(select(Company).where(Company.id == company_id))
    if not company:
        raise ValueError("Company not found")
    await _verify_org_access(db, user, company.organization_id)
    return company


async def create_company(
    db: AsyncSession, user: User, data: CompanyCreate, org_id: uuid.UUID | None = None
) -> Company:
    resolved_org = org_id or await _default_org_id(db, user)
    await _verify_org_access(db, user, resolved_org)
    company = Company(organization_id=resolved_org, **data.model_dump())
    db.add(company)
    await db.flush()
    db.add(AIConfig(company_id=company.id, text_provider="anthropic", image_provider="openai"))
    await db.flush()
    return company


async def update_company(db: AsyncSession, user: User, company_id: uuid.UUID, data: CompanyUpdate) -> Company:
    company = await get_company(db, user, company_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(company, k, v)
    await db.flush()
    return company


async def delete_company(db: AsyncSession, user: User, company_id: uuid.UUID) -> None:
    company = await get_company(db, user, company_id)
    await db.delete(company)
    await db.flush()
