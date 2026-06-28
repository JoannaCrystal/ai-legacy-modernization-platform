from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.project_analysis_snapshot import ProjectAnalysisSnapshot


class EnterpriseReport(Base):
    __tablename__ = "enterprise_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )
    analysis_snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("project_analysis_snapshots.id"),
        nullable=False,
        index=True,
    )
    overall_risk: Mapped[str] = mapped_column(String, nullable=False)
    pdf_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(back_populates="enterprise_reports")
    analysis_snapshot: Mapped["ProjectAnalysisSnapshot"] = relationship(
        back_populates="reports",
    )
