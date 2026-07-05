from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.health_checks import check_configuration, check_database
from app.database.session import get_db
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API health",
    description=(
        "Returns a lightweight health response confirming that the API "
        "process is running."
    ),
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Check application readiness",
    description=(
        "Verifies readiness by checking critical dependencies such as "
        "database connectivity and required application configuration."
    ),
)
def readiness_check(
    response: Response,
    db: Session = Depends(get_db),
) -> ReadinessResponse:
    dependencies = [
        check_configuration(),
        check_database(db),
    ]
    overall_status = (
        "ready"
        if all(item.status == "healthy" for item in dependencies)
        else "not_ready"
    )
    if overall_status != "ready":
        response.status_code = 503

    return ReadinessResponse(
        status=overall_status,
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        dependencies=dependencies,
    )
