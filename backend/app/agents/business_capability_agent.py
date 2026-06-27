import logging

from app.agents.base_agent import BaseAgent
from app.agents.state import ModernizationState
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class BusinessCapabilityAgent(BaseAgent):
    name = "business_capability_agent"

    def __init__(self) -> None:
        self.llm_service = LLMService()

    def execute(self, state: ModernizationState) -> ModernizationState:
        self._log_pipeline_step()

        context = {
            "architecture_summary": state.get("architecture_summary", {}),
            "code_analysis": state.get("code_analysis", {}),
            "dependency_analysis": state.get("dependency_analysis", {}),
        }

        try:
            business_capabilities = (
                self.llm_service.generate_business_capabilities(context)
            )
            state["business_capabilities"] = business_capabilities
        except Exception as exc:
            logger.error(
                "%s LLM generation failed: %s", self.name, exc, exc_info=True
            )
            state["business_capabilities"] = {"capabilities": []}

        return state
