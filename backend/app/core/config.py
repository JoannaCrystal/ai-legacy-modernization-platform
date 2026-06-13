import os
from pathlib import Path

from dotenv import load_dotenv

_backend_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_backend_root / ".env")

DEFAULT_DATABASE_URL = (
    "postgresql://admin:password@localhost:5432/modernizer_db"
)


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


settings = Settings()
