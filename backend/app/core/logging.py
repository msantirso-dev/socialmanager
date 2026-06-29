from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import structlog

logger = structlog.get_logger()


class LogCategory(StrEnum):
    API = "api"
    AI = "ai"
    SOCIAL = "social"
    SCHEDULER = "scheduler"
    AUTH = "auth"
    ERROR = "error"
    AUDIT = "audit"


async def log_event(
    category: LogCategory,
    action: str,
    *,
    user_id: str | None = None,
    company_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    error: str | None = None,
    duration_ms: float | None = None,
    cost: float | None = None,
) -> None:
    """
    Central logging entry point.
    Phase 2 will persist to the `logs` table; for now structured stdout.
    """
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "category": category.value,
        "action": action,
        "user_id": user_id,
        "company_id": company_id,
        "metadata": metadata or {},
        "error": error,
        "duration_ms": duration_ms,
        "cost": cost,
    }
    if error:
        logger.error("app_event", **payload)
    else:
        logger.info("app_event", **payload)
