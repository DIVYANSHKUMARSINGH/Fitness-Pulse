from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    Returns a simple status message to confirm the API is running.
    Useful for monitoring tools and CI/CD pipelines.
    """
    return {"status": "healthy"}
