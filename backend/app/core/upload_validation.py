import zipfile
from io import BytesIO
from pathlib import PurePosixPath

from app.core.config import settings
from app.core.exceptions import UploadValidationError

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


def validate_upload_filename(filename: str | None) -> None:
    if not filename or not filename.lower().endswith(".zip"):
        raise UploadValidationError("Only ZIP files are accepted")


def validate_zip_archive(zip_bytes: bytes) -> None:
    if not zip_bytes:
        raise UploadValidationError("Uploaded file is empty")

    if len(zip_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
        raise UploadValidationError(
            f"Upload exceeds the maximum allowed size of {max_mb} MB"
        )

    if not zipfile.is_zipfile(BytesIO(zip_bytes)):
        raise UploadValidationError("Invalid ZIP file")

    try:
        with zipfile.ZipFile(BytesIO(zip_bytes)) as archive:
            entries = archive.infolist()
    except zipfile.BadZipFile as exc:
        raise UploadValidationError("Malformed ZIP archive") from exc

    if len(entries) > settings.MAX_ZIP_FILES:
        raise UploadValidationError(
            f"Archive contains too many files "
            f"(maximum {settings.MAX_ZIP_FILES})"
        )

    total_uncompressed_size = 0
    supported_files = 0
    unsupported_files: list[str] = []

    for entry in entries:
        if entry.is_dir():
            continue

        total_uncompressed_size += entry.file_size
        if total_uncompressed_size > settings.MAX_UNCOMPRESSED_SIZE_BYTES:
            raise UploadValidationError(
                "Archive exceeds the maximum allowed uncompressed size"
            )

        file_path = entry.filename
        if not _is_safe_path(file_path):
            raise UploadValidationError(
                f"Archive contains an unsafe path: {file_path}"
            )

        if _is_ignored_path(file_path):
            continue

        extension = PurePosixPath(file_path).suffix.lower()
        if extension in ALLOWED_EXTENSIONS:
            supported_files += 1
        else:
            unsupported_files.append(file_path)

    if supported_files == 0:
        if unsupported_files:
            raise UploadValidationError(
                "Archive does not contain supported source files. "
                f"Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        raise UploadValidationError(
            "Archive does not contain any supported source files"
        )


def _is_ignored_path(file_path: str) -> bool:
    return any(part in IGNORED_DIRS for part in PurePosixPath(file_path).parts)


def _is_safe_path(file_path: str) -> bool:
    return ".." not in PurePosixPath(file_path).parts
