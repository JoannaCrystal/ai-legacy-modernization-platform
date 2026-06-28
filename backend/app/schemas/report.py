from datetime import datetime

from pydantic import BaseModel


class ReportMetadataResponse(BaseModel):
    report_id: int
    project_id: int
    analysis_snapshot_id: int
    overall_risk: str
    generated_at: datetime


class ProjectHistoryItem(BaseModel):
    project_id: int
    project_name: str
    upload_date: datetime
    analysis_completed_at: datetime | None
    overall_risk: str | None
    analysis_status: str
    report_status: str
    latest_report_id: int | None


class PersistedAnalysisResponse(BaseModel):
    project_id: int
    project_name: str
    analysis_completed_at: datetime
    overall_risk: str
    payload: dict
