from typing import NotRequired, TypedDict


class ModernizationState(TypedDict):
    project_id: int
    classes: list
    methods: list
    dependencies: list
    code_analysis: NotRequired[dict]
    dependency_analysis: NotRequired[dict]
    risk_analysis: NotRequired[dict]
    architecture_summary: NotRequired[dict]
    business_capabilities: NotRequired[dict]
    retrieved_context: NotRequired[list[str]]
    architecture_report: NotRequired[dict]
    modernization_plan: NotRequired[dict]
    code_modernization: NotRequired[dict]
    modernization_roadmap: NotRequired[dict]
