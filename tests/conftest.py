import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base
from app.core.dependencies import get_db
from app.main import app


# ---------------------------------------------------------------------------
# Test Database Setup
# ---------------------------------------------------------------------------
# Uses a separate in-memory SQLite database so tests never touch production data.
# Each test session gets a fresh database — tables are created once, then
# dropped at the end of the session.
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite:///./test_fitnesspulse.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create all tables at the start of the test session,
    drop them when all tests finish.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session():
    """
    Provide a clean database session for each test.
    Rolls back all changes after each test so tests don't interfere
    with each other.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """
    Provide a TestClient that uses the test database session.
    Overrides the app's get_db dependency so all HTTP requests
    during testing go through the test database, not production.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # session cleanup handled by the db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Sample Data Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_user_data():
    """Return a valid user payload for creating test users."""
    return {"username": "testuser", "email": "test@example.com"}


@pytest.fixture()
def sample_workout_data():
    """Return a valid workout payload for creating test workouts."""
    return {
        "workout_type": "running",
        "duration": 30,
        "calories": 250,
        "date": "2026-04-27"
    }


@pytest.fixture()
def created_user(client, sample_user_data):
    """Create a user via the API and return the response JSON."""
    response = client.post("/api/v1/users", json=sample_user_data)
    return response.json()


@pytest.fixture()
def created_workout(client, created_user, sample_workout_data):
    """Create a workout for the test user and return the response JSON."""
    user_id = created_user["id"]
    response = client.post(f"/api/v1/users/{user_id}/workouts", json=sample_workout_data)
    return response.json()
