from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_analysis_snapshot import ProjectAnalysisSnapshot


class AnalysisNotFoundError(Exception):
    pass


def get_latest_snapshot(
    db: Session,
    project_id: int,
) -> ProjectAnalysisSnapshot | None:
    return (
        db.query(ProjectAnalysisSnapshot)
        .filter(ProjectAnalysisSnapshot.project_id == project_id)
        .order_by(ProjectAnalysisSnapshot.completed_at.desc())
        .first()
    )


def save_analysis_snapshot(
    db: Session,
    project_id: int,
    payload: dict,
) -> ProjectAnalysisSnapshot:
    risk_analysis = payload.get("risk_analysis", {})
    overall_risk = risk_analysis.get("overall_risk", "UNKNOWN")

    snapshot = ProjectAnalysisSnapshot(
        project_id=project_id,
        payload=payload,
        overall_risk=overall_risk,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(snapshot)

    project = db.query(Project).filter(Project.id == project_id).first()
    if project is not None:
        project.status = "ANALYZED"

    db.commit()
    db.refresh(snapshot)
    return snapshot
