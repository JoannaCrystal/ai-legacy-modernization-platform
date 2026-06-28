from sqlalchemy.orm import Session

from app.models.enterprise_report import EnterpriseReport
from app.models.project import Project
from app.models.project_analysis_snapshot import ProjectAnalysisSnapshot
from app.services.analysis_persistence_service import (
    AnalysisNotFoundError,
    get_latest_snapshot,
)
from app.services.pdf_service import generate_pdf
from app.services.project_analysis_service import ProjectNotFoundError
from app.services.report_builder_service import build_enterprise_report


class ReportNotFoundError(Exception):
    pass


def list_project_history(db: Session) -> list[dict]:
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    history: list[dict] = []

    for project in projects:
        snapshot = get_latest_snapshot(db, project.id)
        latest_report = (
            db.query(EnterpriseReport)
            .filter(EnterpriseReport.project_id == project.id)
            .order_by(EnterpriseReport.generated_at.desc())
            .first()
        )

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


def generate_and_store_report(db: Session, project_id: int) -> tuple[EnterpriseReport, bytes]:
    project = _get_project_or_raise(db, project_id)
    snapshot = get_latest_snapshot(db, project_id)
    if snapshot is None:
        raise AnalysisNotFoundError()

    report_data = build_enterprise_report(
        project_name=project.name,
        project_id=project.id,
        upload_date=project.created_at,
        analysis_payload=snapshot.payload,
    )
    pdf_bytes = generate_pdf(report_data)

    report = EnterpriseReport(
        project_id=project.id,
        analysis_snapshot_id=snapshot.id,
        overall_risk=snapshot.overall_risk,
        pdf_data=pdf_bytes,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
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
