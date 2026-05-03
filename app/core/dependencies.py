"""
FastAPI dependency providers.

Contains yield-based dependencies that FastAPI injects into route handlers
via the Depends() mechanism. The get_db dependency provides a database session
per request and guarantees cleanup (session.close()) even if the request fails.
"""

from app.core.database import SessionLocal


def get_db():
    """
    Dependency that provides a database session per request.
    The session is automatically closed after the request completes.

    Usage in routes:
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()