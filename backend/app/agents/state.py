from typing import TypedDict


class ModernizationState(TypedDict):
    project_id: str
    classes: list[str]
    methods: list[str]
    dependencies: list[str]
    dependency_findings: list[str]
    risk_findings: list[str]
    modernization_recommendations: list[str]
