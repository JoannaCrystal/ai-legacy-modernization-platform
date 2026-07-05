import os
from pathlib import Path

from dotenv import load_dotenv

_backend_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_backend_root / ".env")

DEFAULT_DATABASE_URL = (
    "postgresql://admin:password@localhost:5432/modernizer_db"
)
DEFAULT_CORS_ORIGINS = "http://127.0.0.1:5173,http://localhost:5173"
DEFAULT_MAX_UPLOAD_SIZE_BYTES = 52_428_800  # 50 MB
DEFAULT_MAX_ZIP_FILES = 5_000
DEFAULT_MAX_UNCOMPRESSED_SIZE_BYTES = 524_288_000  # 500 MB


def _parse_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return int(raw_value)


def _parse_csv(name: str, default: str) -> list[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


class Settings:
    APP_NAME: str = os.getenv(
        "APP_NAME",
        "AI Legacy Modernization Platform",
    )
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    CORS_ORIGINS: list[str] = _parse_csv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
    MAX_UPLOAD_SIZE_BYTES: int = _parse_int(
        "MAX_UPLOAD_SIZE_BYTES",
        DEFAULT_MAX_UPLOAD_SIZE_BYTES,
    )
    MAX_ZIP_FILES: int = _parse_int("MAX_ZIP_FILES", DEFAULT_MAX_ZIP_FILES)
    MAX_UNCOMPRESSED_SIZE_BYTES: int = _parse_int(
        "MAX_UNCOMPRESSED_SIZE_BYTES",
        DEFAULT_MAX_UNCOMPRESSED_SIZE_BYTES,
    )


settings = Settings()


def validate_startup_config() -> None:
    missing: list[str] = []

    if not settings.DATABASE_URL.strip():
        missing.append("DATABASE_URL")

    if not settings.OPENAI_API_KEY.strip():
        missing.append("OPENAI_API_KEY")

    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Missing required environment variables: {joined}. "
            "Set them in backend/.env before starting the application."
        )

    if settings.MAX_UPLOAD_SIZE_BYTES <= 0:
        raise RuntimeError("MAX_UPLOAD_SIZE_BYTES must be greater than zero")

    if settings.MAX_ZIP_FILES <= 0:
        raise RuntimeError("MAX_ZIP_FILES must be greater than zero")
