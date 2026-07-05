import os

os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://admin:password@localhost:5432/modernizer_db",
)
