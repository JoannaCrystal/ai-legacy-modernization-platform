import logging

from app.agents.base_agent import BaseAgent
from app.agents.state import ModernizationState
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ModernizationAgent(BaseAgent):
    name = "modernization_agent"

    def __init__(self) -> None:
        self.llm_service = LLMService()

    def execute(self, state: ModernizationState) -> ModernizationState:
        logger.info("Executing %s", self.name)

        code_analysis = state.get("code_analysis", {})
        dependency_analysis = state.get("dependency_analysis", {})
        risk_analysis = state.get("risk_analysis", {})
        dependencies = state.get("dependencies", [])

        if not code_analysis or not dependency_analysis or not risk_analysis:
            logger.warning(
                "%s invoked with incomplete upstream analysis", self.name
            )

        context = {
            "code_analysis": code_analysis,
            "dependency_analysis": dependency_analysis,
            "risk_analysis": risk_analysis,
            "dependencies": dependencies,
        }

        try:
            llm_response = self.llm_service.generate_modernization_strategy(
                context
            )
            state["modernization_plan"] = llm_response
        except Exception as exc:
            logger.error(
                "%s LLM generation failed: %s", self.name, exc, exc_info=True
            )
            state["modernization_plan"] = {
                "summary": "LLM unavailable",
                "recommendations": [
                    "Manual modernization review required",
                ],
            }

        return state
