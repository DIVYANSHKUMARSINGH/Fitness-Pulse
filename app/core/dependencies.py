from app.core.database import SessionLocal

def get_db():
    """
    Dependency that provides a database session per request.
    The session is automatically closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()