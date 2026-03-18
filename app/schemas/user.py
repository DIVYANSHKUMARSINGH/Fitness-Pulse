from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# Base properties shared across all schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

# Properties strictly needed to create a new user via API
class UserCreate(UserBase):
    pass

# Properties returned to the client from the API
class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    # Crucial: Tells Pydantic it's okay to read from a SQLAlchemy ORM model directly
    model_config = ConfigDict(from_attributes=True)