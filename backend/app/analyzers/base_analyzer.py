from abc import ABC, abstractmethod
from typing import Any


class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, content: str) -> dict[str, Any]:
        pass
