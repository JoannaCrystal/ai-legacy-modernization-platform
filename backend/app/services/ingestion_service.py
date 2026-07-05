import logging
import time
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath

from sqlalchemy.orm import Session

from app.core.exceptions import UploadValidationError
from app.core.logging_config import log_with_context
from app.core.upload_validation import (
    ALLOWED_EXTENSIONS,
    EXTENSION_TO_LANGUAGE,
    IGNORED_DIRS,
    validate_zip_archive,
)
from app.models.code_file import CodeFile
from app.models.project import Project
from app.services.code_analysis_service import analyze_code_file

logger = logging.getLogger(__name__)


@dataclass
class ExtractedFile:
    file_path: str
    file_name: str
    language: str
    file_size: int
    content: str


@dataclass
class IngestionResult:
    project_id: int
    status: str
    files_processed: int


def _is_ignored_path(file_path: str) -> bool:
    return any(part in IGNORED_DIRS for part in PurePosixPath(file_path).parts)


def _is_safe_path(file_path: str) -> bool:
    return ".." not in PurePosixPath(file_path).parts


def _extract_source_files(zip_bytes: bytes) -> list[ExtractedFile]:
    extracted_files: list[ExtractedFile] = []

    try:
        with zipfile.ZipFile(BytesIO(zip_bytes)) as archive:
            for entry in archive.infolist():
                if entry.is_dir():
                    continue

                file_path = entry.filename
                if not _is_safe_path(file_path) or _is_ignored_path(file_path):
                    continue

                extension = PurePosixPath(file_path).suffix.lower()
                if extension not in ALLOWED_EXTENSIONS:
                    continue

                language = EXTENSION_TO_LANGUAGE[extension]
                content_bytes = archive.read(entry)
                file_size = len(content_bytes)
                content = content_bytes.decode("utf-8", errors="replace")

                extracted_files.append(
                    ExtractedFile(
                        file_path=file_path,
                        file_name=PurePosixPath(file_path).name,
                        language=language,
                        file_size=file_size,
                        content=content,
                    )
                )
    except zipfile.BadZipFile as exc:
        raise UploadValidationError("Malformed ZIP archive") from exc

    return extracted_files


def ingest_zip_archive(
    db: Session,
    project_name: str,
    zip_bytes: bytes,
) -> IngestionResult:
    start_time = time.perf_counter()
    validate_zip_archive(zip_bytes)

    project = Project(name=project_name, status="UPLOADED")
    db.add(project)
    db.flush()

    try:
        extracted_files = _extract_source_files(zip_bytes)

        for extracted_file in extracted_files:
            code_file = CodeFile(
                project_id=project.id,
                file_path=extracted_file.file_path,
                file_name=extracted_file.file_name,
                language=extracted_file.language,
                file_size=extracted_file.file_size,
                content=extracted_file.content,
            )
            db.add(code_file)
            db.flush()
            analyze_code_file(db, code_file)

        db.commit()
        db.refresh(project)
    except Exception:
        db.rollback()
        raise

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    log_with_context(
        logger,
        logging.INFO,
        "Project upload ingested",
        project_id=project.id,
        project_name=project_name,
        files_processed=len(extracted_files),
        duration_ms=duration_ms,
    )

    return IngestionResult(
        project_id=project.id,
        status=project.status,
        files_processed=len(extracted_files),
    )
