"""
Gemini AI service layer.

Isolates everything about the AI provider behind a small `AIClient` interface so
the rest of the app (and the tests) never touch the real network:

- GeminiClient: real implementation using the google-genai SDK, with retries
  and exponential backoff for transient failures.
- compute_stats / build_prompt: pure functions (easy to unit test).
- get_workout_insights: orchestrates DB data -> stats -> prompt -> AI tip.
"""

import logging
import time
from typing import Callable, Protocol

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AIResponseException, AIServiceUnavailableException
from app.models.workout import Workout
from app.schemas.insight import InsightResponse, WorkoutStats
from app.services.workout_service import get_workouts_by_user

logger = logging.getLogger(__name__)


class AIClient(Protocol):
    """Anything that can turn a prompt into text. Fakes implement this in tests."""

    def generate(self, prompt: str) -> str:
        """Return the model's text response for the prompt."""
        ...


class GeminiClient:
    """Real Gemini client with retry/backoff around the google-genai SDK."""

    def __init__(
        self,
        api_key: str,
        model: str,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """Store configuration. The SDK is imported lazily on first call."""
        self.api_key = api_key
        self.model = model
        self.max_retries = max(1, max_retries)
        self.backoff_seconds = backoff_seconds
        self._sleep = sleep
        self._client = None

    def _get_client(self):
        """Create the SDK client lazily so importing this module needs no SDK/key."""
        if self._client is None:
            from google import genai  # local import: keeps tests/CI independent of network SDK

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate(self, prompt: str) -> str:
        """
        Call Gemini, retrying transient failures with exponential backoff.
        Raises AIServiceUnavailableException if all attempts fail,
        AIResponseException if the model returns empty text.
        """
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._get_client().models.generate_content(
                    model=self.model, contents=prompt
                )
                text = (getattr(response, "text", None) or "").strip()
                if not text:
                    raise AIResponseException("AI returned an empty response")
                return text
            except AIResponseException:
                raise
            except Exception as exc:  # SDK raises many types; treat all as transient
                last_error = exc
                logger.warning("Gemini attempt %d/%d failed: %s", attempt, self.max_retries, exc)
                if attempt < self.max_retries:
                    self._sleep(self.backoff_seconds * (2 ** (attempt - 1)))
        raise AIServiceUnavailableException(
            f"AI service failed after {self.max_retries} attempts"
        ) from last_error


def get_ai_client() -> AIClient:
    """
    FastAPI dependency returning the real Gemini client.
    Raises AIServiceUnavailableException if no API key is configured.
    Tests override this dependency with a fake client.
    """
    if not settings.GEMINI_API_KEY:
        raise AIServiceUnavailableException("GEMINI_API_KEY is not configured")
    return GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
        max_retries=settings.AI_MAX_RETRIES,
        backoff_seconds=settings.AI_RETRY_BACKOFF_SECONDS,
    )


def compute_stats(workouts: list[Workout]) -> WorkoutStats:
    """Aggregate totals and per-type counts from a list of workouts."""
    by_type: dict[str, int] = {}
    for w in workouts:
        by_type[w.workout_type] = by_type.get(w.workout_type, 0) + 1
    return WorkoutStats(
        total_workouts=len(workouts),
        total_minutes=sum(w.duration for w in workouts),
        total_calories=sum(w.calories or 0 for w in workouts),
        workouts_by_type=by_type,
    )


def build_prompt(stats: WorkoutStats) -> str:
    """Build the coaching prompt from aggregated stats (no personal data sent)."""
    types = ", ".join(f"{k} x{v}" for k, v in stats.workouts_by_type.items()) or "none"
    return (
        "You are a concise, encouraging fitness coach. Based on this summary, "
        "give 2-3 sentences of practical coaching advice.\n"
        f"Total workouts: {stats.total_workouts}\n"
        f"Total minutes: {stats.total_minutes}\n"
        f"Total calories burned: {stats.total_calories}\n"
        f"Workout types: {types}"
    )


def get_workout_insights(db: Session, user_id: int, ai_client: AIClient) -> InsightResponse:
    """
    Produce an AI coaching tip for a user.
    Raises NotFoundException if the user does not exist, and AI* exceptions
    if the provider fails.
    """
    workouts = get_workouts_by_user(db, user_id, skip=0, limit=1000)  # 404s if no user
    stats = compute_stats(workouts)
    tip = ai_client.generate(build_prompt(stats))
    return InsightResponse(user_id=user_id, stats=stats, coaching_tip=tip)
