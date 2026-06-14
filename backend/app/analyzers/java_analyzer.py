import re
from typing import Any

from app.analyzers.base_analyzer import BaseAnalyzer

IMPORT_PATTERN = re.compile(
    r"^\s*import\s+(?:static\s+)?([a-zA-Z_][\w.]*(?:\.\*)?)\s*;?",
    re.MULTILINE,
)
CLASS_PATTERN = re.compile(
    r"(?:public\s+|private\s+|protected\s+)?"
    r"(?:abstract\s+|final\s+)?"
    r"class\s+(\w+)",
    re.MULTILINE,
)


class JavaAnalyzer(BaseAnalyzer):
    def analyze(self, content: str) -> dict[str, Any]:
        classes = self._extract_classes(content)
        dependencies = self._extract_imports(content)

        return {
            "classes": classes,
            "methods": [],
            "dependencies": dependencies,
        }

    def _extract_classes(self, content: str) -> list[dict[str, str]]:
        seen: set[str] = set()
        classes: list[dict[str, str]] = []

        for match in CLASS_PATTERN.finditer(content):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            classes.append({"name": name})

        return classes

    def _extract_imports(self, content: str) -> list[dict[str, str]]:
        seen: set[str] = set()
        dependencies: list[dict[str, str]] = []

        for match in IMPORT_PATTERN.finditer(content):
            name = match.group(1)
            if name in seen:
                continue
            seen.add(name)
            dependencies.append({"name": name, "type": "IMPORT"})

        return dependencies
