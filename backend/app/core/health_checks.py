from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.health import DependencyStatus


def check_database(db: Session) -> DependencyStatus:
    try:
        db.execute(text("SELECT 1"))
        return DependencyStatus(
            name="database",
            status="healthy",
            message="Database connection successful",
        )
    except SQLAlchemyError as exc:
        return DependencyStatus(
            name="database",
            status="unhealthy",
            message=str(exc),
        )


def check_configuration() -> DependencyStatus:
    missing: list[str] = []

    if not settings.DATABASE_URL.strip():
        missing.append("DATABASE_URL")

    if not settings.OPENAI_API_KEY.strip():
        missing.append("OPENAI_API_KEY")

    if missing:
        return DependencyStatus(
            name="configuration",
            status="unhealthy",
            message=f"Missing required settings: {', '.join(missing)}",
        )

    return DependencyStatus(
        name="configuration",
        status="healthy",
        message="Required configuration is present",
    )
