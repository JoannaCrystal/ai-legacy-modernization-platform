import logging

from app.agents.base_agent import BaseAgent
from app.agents.state import ModernizationState
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class DocumentationAgent(BaseAgent):
    name = "documentation_agent"

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
            "retrieved_context": state.get("retrieved_context", []),
        }

        try:
            architecture_report = (
                self.llm_service.generate_architecture_report(context)
            )
            state["architecture_report"] = architecture_report
        except Exception as exc:
            logger.error(
                "%s LLM generation failed: %s", self.name, exc, exc_info=True
            )
            state["architecture_report"] = {
                "application_overview": "Documentation unavailable",
                "architecture_summary": "",
                "components": [],
                "business_capabilities": [],
                "technology_summary": "",
                "technical_risks": [],
                "modernization_opportunities": [],
            }

        return state
