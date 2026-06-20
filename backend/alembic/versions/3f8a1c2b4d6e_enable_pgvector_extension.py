"""enable pgvector extension

Revision ID: 3f8a1c2b4d6e
Revises: 4dae0c0062bd
Create Date: 2026-06-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3f8a1c2b4d6e"
down_revision: Union[str, Sequence[str], None] = "4dae0c0062bd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector;")
