class AppError(Exception):
    """Base application exception with HTTP mapping metadata."""

    error_code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ProjectNotFoundError(AppError):
    error_code = "PROJECT_NOT_FOUND"
    status_code = 404

    def __init__(self, message: str = "Project not found") -> None:
        super().__init__(message)


class AnalysisNotFoundError(AppError):
    error_code = "ANALYSIS_NOT_FOUND"
    status_code = 404

    def __init__(
        self,
        message: str = "Completed analysis not found for this project",
    ) -> None:
        super().__init__(message)


class ReportNotFoundError(AppError):
    error_code = "REPORT_NOT_FOUND"
    status_code = 404

    def __init__(self, message: str = "Report not found") -> None:
        super().__init__(message)


class UploadValidationError(AppError):
    error_code = "UPLOAD_VALIDATION_ERROR"
    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)


class EmbeddingGenerationError(AppError):
    error_code = "EMBEDDING_GENERATION_ERROR"
    status_code = 503

    def __init__(self, message: str = "Failed to generate embedding") -> None:
        super().__init__(message)


class LLMServiceError(AppError):
    error_code = "LLM_SERVICE_ERROR"
    status_code = 502

    def __init__(self, message: str = "LLM service request failed") -> None:
        super().__init__(message)


class ConfigurationError(AppError):
    error_code = "CONFIGURATION_ERROR"
    status_code = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
