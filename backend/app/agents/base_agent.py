import logging

from app.agents.state import ModernizationState

pipeline_logger = logging.getLogger("app.agents.pipeline")


class BaseAgent:
    name = "base_agent"
    is_pipeline_final = False

    def _log_pipeline_step(self) -> None:
        if self.is_pipeline_final:
            pipeline_logger.info("%s:", self.__class__.__name__)
        else:
            pipeline_logger.info("%s\n\n↓", self.__class__.__name__)

    def execute(self, state: ModernizationState) -> ModernizationState:
        raise NotImplementedError("Subclasses must implement execute().")
