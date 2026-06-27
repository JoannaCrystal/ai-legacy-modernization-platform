from pydantic import BaseModel


class ModernizationPlanResponse(BaseModel):
    project_id: int
    classes: list[dict]
    methods: list[dict]
    dependencies: list[dict]
    code_analysis: dict
    dependency_analysis: dict
    risk_analysis: dict
    architecture_summary: dict
    modernization_plan: dict
