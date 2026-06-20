from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.modernization import ModernizationPlanResponse
from app.services.modernization_service import generate_modernization_plan
from app.services.project_analysis_service import ProjectNotFoundError

router = APIRouter(prefix="/projects", tags=["modernization"])


@router.get(
    "/{project_id}/modernization-plan",
    response_model=ModernizationPlanResponse,
)
def get_modernization_plan(
    project_id: int,
    db: Session = Depends(get_db),
) -> ModernizationPlanResponse:
    try:
        result = generate_modernization_plan(project_id, db)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        ) from exc

    return ModernizationPlanResponse(**result)
