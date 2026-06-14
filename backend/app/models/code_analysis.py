from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.code_file import CodeFile


class CodeClass(Base):
    __tablename__ = "code_classes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code_file_id: Mapped[int] = mapped_column(
        ForeignKey("code_files.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    code_file: Mapped["CodeFile"] = relationship(back_populates="classes")
    methods: Mapped[list["CodeMethod"]] = relationship(
        back_populates="code_class",
    )


class CodeMethod(Base):
    __tablename__ = "code_methods"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    class_id: Mapped[int] = mapped_column(
        ForeignKey("code_classes.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    parameters: Mapped[str | None] = mapped_column(String, nullable=True)
    return_type: Mapped[str | None] = mapped_column(String, nullable=True)
    start_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    code_class: Mapped["CodeClass"] = relationship(back_populates="methods")


class CodeDependency(Base):
    __tablename__ = "code_dependencies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code_file_id: Mapped[int] = mapped_column(
        ForeignKey("code_files.id"),
        nullable=False,
        index=True,
    )
    dependency_name: Mapped[str] = mapped_column(String, nullable=False)
    dependency_type: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    code_file: Mapped["CodeFile"] = relationship(back_populates="dependencies")
