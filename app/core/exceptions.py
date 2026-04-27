from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """
    Raised when a requested resource does not exist.
    Returns HTTP 404.
    """
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AlreadyExistsException(HTTPException):
    """
    Raised when attempting to create a resource that already exists.
    Returns HTTP 409.
    """
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
