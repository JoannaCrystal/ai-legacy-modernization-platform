import logging

from app.agents.base_agent import BaseAgent
from app.agents.state import ModernizationState
from app.database.session import SessionLocal
from app.rag.retriever import KnowledgeRetriever

logger = logging.getLogger(__name__)


class KnowledgeAgent(BaseAgent):
    name = "knowledge_agent"

    def execute(self, state: ModernizationState) -> ModernizationState:
        logger.info("Executing %s", self.name)

        query = self._build_retrieval_query(state)
        retrieved_context: list[str] = []

        db = SessionLocal()
        try:
            retriever = KnowledgeRetriever(db)
            results = retriever.retrieve(query)
            retrieved_context = [result["content"] for result in results]
        except Exception as exc:
            logger.error(
                "%s retrieval failed: %s",
                self.name,
                exc,
                exc_info=True,
            )
        finally:
            db.close()

        state["retrieved_context"] = retrieved_context
        return state

    def _build_retrieval_query(self, state: ModernizationState) -> str:
        dependency_analysis = state.get("dependency_analysis", {})
        risk_analysis = state.get("risk_analysis", {})
        dependencies = state.get("dependencies", [])

        query_parts: list[str] = []

        for dependency in dependencies:
            if not isinstance(dependency, dict):
                query_parts.append(str(dependency))
                continue

            dependency_name = dependency.get("dependency")
            technology = dependency.get("technology")
            if dependency_name:
                query_parts.append(str(dependency_name))
            if technology:
                query_parts.append(str(technology))

        high_risk_dependencies = dependency_analysis.get(
            "high_risk_dependencies",
            [],
        )
        for dependency in high_risk_dependencies:
            if not isinstance(dependency, dict):
                continue

            dependency_name = dependency.get("dependency")
            technology = dependency.get("technology")
            if dependency_name:
                query_parts.append(str(dependency_name))
            if technology:
                query_parts.append(str(technology))

        unique_parts = list(
            dict.fromkeys(part for part in query_parts if part)
        )

        if unique_parts:
            query = f"Modernization guidance for {' '.join(unique_parts)}"
        else:
            query = "Enterprise application modernization guidance"

        overall_risk = risk_analysis.get("overall_risk")
        if overall_risk:
            query = f"{query} risk level {overall_risk}"

        return query
