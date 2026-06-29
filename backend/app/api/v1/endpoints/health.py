from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "social-ai-manager-api"}


@router.get("/health/ready")
async def readiness_check():
    """Readiness probe — verifies DB, Redis and schema migrations (Coolify health check)."""
    checks: dict = {"database": False, "redis": False, "migrations": False}

    try:
        from sqlalchemy import text

        from app.core.database import engine

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            checks["database"] = True

            version = await conn.scalar(
                text("SELECT version_num FROM alembic_version LIMIT 1")
            )
            checks["migrations"] = version is not None
            checks["alembic_version"] = version

            table_count = await conn.scalar(
                text(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
                )
            )
            checks["database_tables"] = table_count
    except Exception as exc:
        checks["database_error"] = str(exc)

    try:
        from app.core.redis import get_redis

        redis = await get_redis()
        await redis.ping()
        checks["redis"] = True
    except Exception as exc:
        checks["redis_error"] = str(exc)

    all_ok = all(checks.get(k) for k in ("database", "redis", "migrations"))
    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
    }
