"""
Workout Pydantic schemas for request validation and response serialization.

- WorkoutBase: shared fields (workout_type, duration, calories, date)
- WorkoutCreate: used for POST request bodies (inherits WorkoutBase)
- WorkoutResponse: used for API responses — adds id and user_id, configured
  with from_attributes=True so Pydantic can read directly from SQLAlchemy objects
"""

from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class WorkoutBase(BaseModel):
    """Base properties shared across all Workout schemas."""
    workout_type: str
    duration: int
    calories: Optional[int] = None
    date: date


class WorkoutCreate(WorkoutBase):
    """Schema for logging a new workout via the API."""
    pass


class WorkoutResponse(WorkoutBase):
    """Schema for returning workout data in API responses."""
    id: int
    user_id: int

    # Tells Pydantic it's okay to read from a SQLAlchemy ORM model directly
    model_config = ConfigDict(from_attributes=True)