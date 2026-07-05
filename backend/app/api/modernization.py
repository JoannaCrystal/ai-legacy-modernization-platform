from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.modernization import ModernizationPlanResponse
from app.services.modernization_service import generate_modernization_plan

router = APIRouter(prefix="/projects", tags=["modernization"])


@router.get(
    "/{project_id}/modernization-plan",
    response_model=ModernizationPlanResponse,
    summary="Generate or retrieve a modernization plan",
    description=(
        "Runs the LangGraph modernization workflow for the project on first "
        "request and returns the cached analysis snapshot on subsequent "
        "requests."
    ),
)
def get_modernization_plan(
    project_id: int,
    db: Session = Depends(get_db),
) -> ModernizationPlanResponse:
    result = generate_modernization_plan(project_id, db)
    return ModernizationPlanResponse(**result)
