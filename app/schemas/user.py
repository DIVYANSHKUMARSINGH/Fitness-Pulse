"""
User Pydantic schemas for request validation and response serialization.

- UserBase: shared fields (username, email)
- UserCreate: used for POST/PUT request bodies (inherits UserBase)
- UserResponse: used for API responses — adds id and created_at, configured
  with from_attributes=True so Pydantic can read directly from SQLAlchemy objects
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    """Base properties shared across all User schemas."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user via the API. Requires username and email."""
    pass


class UserResponse(UserBase):
    """Schema for returning user data in API responses."""
    id: int
    created_at: datetime

    # Tells Pydantic it's okay to read from a SQLAlchemy ORM model directly
    model_config = ConfigDict(from_attributes=True)