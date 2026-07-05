from io import BytesIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.report import (
    PersistedAnalysisResponse,
    ProjectHistoryItem,
    ReportMetadataResponse,
)
from app.services.report_service import (
    generate_and_store_report,
    get_persisted_analysis,
    get_report_metadata,
    get_report_pdf,
    list_project_history,
    list_project_reports,
)

router = APIRouter(prefix="/projects", tags=["reports"])


@router.get(
    "/history",
    response_model=list[ProjectHistoryItem],
    summary="List project history",
    description=(
        "Returns uploaded projects with analysis and report status metadata."
    ),
)
def get_project_history(db: Session = Depends(get_db)) -> list[ProjectHistoryItem]:
    return list_project_history(db)


@router.get(
    "/{project_id}/analysis-result",
    response_model=PersistedAnalysisResponse,
    summary="Get completed analysis snapshot",
    description=(
        "Returns the persisted modernization workflow payload for a project "
        "after analysis has completed."
    ),
)
def get_completed_analysis(
    project_id: int,
    db: Session = Depends(get_db),
) -> PersistedAnalysisResponse:
    return get_persisted_analysis(db, project_id)


@router.get(
    "/{project_id}/reports",
    response_model=list[ReportMetadataResponse],
    summary="List generated reports",
    description="Returns metadata for all enterprise reports generated for a project.",
)
def get_project_reports(
    project_id: int,
    db: Session = Depends(get_db),
) -> list[ReportMetadataResponse]:
    return list_project_reports(db, project_id)


@router.get(
    "/{project_id}/reports/{report_id}",
    response_model=ReportMetadataResponse,
    summary="Get report metadata",
    description="Returns metadata for a specific enterprise report.",
)
def get_report_details(
    project_id: int,
    report_id: int,
    db: Session = Depends(get_db),
) -> ReportMetadataResponse:
    return get_report_metadata(db, project_id, report_id)


@router.post(
    "/{project_id}/reports/generate",
    summary="Generate an enterprise PDF report",
    description=(
        "Builds an enterprise report from the latest completed analysis "
        "snapshot and returns the generated PDF."
    ),
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Generated enterprise PDF report",
        }
    },
)
def generate_project_report(
    project_id: int,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    report, pdf_bytes = generate_and_store_report(db, project_id)

    filename = f"modernization-report-project-{project_id}-{report.id}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{project_id}/reports/{report_id}/download",
    summary="Download a generated report",
    description="Downloads a previously generated enterprise PDF report.",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Enterprise PDF report download",
        }
    },
)
def download_project_report(
    project_id: int,
    report_id: int,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    report, pdf_bytes = get_report_pdf(db, project_id, report_id)

    filename = f"modernization-report-project-{project_id}-{report.id}.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
