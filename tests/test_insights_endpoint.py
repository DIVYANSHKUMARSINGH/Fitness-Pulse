"""Integration tests for GET /api/v1/users/{id}/insights with a faked AI client."""

import pytest

from app.core.exceptions import AIResponseException, AIServiceUnavailableException
from app.main import app
from app.services.gemini_service import get_ai_client


class StubAI:
    """AI client stub that returns text or raises a configured exception."""

    def __init__(self, result="Nice work!"):
        self.result = result

    def generate(self, prompt: str) -> str:
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


@pytest.fixture()
def use_ai(client):
    """Return a helper that installs a stub AI client for the current test."""
    def _install(result="Nice work!"):
        app.dependency_overrides[get_ai_client] = lambda: StubAI(result)
    return _install


def test_insights_success(client, use_ai, created_user, sample_workout_data):
    uid = created_user["id"]
    client.post(f"/api/v1/users/{uid}/workouts", json=sample_workout_data)
    use_ai("Add strength training.")

    r = client.get(f"/api/v1/users/{uid}/insights")

    assert r.status_code == 200
    body = r.json()
    assert body["coaching_tip"] == "Add strength training."
    assert body["stats"]["total_workouts"] == 1
    assert body["stats"]["workouts_by_type"] == {"running": 1}


def test_insights_user_not_found(client, use_ai):
    use_ai()
    assert client.get("/api/v1/users/9999/insights").status_code == 404


@pytest.mark.parametrize(
    "error, status",
    [
        (AIServiceUnavailableException(), 503),
        (AIResponseException(), 502),
    ],
)
def test_insights_ai_failures_map_to_http_errors(client, use_ai, created_user, error, status):
    use_ai(error)
    assert client.get(f"/api/v1/users/{created_user['id']}/insights").status_code == status


def test_insights_without_api_key_returns_503(client, created_user, monkeypatch):
    from app.services import gemini_service
    monkeypatch.setattr(gemini_service.settings, "GEMINI_API_KEY", "")
    r = client.get(f"/api/v1/users/{created_user['id']}/insights")
    assert r.status_code == 503
