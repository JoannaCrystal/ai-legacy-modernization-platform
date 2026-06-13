import zipfile
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.project import UploadResponse
from app.services.ingestion_service import ingest_zip_archive

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/upload", response_model=UploadResponse)
async def upload_legacy_application(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are accepted",
        )

    zip_bytes = await file.read()
    if not zip_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if not zipfile.is_zipfile(BytesIO(zip_bytes)):
        raise HTTPException(status_code=400, detail="Invalid ZIP file")

    try:
        result = ingest_zip_archive(db, name, zip_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UploadResponse(
        project_id=result.project_id,
        status=result.status,
        files_processed=result.files_processed,
    )
