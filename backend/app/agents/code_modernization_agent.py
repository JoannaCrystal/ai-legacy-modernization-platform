import logging

from app.agents.base_agent import BaseAgent
from app.agents.state import ModernizationState
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class CodeModernizationAgent(BaseAgent):
    name = "code_modernization_agent"

    def __init__(self) -> None:
        self.llm_service = LLMService()

    def execute(self, state: ModernizationState) -> ModernizationState:
        self._log_pipeline_step()

        context = {
            "code_analysis": state.get("code_analysis", {}),
            "dependency_analysis": state.get("dependency_analysis", {}),
            "risk_analysis": state.get("risk_analysis", {}),
            "architecture_summary": state.get("architecture_summary", {}),
            "business_capabilities": state.get("business_capabilities", {}),
            "architecture_report": state.get("architecture_report", {}),
            "modernization_plan": state.get("modernization_plan", {}),
            "retrieved_context": state.get("retrieved_context", []),
        }

        try:
            code_modernization = self.llm_service.generate_code_modernization(
                context
            )
            state["code_modernization"] = code_modernization
        except Exception as exc:
            logger.error(
                "%s LLM generation failed: %s", self.name, exc, exc_info=True
            )
            state["code_modernization"] = {"opportunities": []}

        self._log_pipeline_end()

        return state
