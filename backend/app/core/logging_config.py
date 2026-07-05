import logging
import sys
from typing import Any

from app.core.config import settings

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
        format=LOG_FORMAT,
        stream=sys.stdout,
        force=True,
    )

    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context: Any,
) -> None:
    if not context:
        logger.log(level, message)
        return

    context_parts = " | ".join(
        f"{key}={value}"
        for key, value in context.items()
        if value is not None
    )
    logger.log(level, "%s | %s", message, context_parts)
