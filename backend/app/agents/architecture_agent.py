import logging

from app.agents.base_agent import BaseAgent
from app.agents.state import ModernizationState
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ArchitectureUnderstandingAgent(BaseAgent):
    name = "architecture_understanding_agent"

    def __init__(self) -> None:
        self.llm_service = LLMService()

    def execute(self, state: ModernizationState) -> ModernizationState:
        logger.info("Executing %s", self.name)

        context = {
            "classes": state.get("classes", []),
            "methods": state.get("methods", []),
            "dependencies": state.get("dependencies", []),
            "code_analysis": state.get("code_analysis", {}),
            "dependency_analysis": state.get("dependency_analysis", {}),
            "risk_analysis": state.get("risk_analysis", {}),
        }

        try:
            architecture_summary = (
                self.llm_service.generate_architecture_summary(context)
            )
            state["architecture_summary"] = architecture_summary
        except Exception as exc:
            logger.error(
                "%s LLM generation failed: %s", self.name, exc, exc_info=True
            )
            state["architecture_summary"] = {"components": []}

        return state
