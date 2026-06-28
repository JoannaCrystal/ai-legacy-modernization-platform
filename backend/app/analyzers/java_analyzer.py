import re
from typing import Any

from app.analyzers.base_analyzer import BaseAnalyzer

IMPORT_PATTERN = re.compile(
    r"^\s*import\s+(?:static\s+)?([a-zA-Z_][\w.]*(?:\.\*)?)\s*;?",
    re.MULTILINE,
)
CLASS_PATTERN = re.compile(
    r"^\s*"
    r"(?:(?:@\w+(?:\([^)]*\))?\s*)*)"
    r"(?:(?:public|private|protected)\s+)?"
    r"(?:(?:abstract|final)\s+)*"
    r"class\s+(\w+)",
    re.MULTILINE,
)
METHOD_PATTERN = re.compile(
    r"(?<![\w.])"
    r"(?!if\s*\(|for\s*\(|while\s*\(|switch\s*\(|catch\s*\()"
    r"(?:(?:@\w+(?:\([^)]*\))?\s*)*)"
    r"(?:(?:public|private|protected)\s+)?"
    r"(?:(?:static|final|synchronized|native|abstract|strictfp)\s+)*"
    r"(?P<return_type>void|[\w<>,\[\]?\.]+(?:\s*\[\s*\])*)"
    r"\s+(?P<name>\w+)\s*"
    r"\((?P<parameters>[^)]*)\)"
    r"(?:\s*throws\s+[\w.\s,]+)?"
    r"\s*(?:\{|;)",
    re.MULTILINE,
)

INVALID_IDENTIFIERS = {
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "return",
    "throw",
    "new",
    "else",
    "do",
    "try",
    "finally",
    "class",
    "interface",
    "enum",
    "import",
    "package",
    "super",
    "this",
    "case",
    "default",
    "break",
    "continue",
}

ACCESS_MODIFIERS = {"public", "private", "protected"}


class JavaAnalyzer(BaseAnalyzer):
    def analyze(self, content: str) -> dict[str, Any]:
        classes = self._extract_classes(content)
        methods = self._extract_methods(content, classes)
        dependencies = self._extract_dependencies(content)

        return {
            "classes": classes,
            "methods": methods,
            "dependencies": dependencies,
        }

    def _extract_classes(self, content: str) -> list[dict[str, str | int]]:
        seen: set[str] = set()
        classes: list[dict[str, str | int]] = []

        for match in CLASS_PATTERN.finditer(content):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            classes.append(
                {
                    "name": name,
                    "start_line": self._line_number(content, match.start()),
                }
            )

        return classes

    def _extract_methods(
        self,
        content: str,
        classes: list[dict[str, str | int]],
    ) -> list[dict[str, str | int]]:
        methods: list[dict[str, str | int]] = []
        seen: set[tuple[str | None, str, str, int]] = set()

        for match in METHOD_PATTERN.finditer(content):
            return_type = match.group("return_type").strip()
            name = match.group("name").strip()
            parameters = match.group("parameters").strip()
            start_line = self._line_number(content, match.start())
            class_name = self._find_containing_class(classes, start_line)

            if (
                return_type in INVALID_IDENTIFIERS
                or return_type in ACCESS_MODIFIERS
                or name in INVALID_IDENTIFIERS
                or self._is_constructor(name, class_name)
            ):
                continue

            dedupe_key = (class_name, name, parameters, start_line)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            methods.append(
                {
                    "name": name,
                    "return_type": return_type,
                    "parameters": parameters,
                    "class_name": class_name,
                    "start_line": start_line,
                }
            )

        return methods

    def _find_containing_class(
        self,
        classes: list[dict[str, str | int]],
        line: int,
    ) -> str | None:
        containing: dict[str, str | int] | None = None

        for cls in classes:
            cls_line = int(cls["start_line"])
            if cls_line <= line and (
                containing is None or cls_line > int(containing["start_line"])
            ):
                containing = cls

        if containing is None:
            return None
        return str(containing["name"])

    def _is_constructor(self, name: str, class_name: str | None) -> bool:
        return class_name is not None and name == class_name

    def _extract_dependencies(self, content: str) -> list[dict[str, str]]:
        seen: set[str] = set()
        dependencies: list[dict[str, str]] = []

        for match in IMPORT_PATTERN.finditer(content):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            dependencies.append({"name": name, "type": "IMPORT"})

        return dependencies

    def _line_number(self, content: str, index: int) -> int:
        return content.count("\n", 0, index) + 1
