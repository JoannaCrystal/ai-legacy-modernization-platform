from sqlalchemy.orm import Session

from app.agents.graph import graph
from app.models.code_analysis import CodeClass, CodeDependency, CodeMethod
from app.models.code_file import CodeFile
from app.models.project import Project
from app.services.dependency_intelligence_service import (
    DependencyIntelligenceService,
)
from app.services.project_analysis_service import ProjectNotFoundError


def generate_modernization_plan(project_id: int, db: Session) -> dict:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise ProjectNotFoundError()

    code_files = (
        db.query(CodeFile).filter(CodeFile.project_id == project_id).all()
    )
    code_file_ids = [code_file.id for code_file in code_files]

    classes = _load_classes(db, code_file_ids)
    methods = _load_methods(db, code_file_ids)
    dependencies = _load_dependencies(db, code_file_ids)

    state = {
        "project_id": project.id,
        "classes": [{"name": code_class.name} for code_class in classes],
        "methods": [{"name": code_method.name} for code_method in methods],
        "dependencies": dependencies,
    }

    return graph.invoke(state)


def _load_classes(db: Session, code_file_ids: list[int]) -> list[CodeClass]:
    if not code_file_ids:
        return []

    return (
        db.query(CodeClass)
        .filter(CodeClass.code_file_id.in_(code_file_ids))
        .all()
    )


def _load_methods(db: Session, code_file_ids: list[int]) -> list[CodeMethod]:
    if not code_file_ids:
        return []

    return (
        db.query(CodeMethod)
        .join(CodeClass, CodeMethod.class_id == CodeClass.id)
        .filter(CodeClass.code_file_id.in_(code_file_ids))
        .all()
    )


def _load_dependencies(
    db: Session,
    code_file_ids: list[int],
) -> list[dict[str, str]]:
    if not code_file_ids:
        return []

    dependency_rows = (
        db.query(CodeDependency)
        .filter(CodeDependency.code_file_id.in_(code_file_ids))
        .all()
    )

    intelligence_service = DependencyIntelligenceService()
    seen: set[str] = set()
    dependencies: list[dict[str, str]] = []

    for dependency_row in dependency_rows:
        if dependency_row.dependency_name in seen:
            continue
        seen.add(dependency_row.dependency_name)

        result = intelligence_service.analyze_dependency(
            dependency_row.dependency_name
        )
        dependencies.append(
            {
                "dependency": result["dependency"],
                "technology": result["technology"],
                "risk_level": result["risk_level"],
            }
        )

    return dependencies
