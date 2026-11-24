"""
Pydantic schemas for AI-generated workout insights.

- WorkoutStats: locally computed aggregates sent to the AI and returned to the client
- InsightResponse: the API response combining stats with the AI coaching tip
"""

from pydantic import BaseModel


class WorkoutStats(BaseModel):
    """Aggregate statistics computed from a user's workouts."""
    total_workouts: int
    total_minutes: int
    total_calories: int
    workouts_by_type: dict[str, int]


class InsightResponse(BaseModel):
    """Response for the AI insights endpoint."""
    user_id: int
    stats: WorkoutStats
    coaching_tip: str
