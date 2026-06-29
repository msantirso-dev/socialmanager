"""Database seed — demo org, admin user, sample company."""

import asyncio
import uuid

from passlib.context import CryptContext
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.ai import AIConfig
from app.models.company import Company
from app.models.enums import OrganizationPlan, UserRole
from app.models.organization import Organization, OrganizationMember
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123!"
ORG_SLUG = "demo"


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(User).where(User.email == ADMIN_EMAIL))
        if existing:
            print(f"Seed skipped: user {ADMIN_EMAIL} already exists.")
            return

        org = Organization(
            id=uuid.uuid4(),
            name="Demo Organization",
            slug=ORG_SLUG,
            plan=OrganizationPlan.FREE,
            credits_balance=500,
        )
        session.add(org)

        user = User(
            id=uuid.uuid4(),
            email=ADMIN_EMAIL,
            password_hash=pwd_context.hash(ADMIN_PASSWORD),
            full_name="Administrador",
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(user)

        membership = OrganizationMember(
            id=uuid.uuid4(),
            organization_id=org.id,
            user_id=user.id,
            role=UserRole.ADMIN,
        )
        session.add(membership)

        company = Company(
            id=uuid.uuid4(),
            organization_id=org.id,
            name="Empresa Demo",
            website="https://example.com",
            brand_description="Empresa de demostración para Social AI Manager",
            tone="professional",
            language="es",
            colors={"primary": "#7c3aed", "secondary": "#1e1b4b", "accent": "#f59e0b"},
            target_audience="Profesionales y empresas B2B",
            location="Madrid, ES",
            custom_hashtags=["#SocialAI", "#Demo"],
            forbidden_words=["spam", "gratis total"],
        )
        session.add(company)

        ai_config = AIConfig(
            id=uuid.uuid4(),
            company_id=company.id,
            text_provider="anthropic",
            text_model="claude-3-5-sonnet-20241022",
            image_provider="openai",
            image_model="dall-e-3",
            hashtag_provider="google",
            ideas_provider="openai",
        )
        session.add(ai_config)

        await session.commit()
        print("Seed complete:")
        print(f"  Organization: {org.name} ({org.slug})")
        print(f"  Admin user:   {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"  Company:      {company.name}")


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
