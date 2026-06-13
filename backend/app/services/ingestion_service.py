import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath

from sqlalchemy.orm import Session

from app.models.code_file import CodeFile
from app.models.project import Project

IGNORED_DIRS = {".git", "target", "build", "node_modules", "__pycache__"}

ALLOWED_EXTENSIONS = {
    ".java",
    ".py",
    ".xml",
    ".yml",
    ".yaml",
    ".sql",
    ".properties",
}

EXTENSION_TO_LANGUAGE = {
    ".java": "java",
    ".py": "python",
    ".xml": "xml",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".sql": "sql",
    ".properties": "properties",
}


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

    return extracted_files


def ingest_zip_archive(
    db: Session,
    project_name: str,
    zip_bytes: bytes,
) -> IngestionResult:
    if not zipfile.is_zipfile(BytesIO(zip_bytes)):
        raise ValueError("Invalid ZIP file")

    project = Project(name=project_name, status="UPLOADED")
    db.add(project)
    db.flush()

    extracted_files = _extract_source_files(zip_bytes)

    for extracted_file in extracted_files:
        db.add(
            CodeFile(
                project_id=project.id,
                file_path=extracted_file.file_path,
                file_name=extracted_file.file_name,
                language=extracted_file.language,
                file_size=extracted_file.file_size,
                content=extracted_file.content,
            )
        )

    db.commit()
    db.refresh(project)

    return IngestionResult(
        project_id=project.id,
        status=project.status,
        files_processed=len(extracted_files),
    )
