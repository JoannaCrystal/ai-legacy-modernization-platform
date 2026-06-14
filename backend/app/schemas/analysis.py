from pydantic import BaseModel, ConfigDict, Field


class AnalysisSummary(BaseModel):
    total_files: int
    total_classes: int
    total_methods: int
    total_dependencies: int


class ClassAnalysis(BaseModel):
    name: str
    file: str


class MethodAnalysis(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    class_name: str = Field(serialization_alias="class")
    return_type: str | None = None


class DependencyAnalysis(BaseModel):
    dependency: str
    technology: str
    category: str
    risk_level: str
    recommendation: str


class ProjectAnalysisResponse(BaseModel):
    project_id: int
    project_name: str
    summary: AnalysisSummary
    classes: list[ClassAnalysis]
    methods: list[MethodAnalysis]
    dependencies: list[DependencyAnalysis]
