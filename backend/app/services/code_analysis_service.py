from sqlalchemy.orm import Session

from app.analyzers.analyzer_factory import AnalyzerFactory
from app.models.code_analysis import CodeClass, CodeDependency, CodeMethod
from app.models.code_file import CodeFile


def analyze_code_file(db: Session, code_file: CodeFile) -> None:
    if not code_file.language or not code_file.content:
        return

    try:
        analyzer = AnalyzerFactory.get_analyzer(code_file.language)
    except ValueError:
        return

    analysis_result = analyzer.analyze(code_file.content)
    code_classes = _persist_classes(
        db, code_file, analysis_result.get("classes", [])
    )
    _persist_methods(db, code_classes, analysis_result.get("methods", []))
    _persist_dependencies(
        db, code_file, analysis_result.get("dependencies", [])
    )


def _persist_classes(
    db: Session,
    code_file: CodeFile,
    classes: list[dict[str, object]],
) -> list[CodeClass]:
    code_classes: list[CodeClass] = []

    for class_data in classes:
        code_class = CodeClass(
            code_file_id=code_file.id,
            name=str(class_data["name"]),
            start_line=_optional_int(class_data.get("start_line")),
            end_line=_optional_int(class_data.get("end_line")),
        )
        db.add(code_class)
        code_classes.append(code_class)

    if code_classes:
        db.flush()

    return code_classes


def _persist_methods(
    db: Session,
    code_classes: list[CodeClass],
    methods: list[dict[str, object]],
) -> None:
    if not code_classes or not methods:
        return

    class_id_by_name = {
        code_class.name: code_class.id for code_class in code_classes
    }
    default_class_id = code_classes[0].id

    for method_data in methods:
        class_name = method_data.get("class_name")
        class_id = (
            class_id_by_name.get(str(class_name), default_class_id)
            if class_name
            else default_class_id
        )
        db.add(
            CodeMethod(
                class_id=class_id,
                name=str(method_data["name"]),
                return_type=_optional_str(method_data.get("return_type")),
                parameters=_optional_str(method_data.get("parameters")),
                start_line=_optional_int(method_data.get("start_line")),
                end_line=_optional_int(method_data.get("end_line")),
            )
        )


def _persist_dependencies(
    db: Session,
    code_file: CodeFile,
    dependencies: list[dict[str, object]],
) -> None:
    for dependency_data in dependencies:
        db.add(
            CodeDependency(
                code_file_id=code_file.id,
                dependency_name=str(dependency_data["name"]),
                dependency_type=_optional_str(dependency_data.get("type")),
            )
        )


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(value)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
