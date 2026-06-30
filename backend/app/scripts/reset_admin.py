"""Reset demo admin password — run: python -m app.scripts.reset_admin"""

import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123!"


async def reset_admin() -> None:
    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == ADMIN_EMAIL))
        if not user:
            print(f"User {ADMIN_EMAIL} not found. Run seed first.")
            return
        user.password_hash = hash_password(ADMIN_PASSWORD)
        await session.commit()
        print(f"Password reset for {ADMIN_EMAIL}")


if __name__ == "__main__":
    asyncio.run(reset_admin())
