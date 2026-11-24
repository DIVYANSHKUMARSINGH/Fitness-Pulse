"""
AI insights API endpoint.

GET /api/v1/users/{user_id}/insights returns workout stats plus a Gemini-generated
coaching tip. The AI client is injected so tests can substitute a fake.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.insight import InsightResponse
from app.services import gemini_service
from app.services.gemini_service import AIClient, get_ai_client

router = APIRouter()


@router.get("/users/{user_id}/insights", response_model=InsightResponse, tags=["AI"])
def get_insights(
    user_id: int,
    db: Session = Depends(get_db),
    ai_client: AIClient = Depends(get_ai_client),
):
    """
    Get AI coaching insights for a user.
    Returns 404 if the user does not exist, 502 on an invalid AI response,
    503 if the AI service is unconfigured or unavailable.
    """
    return gemini_service.get_workout_insights(db=db, user_id=user_id, ai_client=ai_client)
