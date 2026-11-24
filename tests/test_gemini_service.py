"""Unit tests for the Gemini service layer — no network, everything faked."""

from datetime import date
from types import SimpleNamespace

import pytest

from app.core.exceptions import (
    AIResponseException,
    AIServiceUnavailableException,
    NotFoundException,
)
from app.schemas.user import UserCreate
from app.schemas.workout import WorkoutCreate
from app.services import gemini_service
from app.services.gemini_service import GeminiClient, build_prompt, compute_stats
from app.services.user_service import create_user
from app.services.workout_service import create_workout


class FakeAI:
    """Fake AIClient that records prompts and returns a canned tip."""

    def __init__(self, tip: str = "Keep it up!"):
        self.tip = tip
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.tip


class FakeModels:
    """Fake `client.models` that plays back a scripted list of results/errors."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

    def generate_content(self, model, contents):
        self.calls += 1
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return SimpleNamespace(text=item)


def make_client(script, retries=3):
    """Build a GeminiClient wired to a fake SDK client and a no-op sleep."""
    sleeps: list[float] = []
    client = GeminiClient("key", "model", max_retries=retries, backoff_seconds=1.0, sleep=sleeps.append)
    models = FakeModels(script)
    client._client = SimpleNamespace(models=models)
    return client, models, sleeps


class TestComputeStats:
    @pytest.mark.parametrize(
        "rows, workouts, minutes, calories, types",
        [
            ([], 0, 0, 0, {}),
            ([("running", 30, 250)], 1, 30, 250, {"running": 1}),
            ([("running", 30, None), ("yoga", 60, 100), ("running", 20, 150)], 3, 110, 250, {"running": 2, "yoga": 1}),
        ],
    )
    def test_compute_stats(self, rows, workouts, minutes, calories, types):
        ws = [SimpleNamespace(workout_type=t, duration=d, calories=c) for t, d, c in rows]
        stats = compute_stats(ws)
        assert stats.total_workouts == workouts
        assert stats.total_minutes == minutes
        assert stats.total_calories == calories
        assert stats.workouts_by_type == types


class TestBuildPrompt:
    def test_prompt_contains_stats(self):
        stats = compute_stats([SimpleNamespace(workout_type="running", duration=30, calories=250)])
        prompt = build_prompt(stats)
        assert "Total workouts: 1" in prompt
        assert "running x1" in prompt

    def test_prompt_with_no_workouts(self):
        assert "Workout types: none" in build_prompt(compute_stats([]))


class TestGeminiClient:
    def test_success_first_try(self):
        client, models, sleeps = make_client(["  Great job  "])
        assert client.generate("hi") == "Great job"
        assert models.calls == 1 and sleeps == []

    def test_retries_then_succeeds_with_backoff(self):
        client, models, sleeps = make_client([RuntimeError("x"), RuntimeError("y"), "ok"])
        assert client.generate("hi") == "ok"
        assert models.calls == 3
        assert sleeps == [1.0, 2.0]

    def test_all_attempts_fail_raises_503(self):
        client, models, _ = make_client([RuntimeError("x")] * 3)
        with pytest.raises(AIServiceUnavailableException) as exc:
            client.generate("hi")
        assert exc.value.status_code == 503
        assert models.calls == 3

    @pytest.mark.parametrize("bad", ["", "   ", None])
    def test_empty_response_raises_502_without_retry(self, bad):
        client, models, _ = make_client([bad])
        with pytest.raises(AIResponseException) as exc:
            client.generate("hi")
        assert exc.value.status_code == 502
        assert models.calls == 1


class TestGetAIClient:
    def test_missing_key_raises_503(self, monkeypatch):
        monkeypatch.setattr(gemini_service.settings, "GEMINI_API_KEY", "")
        with pytest.raises(AIServiceUnavailableException):
            gemini_service.get_ai_client()

    def test_with_key_returns_gemini_client(self, monkeypatch):
        monkeypatch.setattr(gemini_service.settings, "GEMINI_API_KEY", "abc")
        assert isinstance(gemini_service.get_ai_client(), GeminiClient)


class TestGetWorkoutInsights:
    def test_returns_tip_and_stats(self, db_session):
        user = create_user(db_session, UserCreate(username="ai_user", email="ai@example.com"))
        create_workout(db_session, user.id, WorkoutCreate(workout_type="running", duration=30, calories=250, date=date(2026, 4, 27)))
        fake = FakeAI("Add a rest day.")

        result = gemini_service.get_workout_insights(db_session, user.id, fake)

        assert result.coaching_tip == "Add a rest day."
        assert result.stats.total_workouts == 1
        assert len(fake.prompts) == 1

    def test_unknown_user_raises_404_and_skips_ai(self, db_session):
        fake = FakeAI()
        with pytest.raises(NotFoundException):
            gemini_service.get_workout_insights(db_session, 9999, fake)
        assert fake.prompts == []
