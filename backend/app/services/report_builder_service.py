from datetime import datetime, timezone
from typing import Any


def build_enterprise_report(
    project_name: str,
    project_id: int,
    upload_date: datetime,
    analysis_payload: dict[str, Any],
) -> dict[str, Any]:
    architecture_report = analysis_payload.get("architecture_report", {})
    architecture_summary = analysis_payload.get("architecture_summary", {})
    business_capabilities = analysis_payload.get("business_capabilities", {})
    dependency_analysis = analysis_payload.get("dependency_analysis", {})
    risk_analysis = analysis_payload.get("risk_analysis", {})
    modernization_plan = analysis_payload.get("modernization_plan", {})
    code_modernization = analysis_payload.get("code_modernization", {})
    modernization_roadmap = analysis_payload.get("modernization_roadmap", {})
    code_analysis = analysis_payload.get("code_analysis", {})
    dependencies = analysis_payload.get("dependencies", [])

    generated_at = datetime.now(timezone.utc).isoformat()

    executive_summary = _build_executive_summary(
        architecture_report,
        risk_analysis,
        modernization_plan,
    )
    conclusion = _build_conclusion(modernization_plan, modernization_roadmap)

    return {
        "cover_page": {
            "title": "Enterprise Modernization Assessment",
            "subtitle": project_name,
            "project_id": project_id,
        },
        "project_information": {
            "project_name": project_name,
            "project_id": project_id,
            "upload_date": upload_date.isoformat(),
            "analysis_summary": code_analysis.get("summary", ""),
            "total_dependencies": dependency_analysis.get(
                "total_dependencies",
                len(dependencies),
            ),
            "overall_risk": risk_analysis.get("overall_risk", "UNKNOWN"),
        },
        "executive_summary": executive_summary,
        "application_overview": architecture_report.get(
            "application_overview",
            "",
        ),
        "architecture_summary": {
            "narrative": architecture_report.get("architecture_summary", ""),
            "components": architecture_summary.get("components", []),
            "technology_summary": architecture_report.get(
                "technology_summary",
                "",
            ),
        },
        "architecture_components": architecture_summary.get("components", []),
        "business_capabilities": business_capabilities.get("capabilities", []),
        "dependency_analysis": {
            "dependencies": dependencies,
            "high_risk_dependencies": dependency_analysis.get(
                "high_risk_dependencies",
                [],
            ),
        },
        "technical_risk_assessment": {
            "overall_risk": risk_analysis.get("overall_risk", "UNKNOWN"),
            "reason": risk_analysis.get("reason", ""),
            "technical_risks": architecture_report.get("technical_risks", []),
        },
        "modernization_plan": modernization_plan,
        "code_modernization": code_modernization.get("opportunities", []),
        "modernization_roadmap": modernization_roadmap.get("phases", []),
        "conclusion": conclusion,
        "report_generated_at": generated_at,
    }


def _build_executive_summary(
    architecture_report: dict,
    risk_analysis: dict,
    modernization_plan: dict,
) -> str:
    parts = [
        architecture_report.get("application_overview", ""),
        f"Overall technical risk: {risk_analysis.get('overall_risk', 'UNKNOWN')}.",
        risk_analysis.get("reason", ""),
        modernization_plan.get(
            "architecture_assessment",
            modernization_plan.get("summary", ""),
        ),
        modernization_plan.get("target_architecture", ""),
    ]
    return " ".join(part for part in parts if part).strip()


def _build_conclusion(
    modernization_plan: dict,
    modernization_roadmap: dict,
) -> str:
    phase_count = len(modernization_roadmap.get("phases", []))
    recommended_steps = modernization_plan.get("recommended_steps", [])
    if not recommended_steps:
        recommended_steps = modernization_plan.get("recommendations", [])

    steps_text = ", ".join(recommended_steps[:3])
    return (
        f"This assessment recommends a phased modernization approach across "
        f"{phase_count} execution phases. Priority actions include "
        f"{steps_text or 'targeted legacy remediation'}. "
        f"The roadmap balances technical risk reduction, business impact, "
        f"and implementation complexity to support an executable migration plan."
    )
