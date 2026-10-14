class AIDataAnalystError(Exception):
    """Base exception for the AI Data Analyst system."""


class UnsupportedFileFormatError(AIDataAnalystError):
    """Raised when an uploaded file is not CSV or Excel."""


class LLMReasoningError(AIDataAnalystError):
    """Raised when Gemini fails to return a valid structured response."""


class SQLValidationError(AIDataAnalystError):
    """Raised when a generated SQL query is unsafe or invalid."""


class PipelineExecutionError(AIDataAnalystError):
    """Raised when an agent fails during workflow execution."""
