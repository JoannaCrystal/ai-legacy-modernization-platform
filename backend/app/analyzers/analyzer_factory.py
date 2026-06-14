from app.analyzers.base_analyzer import BaseAnalyzer
from app.analyzers.java_analyzer import JavaAnalyzer


class AnalyzerFactory:
    @staticmethod
    def get_analyzer(language: str) -> BaseAnalyzer:
        normalized_language = language.strip().upper()

        if normalized_language == "JAVA":
            return JavaAnalyzer()

        raise ValueError(f"Unsupported language: {language}")
