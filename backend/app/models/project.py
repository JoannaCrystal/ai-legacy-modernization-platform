from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.code_file import CodeFile
    from app.models.enterprise_report import EnterpriseReport
    from app.models.project_analysis_snapshot import ProjectAnalysisSnapshot


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        String,
        default="UPLOADED",
        server_default="UPLOADED",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    code_files: Mapped[list["CodeFile"]] = relationship(
        back_populates="project",
    )
    analysis_snapshots: Mapped[list["ProjectAnalysisSnapshot"]] = relationship(
        back_populates="project",
    )
    enterprise_reports: Mapped[list["EnterpriseReport"]] = relationship(
        back_populates="project",
    )
