import logging

from app.agents.base_agent import BaseAgent
from app.agents.state import ModernizationState
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ModernizationAgent(BaseAgent):
    name = "modernization_agent"
    is_pipeline_final = True

    def __init__(self) -> None:
        self.llm_service = LLMService()

    def execute(self, state: ModernizationState) -> ModernizationState:
        self._log_pipeline_step()

        code_analysis = state.get("code_analysis", {})
        dependency_analysis = state.get("dependency_analysis", {})
        risk_analysis = state.get("risk_analysis", {})
        architecture_summary = state.get("architecture_summary", {})
        business_capabilities = state.get("business_capabilities", {})
        architecture_report = state.get("architecture_report", {})
        dependencies = state.get("dependencies", [])
        retrieved_context = state.get("retrieved_context", [])

        if not code_analysis or not dependency_analysis or not risk_analysis:
            logger.warning(
                "%s invoked with incomplete upstream analysis", self.name
            )

        context = {
            "code_analysis": code_analysis,
            "dependency_analysis": dependency_analysis,
            "risk_analysis": risk_analysis,
            "architecture_summary": architecture_summary,
            "business_capabilities": business_capabilities,
            "architecture_report": architecture_report,
            "dependencies": dependencies,
            "retrieved_context": retrieved_context,
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
