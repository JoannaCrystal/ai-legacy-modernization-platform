from sqlalchemy.orm import Session

from app.models.code_analysis import CodeClass, CodeDependency, CodeMethod
from app.models.code_file import CodeFile
from app.models.project import Project
from app.schemas.analysis import (
    AnalysisSummary,
    ClassAnalysis,
    DependencyAnalysis,
    MethodAnalysis,
    ProjectAnalysisResponse,
)
from app.services.dependency_intelligence_service import (
    DependencyIntelligenceService,
)


class ProjectNotFoundError(Exception):
    pass


def get_project_analysis(
    db: Session,
    project_id: int,
) -> ProjectAnalysisResponse:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise ProjectNotFoundError()

    code_files = (
        db.query(CodeFile).filter(CodeFile.project_id == project_id).all()
    )
    code_file_ids = [code_file.id for code_file in code_files]

    classes = _get_classes(db, code_file_ids)
    methods = _get_methods(db, code_file_ids)
    dependencies = _get_dependencies(db, code_file_ids)

    summary = AnalysisSummary(
        total_files=len(code_files),
        total_classes=len(classes),
        total_methods=len(methods),
        total_dependencies=len(dependencies),
    )

    return ProjectAnalysisResponse(
        project_id=project.id,
        project_name=project.name,
        summary=summary,
        classes=classes,
        methods=methods,
        dependencies=dependencies,
    )


def _get_classes(
    db: Session,
    code_file_ids: list[int],
) -> list[ClassAnalysis]:
    if not code_file_ids:
        return []

    rows = (
        db.query(CodeClass, CodeFile)
        .join(CodeFile, CodeClass.code_file_id == CodeFile.id)
        .filter(CodeClass.code_file_id.in_(code_file_ids))
        .all()
    )

    return [
        ClassAnalysis(
            name=code_class.name,
            file=code_file.file_name or code_file.file_path,
        )
        for code_class, code_file in rows
    ]


def _get_methods(
    db: Session,
    code_file_ids: list[int],
) -> list[MethodAnalysis]:
    if not code_file_ids:
        return []

    rows = (
        db.query(CodeMethod, CodeClass)
        .join(CodeClass, CodeMethod.class_id == CodeClass.id)
        .filter(CodeClass.code_file_id.in_(code_file_ids))
        .all()
    )

    return [
        MethodAnalysis(
            name=code_method.name,
            class_name=code_class.name,
            return_type=code_method.return_type,
        )
        for code_method, code_class in rows
    ]


def _get_dependencies(
    db: Session,
    code_file_ids: list[int],
) -> list[DependencyAnalysis]:
    if not code_file_ids:
        return []

    dependency_rows = (
        db.query(CodeDependency)
        .filter(CodeDependency.code_file_id.in_(code_file_ids))
        .all()
    )

    intelligence_service = DependencyIntelligenceService()
    seen: set[str] = set()
    dependencies: list[DependencyAnalysis] = []

    for dependency_row in dependency_rows:
        if dependency_row.dependency_name in seen:
            continue
        seen.add(dependency_row.dependency_name)

        result = intelligence_service.analyze_dependency(
            dependency_row.dependency_name
        )
        dependencies.append(DependencyAnalysis(**result))

    return dependencies
