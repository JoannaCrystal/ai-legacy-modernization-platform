from sqlalchemy.orm import Session

from app.agents.graph import graph
from app.models.code_analysis import CodeClass, CodeDependency, CodeMethod
from app.models.code_file import CodeFile
from app.models.project import Project
from app.services.analysis_persistence_service import (
    get_latest_snapshot,
    save_analysis_snapshot,
)
from app.services.dependency_intelligence_service import (
    DependencyIntelligenceService,
)
from app.services.project_analysis_service import ProjectNotFoundError


def generate_modernization_plan(project_id: int, db: Session) -> dict:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise ProjectNotFoundError()

    snapshot = get_latest_snapshot(db, project_id)
    if snapshot is not None:
        return snapshot.payload

    code_files = (
        db.query(CodeFile).filter(CodeFile.project_id == project_id).all()
    )
    code_file_ids = [code_file.id for code_file in code_files]

    classes = _load_classes(db, code_file_ids)
    methods = _load_methods(db, code_file_ids)
    dependencies = _load_dependencies(db, code_file_ids)

    state = {
        "project_id": project.id,
        "classes": classes,
        "methods": methods,
        "dependencies": dependencies,
    }

    result = graph.invoke(state)
    save_analysis_snapshot(db, project_id, result)
    return result


def _load_classes(db: Session, code_file_ids: list[int]) -> list[dict]:
    if not code_file_ids:
        return []

    rows = (
        db.query(CodeClass, CodeFile)
        .join(CodeFile, CodeClass.code_file_id == CodeFile.id)
        .filter(CodeClass.code_file_id.in_(code_file_ids))
        .all()
    )

    return [
        {
            "name": code_class.name,
            "file": code_file.file_name or code_file.file_path,
            "package": _infer_package(code_file.file_path),
        }
        for code_class, code_file in rows
    ]


def _load_methods(db: Session, code_file_ids: list[int]) -> list[dict]:
    if not code_file_ids:
        return []

    rows = (
        db.query(CodeMethod, CodeClass)
        .join(CodeClass, CodeMethod.class_id == CodeClass.id)
        .filter(CodeClass.code_file_id.in_(code_file_ids))
        .all()
    )

    return [
        {
            "name": code_method.name,
            "class": code_class.name,
            "return_type": code_method.return_type,
        }
        for code_method, code_class in rows
    ]


def _infer_package(file_path: str) -> str | None:
    normalized = file_path.replace("\\", "/")
    if "/src/" not in normalized:
        return None

    relative_path = normalized.split("/src/", 1)[1]
    if "/" not in relative_path:
        return None

    package_path = relative_path.rsplit("/", 1)[0]
    if not package_path:
        return None

    return package_path.replace("/", ".")


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
