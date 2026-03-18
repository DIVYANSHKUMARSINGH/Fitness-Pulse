from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

# Base properties shared across all schemas
class WorkoutBase(BaseModel):
    workout_type: str
    duration: int
    calories: Optional[int] = None
    date: date

# Used when logging a new workout via API
class WorkoutCreate(WorkoutBase):
    pass

# Returned to the client from the API
class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    
    # Crucial: Tells Pydantic it's okay to read from a SQLAlchemy ORM model directly
    model_config = ConfigDict(from_attributes=True)