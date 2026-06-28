import logging

from app.agents.state import ModernizationState

pipeline_logger = logging.getLogger("app.agents.pipeline")


class BaseAgent:
    name = "base_agent"

    def _log_pipeline_start(self) -> None:
        pipeline_logger.info("START\n\n↓")

    def _log_pipeline_step(self) -> None:
        pipeline_logger.info("%s\n\n↓", self.__class__.__name__)

    def _log_pipeline_end(self) -> None:
        pipeline_logger.info("END")

    def execute(self, state: ModernizationState) -> ModernizationState:
        raise NotImplementedError("Subclasses must implement execute().")
