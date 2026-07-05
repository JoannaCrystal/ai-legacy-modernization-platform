import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analysis import router as analysis_router
from app.api.health import router as health_router
from app.api.knowledge import router as knowledge_router
from app.api.modernization import router as modernization_router
from app.api.projects import router as projects_router
from app.api.reports import router as reports_router
from app.core.config import settings, validate_startup_config
from app.core.error_handlers import register_exception_handlers
from app.core.logging_config import configure_logging
from app.middleware.request_logging import RequestLoggingMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    validate_startup_config()
    logger.info(
        "Application startup | service=%s | version=%s | env=%s",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV,
    )
    yield
    logger.info("Application shutdown | service=%s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Enterprise API for analyzing legacy applications, generating "
        "modernization plans, and producing executive reports."
    ),
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(projects_router)
app.include_router(analysis_router)
app.include_router(modernization_router)
app.include_router(reports_router)
app.include_router(knowledge_router)


@app.get(
    "/",
    summary="Legacy health check",
    description="Backward-compatible root endpoint confirming the API is running.",
)
def root_health_check():
    return {
        "status": "running",
    }
