"""create analysis snapshots and enterprise reports tables

Revision ID: b7c4e2f91a3d
Revises: 9c2e7f1a8b4d
Create Date: 2026-06-27 14:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b7c4e2f91a3d"
down_revision: Union[str, Sequence[str], None] = "9c2e7f1a8b4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_analysis_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("overall_risk", sa.String(), nullable=False),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_project_analysis_snapshots_id"),
        "project_analysis_snapshots",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_analysis_snapshots_project_id"),
        "project_analysis_snapshots",
        ["project_id"],
        unique=False,
    )

    op.create_table(
        "enterprise_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("analysis_snapshot_id", sa.Integer(), nullable=False),
        sa.Column("overall_risk", sa.String(), nullable=False),
        sa.Column("pdf_data", sa.LargeBinary(), nullable=False),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(
            ["analysis_snapshot_id"],
            ["project_analysis_snapshots.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_enterprise_reports_id"),
        "enterprise_reports",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_enterprise_reports_project_id"),
        "enterprise_reports",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_enterprise_reports_analysis_snapshot_id"),
        "enterprise_reports",
        ["analysis_snapshot_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_enterprise_reports_analysis_snapshot_id"),
        table_name="enterprise_reports",
    )
    op.drop_index(
        op.f("ix_enterprise_reports_project_id"),
        table_name="enterprise_reports",
    )
    op.drop_index(
        op.f("ix_enterprise_reports_id"),
        table_name="enterprise_reports",
    )
    op.drop_table("enterprise_reports")
    op.drop_index(
        op.f("ix_project_analysis_snapshots_project_id"),
        table_name="project_analysis_snapshots",
    )
    op.drop_index(
        op.f("ix_project_analysis_snapshots_id"),
        table_name="project_analysis_snapshots",
    )
    op.drop_table("project_analysis_snapshots")
