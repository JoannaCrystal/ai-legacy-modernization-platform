import logging

from app.agents.base_agent import BaseAgent
from app.agents.state import ModernizationState

logger = logging.getLogger(__name__)


class RiskAgent(BaseAgent):
    name = "risk_agent"

    def execute(self, state: ModernizationState) -> ModernizationState:
        self._log_pipeline_step()

        dependency_analysis = state.get("dependency_analysis", {})
        high_risk_dependencies = dependency_analysis.get(
            "high_risk_dependencies", []
        )

        if high_risk_dependencies:
            overall_risk = "HIGH"
            reason = (
                f"Found {len(high_risk_dependencies)} high-risk "
                "dependencies requiring attention"
            )
        else:
            overall_risk = "LOW"
            reason = "No high-risk dependencies detected"

        state["risk_analysis"] = {
            "overall_risk": overall_risk,
            "reason": reason,
        }

        return state
