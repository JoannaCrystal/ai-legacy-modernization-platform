"""create code analysis tables

Revision ID: 4dae0c0062bd
Revises: 8d23d65e6b91
Create Date: 2026-06-13 10:15:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4dae0c0062bd"
down_revision: Union[str, Sequence[str], None] = "8d23d65e6b91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "code_classes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code_file_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=True),
        sa.Column("end_line", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["code_file_id"], ["code_files.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_code_classes_code_file_id"),
        "code_classes",
        ["code_file_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_code_classes_id"), "code_classes", ["id"], unique=False
    )

    op.create_table(
        "code_methods",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("parameters", sa.String(), nullable=True),
        sa.Column("return_type", sa.String(), nullable=True),
        sa.Column("start_line", sa.Integer(), nullable=True),
        sa.Column("end_line", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["class_id"], ["code_classes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_code_methods_class_id"),
        "code_methods",
        ["class_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_code_methods_id"), "code_methods", ["id"], unique=False
    )

    op.create_table(
        "code_dependencies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code_file_id", sa.Integer(), nullable=False),
        sa.Column("dependency_name", sa.String(), nullable=False),
        sa.Column("dependency_type", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["code_file_id"], ["code_files.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_code_dependencies_code_file_id"),
        "code_dependencies",
        ["code_file_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_code_dependencies_id"),
        "code_dependencies",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_code_dependencies_id"), table_name="code_dependencies"
    )
    op.drop_index(
        op.f("ix_code_dependencies_code_file_id"),
        table_name="code_dependencies",
    )
    op.drop_table("code_dependencies")
    op.drop_index(op.f("ix_code_methods_id"), table_name="code_methods")
    op.drop_index(op.f("ix_code_methods_class_id"), table_name="code_methods")
    op.drop_table("code_methods")
    op.drop_index(op.f("ix_code_classes_id"), table_name="code_classes")
    op.drop_index(
        op.f("ix_code_classes_code_file_id"), table_name="code_classes"
    )
    op.drop_table("code_classes")
