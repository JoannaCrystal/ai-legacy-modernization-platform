import logging
import time

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AnalysisNotFoundError,
    ProjectNotFoundError,
    ReportNotFoundError,
)
from app.core.logging_config import log_with_context
from app.models.enterprise_report import EnterpriseReport
from app.models.project import Project
from app.models.project_analysis_snapshot import ProjectAnalysisSnapshot
from app.services.analysis_persistence_service import get_latest_snapshot
from app.services.pdf_service import generate_pdf
from app.services.report_builder_service import build_enterprise_report

logger = logging.getLogger(__name__)


def list_project_history(db: Session) -> list[dict]:
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    if not projects:
        return []

    project_ids = [project.id for project in projects]
    snapshots = (
        db.query(ProjectAnalysisSnapshot)
        .filter(ProjectAnalysisSnapshot.project_id.in_(project_ids))
        .order_by(ProjectAnalysisSnapshot.completed_at.desc())
        .all()
    )
    reports = (
        db.query(EnterpriseReport)
        .filter(EnterpriseReport.project_id.in_(project_ids))
        .order_by(EnterpriseReport.generated_at.desc())
        .all()
    )

    latest_snapshot_by_project: dict[int, ProjectAnalysisSnapshot] = {}
    for snapshot in snapshots:
        if snapshot.project_id not in latest_snapshot_by_project:
            latest_snapshot_by_project[snapshot.project_id] = snapshot

    latest_report_by_project: dict[int, EnterpriseReport] = {}
    for report in reports:
        if report.project_id not in latest_report_by_project:
            latest_report_by_project[report.project_id] = report

    history: list[dict] = []
    for project in projects:
        snapshot = latest_snapshot_by_project.get(project.id)
        latest_report = latest_report_by_project.get(project.id)

        history.append(
            {
                "project_id": project.id,
                "project_name": project.name,
                "upload_date": project.created_at,
                "analysis_completed_at": (
                    snapshot.completed_at if snapshot else None
                ),
                "overall_risk": snapshot.overall_risk if snapshot else None,
                "analysis_status": "COMPLETED" if snapshot else "PENDING",
                "report_status": "GENERATED" if latest_report else "NOT_GENERATED",
                "latest_report_id": latest_report.id if latest_report else None,
            }
        )

    return history


def list_project_reports(db: Session, project_id: int) -> list[dict]:
    _get_project_or_raise(db, project_id)
    reports = (
        db.query(EnterpriseReport)
        .filter(EnterpriseReport.project_id == project_id)
        .order_by(EnterpriseReport.generated_at.desc())
        .all()
    )
    return [_serialize_report_metadata(report) for report in reports]


def get_report_metadata(
    db: Session,
    project_id: int,
    report_id: int,
) -> dict:
    report = _get_report_or_raise(db, project_id, report_id)
    return _serialize_report_metadata(report)


def get_persisted_analysis(db: Session, project_id: int) -> dict:
    project = _get_project_or_raise(db, project_id)
    snapshot = get_latest_snapshot(db, project_id)
    if snapshot is None:
        raise AnalysisNotFoundError()

    return {
        "project_id": project.id,
        "project_name": project.name,
        "analysis_completed_at": snapshot.completed_at,
        "overall_risk": snapshot.overall_risk,
        "payload": snapshot.payload,
    }


def generate_and_store_report(
    db: Session,
    project_id: int,
) -> tuple[EnterpriseReport, bytes]:
    start_time = time.perf_counter()
    project = _get_project_or_raise(db, project_id)
    snapshot = get_latest_snapshot(db, project_id)
    if snapshot is None:
        raise AnalysisNotFoundError()

    try:
        report_data = build_enterprise_report(
            project_name=project.name,
            project_id=project.id,
            upload_date=project.created_at,
            analysis_payload=snapshot.payload,
        )
        pdf_bytes = generate_pdf(report_data)
    except Exception as exc:
        log_with_context(
            logger,
            logging.ERROR,
            "Report generation failed",
            project_id=project_id,
            error=str(exc),
        )
        raise

    report = EnterpriseReport(
        project_id=project.id,
        analysis_snapshot_id=snapshot.id,
        overall_risk=snapshot.overall_risk,
        pdf_data=pdf_bytes,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    log_with_context(
        logger,
        logging.INFO,
        "Report generated",
        project_id=project_id,
        report_id=report.id,
        duration_ms=duration_ms,
    )
    return report, pdf_bytes


def get_report_pdf(
    db: Session,
    project_id: int,
    report_id: int,
) -> tuple[EnterpriseReport, bytes]:
    report = _get_report_or_raise(db, project_id, report_id)
    return report, report.pdf_data


def _get_project_or_raise(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise ProjectNotFoundError()
    return project


def _get_report_or_raise(
    db: Session,
    project_id: int,
    report_id: int,
) -> EnterpriseReport:
    report = (
        db.query(EnterpriseReport)
        .filter(
            EnterpriseReport.project_id == project_id,
            EnterpriseReport.id == report_id,
        )
        .first()
    )
    if report is None:
        raise ReportNotFoundError()
    return report


def _serialize_report_metadata(report: EnterpriseReport) -> dict:
    return {
        "report_id": report.id,
        "project_id": report.project_id,
        "analysis_snapshot_id": report.analysis_snapshot_id,
        "overall_risk": report.overall_risk,
        "generated_at": report.generated_at,
    }
