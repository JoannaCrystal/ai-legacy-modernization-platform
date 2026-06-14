from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.code_analysis import CodeDependency
from app.models.code_file import CodeFile


@dataclass(frozen=True)
class DependencyRule:
    patterns: tuple[str, ...]
    technology: str
    category: str
    risk_level: str
    recommendation: str


DEPENDENCY_RULES: tuple[DependencyRule, ...] = (
    DependencyRule(
        patterns=("javax.xml.soap", "javax.jws", "wsdl"),
        technology="SOAP",
        category="Integration",
        risk_level="HIGH",
        recommendation=(
            "Consider migrating SOAP services to REST or event-driven APIs"
        ),
    ),
    DependencyRule(
        patterns=("java.sql", "JdbcTemplate"),
        technology="Direct Database Access",
        category="Database",
        risk_level="MEDIUM",
        recommendation="Introduce repository abstraction or ORM layer",
    ),
    DependencyRule(
        patterns=("org.springframework",),
        technology="Spring Framework",
        category="Framework",
        risk_level="LOW",
        recommendation="Validate Spring version and upgrade if outdated",
    ),
    DependencyRule(
        patterns=("org.apache.log4j",),
        technology="Log4j",
        category="Logging",
        risk_level="HIGH",
        recommendation=(
            "Review version and migrate to supported logging framework"
        ),
    ),
    DependencyRule(
        patterns=("com.ibm.mq",),
        technology="IBM MQ",
        category="Messaging",
        risk_level="MEDIUM",
        recommendation="Evaluate migration to cloud-native messaging services",
    ),
)

UNKNOWN_DEPENDENCY = {
    "technology": "Unknown",
    "category": "Unknown",
    "risk_level": "UNKNOWN",
    "recommendation": "Manual review required",
}


class DependencyIntelligenceService:
    def analyze_dependency(self, dependency_name: str) -> dict[str, str]:
        rule = self._match_rule(dependency_name)
        if rule is None:
            return {
                "dependency": dependency_name,
                **UNKNOWN_DEPENDENCY,
            }

        return {
            "dependency": dependency_name,
            "technology": rule.technology,
            "category": rule.category,
            "risk_level": rule.risk_level,
            "recommendation": rule.recommendation,
        }

    def analyze_project_dependencies(
        self,
        db: Session,
        project_id: int,
    ) -> list[dict[str, str]]:
        dependencies = (
            db.query(CodeDependency)
            .join(CodeFile, CodeDependency.code_file_id == CodeFile.id)
            .filter(CodeFile.project_id == project_id)
            .all()
        )

        seen: set[str] = set()
        results: list[dict[str, str]] = []

        for dependency in dependencies:
            if dependency.dependency_name in seen:
                continue
            seen.add(dependency.dependency_name)
            results.append(self.analyze_dependency(dependency.dependency_name))

        return results

    def _match_rule(self, dependency_name: str) -> DependencyRule | None:
        for rule in DEPENDENCY_RULES:
            if any(pattern in dependency_name for pattern in rule.patterns):
                return rule
        return None
