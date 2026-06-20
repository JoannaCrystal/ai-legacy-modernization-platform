from app.agents.state import ModernizationState


class BaseAgent:
    name = "base_agent"

    def execute(self, state: ModernizationState) -> ModernizationState:
        raise NotImplementedError("Subclasses must implement execute().")
