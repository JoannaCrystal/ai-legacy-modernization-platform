from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.upload_validation import validate_upload_filename
from app.database.session import get_db
from app.schemas.project import UploadResponse
from app.services.ingestion_service import ingest_zip_archive

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload a legacy application archive",
    description=(
        "Accepts a ZIP archive containing supported legacy source files, "
        "creates a project, extracts supported files, and runs static code "
        "analysis during ingestion."
    ),
)
async def upload_legacy_application(
    name: str = Form(..., description="Display name for the uploaded project"),
    file: UploadFile = File(..., description="ZIP archive of legacy source code"),
    db: Session = Depends(get_db),
) -> UploadResponse:
    validate_upload_filename(file.filename)

    zip_bytes = await file.read()
    result = ingest_zip_archive(db, name, zip_bytes)

    return UploadResponse(
        project_id=result.project_id,
        status=result.status,
        files_processed=result.files_processed,
    )
