from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.analysis import ProjectAnalysisResponse
from app.services.project_analysis_service import (
    ProjectNotFoundError,
    get_project_analysis,
)

router = APIRouter(prefix="/projects", tags=["analysis"])


@router.get("/{project_id}/analysis", response_model=ProjectAnalysisResponse)
def get_analysis(
    project_id: int,
    db: Session = Depends(get_db),
) -> ProjectAnalysisResponse:
    try:
        return get_project_analysis(db, project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        ) from exc
