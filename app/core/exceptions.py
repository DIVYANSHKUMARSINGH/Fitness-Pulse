"""
Custom HTTP exception classes.

Provides semantic exception types that the service layer raises for common
error cases. These inherit from FastAPI's HTTPException so they are
automatically converted into proper JSON error responses with the correct
HTTP status codes.
"""

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """
    Raised when a requested resource does not exist.
    Returns HTTP 404 Not Found.
    """
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AlreadyExistsException(HTTPException):
    """
    Raised when attempting to create a resource that already exists.
    Returns HTTP 409 Conflict.
    """
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class AIServiceUnavailableException(HTTPException):
    """
    Raised when the AI provider is not configured or keeps failing after retries.
    Returns HTTP 503 Service Unavailable.
    """
    def __init__(self, detail: str = "AI service is currently unavailable"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class AIResponseException(HTTPException):
    """
    Raised when the AI provider answers with unusable (empty) content.
    Returns HTTP 502 Bad Gateway.
    """
    def __init__(self, detail: str = "AI service returned an invalid response"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
