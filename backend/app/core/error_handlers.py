import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppError
from app.schemas.error import ErrorResponse

logger = logging.getLogger(__name__)


def _build_error_response(
    *,
    error_code: str,
    message: str,
    path: str,
    status_code: int,
) -> JSONResponse:
    payload = ErrorResponse(
        error_code=error_code,
        message=message,
        detail=message,
        timestamp=datetime.now(timezone.utc),
        path=path,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        logger.warning(
            "Application error | error_code=%s | path=%s | message=%s",
            exc.error_code,
            request.url.path,
            exc.message,
        )
        return _build_error_response(
            error_code=exc.error_code,
            message=exc.message,
            path=request.url.path,
            status_code=exc.status_code,
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        error_code = "HTTP_ERROR"
        if exc.status_code == 404:
            error_code = "NOT_FOUND"
        elif exc.status_code == 400:
            error_code = "BAD_REQUEST"

        return _build_error_response(
            error_code=error_code,
            message=message,
            path=request.url.path,
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        message = "; ".join(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
        logger.warning(
            "Validation error | path=%s | message=%s",
            request.url.path,
            message,
        )
        return _build_error_response(
            error_code="VALIDATION_ERROR",
            message=message,
            path=request.url.path,
            status_code=422,
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_database_error(
        request: Request,
        exc: SQLAlchemyError,
    ) -> JSONResponse:
        logger.error(
            "Database error | path=%s",
            request.url.path,
            exc_info=exc,
        )
        return _build_error_response(
            error_code="DATABASE_ERROR",
            message="A database error occurred",
            path=request.url.path,
            status_code=500,
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(
        request: Request,
        exc: ValueError,
    ) -> JSONResponse:
        if request.url.path.endswith("/upload"):
            logger.warning(
                "Upload validation error | path=%s | message=%s",
                request.url.path,
                str(exc),
            )
            return _build_error_response(
                error_code="UPLOAD_VALIDATION_ERROR",
                message=str(exc),
                path=request.url.path,
                status_code=400,
            )

        logger.error(
            "Unexpected value error | path=%s",
            request.url.path,
            exc_info=exc,
        )
        return _build_error_response(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            path=request.url.path,
            status_code=500,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.error(
            "Unexpected error | path=%s",
            request.url.path,
            exc_info=exc,
        )
        return _build_error_response(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            path=request.url.path,
            status_code=500,
        )
