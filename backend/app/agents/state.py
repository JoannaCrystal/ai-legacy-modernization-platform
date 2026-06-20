from typing import NotRequired, TypedDict


class ModernizationState(TypedDict):
    project_id: int
    classes: list
    methods: list
    dependencies: list
    code_analysis: NotRequired[dict]
    dependency_analysis: NotRequired[dict]
    risk_analysis: NotRequired[dict]
    modernization_plan: NotRequired[dict]
