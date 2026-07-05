from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.analysis import ProjectAnalysisResponse
from app.services.project_analysis_service import get_project_analysis

router = APIRouter(prefix="/projects", tags=["analysis"])


@router.get(
    "/{project_id}/analysis",
    response_model=ProjectAnalysisResponse,
    summary="Get static analysis results",
    description=(
        "Returns classes, methods, dependencies, and summary metrics "
        "produced during project ingestion."
    ),
)
def get_analysis(
    project_id: int,
    db: Session = Depends(get_db),
) -> ProjectAnalysisResponse:
    return get_project_analysis(db, project_id)
