import logging

from app.agents.base_agent import BaseAgent
from app.agents.state import ModernizationState

logger = logging.getLogger(__name__)


class DependencyAgent(BaseAgent):
    name = "dependency_agent"

    def execute(self, state: ModernizationState) -> ModernizationState:
        self._log_pipeline_step()

        dependencies = state.get("dependencies", [])
        high_risk_dependencies = [
            dependency
            for dependency in dependencies
            if dependency.get("risk_level") == "HIGH"
        ]

        state["dependency_analysis"] = {
            "total_dependencies": len(dependencies),
            "high_risk_dependencies": high_risk_dependencies,
        }

        return state
