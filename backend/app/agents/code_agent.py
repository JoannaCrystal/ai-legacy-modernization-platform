import logging

from app.agents.base_agent import BaseAgent
from app.agents.state import ModernizationState

logger = logging.getLogger(__name__)


class CodeAnalyzerAgent(BaseAgent):
    name = "code_analyzer_agent"

    def execute(self, state: ModernizationState) -> ModernizationState:
        self._log_pipeline_start()
        self._log_pipeline_step()

        classes = state.get("classes", [])
        methods = state.get("methods", [])
        class_count = len(classes)
        method_count = len(methods)

        detected_components = self._extract_class_names(classes)

        state["code_analysis"] = {
            "summary": (
                f"Application contains {class_count} classes "
                f"and {method_count} methods"
            ),
            "detected_components": detected_components,
        }

        return state

    def _extract_class_names(self, classes: list) -> list[str]:
        names: list[str] = []
        for item in classes:
            if isinstance(item, dict):
                names.append(str(item.get("name", item)))
            else:
                names.append(str(item))
        return names
