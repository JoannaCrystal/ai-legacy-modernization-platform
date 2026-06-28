from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.report import (
    PersistedAnalysisResponse,
    ProjectHistoryItem,
    ReportMetadataResponse,
)
from app.services.analysis_persistence_service import AnalysisNotFoundError
from app.services.project_analysis_service import ProjectNotFoundError
from app.services.report_service import (
    ReportNotFoundError,
    generate_and_store_report,
    get_persisted_analysis,
    get_report_metadata,
    get_report_pdf,
    list_project_history,
    list_project_reports,
)

router = APIRouter(prefix="/projects", tags=["reports"])


@router.get("/history", response_model=list[ProjectHistoryItem])
def get_project_history(db: Session = Depends(get_db)) -> list[ProjectHistoryItem]:
    return list_project_history(db)


@router.get(
    "/{project_id}/analysis-result",
    response_model=PersistedAnalysisResponse,
)
def get_completed_analysis(
    project_id: int,
    db: Session = Depends(get_db),
) -> PersistedAnalysisResponse:
    try:
        return get_persisted_analysis(db, project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    except AnalysisNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Completed analysis not found for this project",
        ) from exc


@router.get(
    "/{project_id}/reports",
    response_model=list[ReportMetadataResponse],
)
def get_project_reports(
    project_id: int,
    db: Session = Depends(get_db),
) -> list[ReportMetadataResponse]:
    try:
        return list_project_reports(db, project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@router.get(
    "/{project_id}/reports/{report_id}",
    response_model=ReportMetadataResponse,
)
def get_report_details(
    project_id: int,
    report_id: int,
    db: Session = Depends(get_db),
) -> ReportMetadataResponse:
    try:
        return get_report_metadata(db, project_id, report_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    except ReportNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc


@router.post("/{project_id}/reports/generate")
def generate_project_report(
    project_id: int,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    try:
        report, pdf_bytes = generate_and_store_report(db, project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    except AnalysisNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Completed analysis not found for this project",
        ) from exc

    filename = f"modernization-report-project-{project_id}-{report.id}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{project_id}/reports/{report_id}/download")
def download_project_report(
    project_id: int,
    report_id: int,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    try:
        report, pdf_bytes = get_report_pdf(db, project_id, report_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    except ReportNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc

    filename = f"modernization-report-project-{project_id}-{report.id}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
