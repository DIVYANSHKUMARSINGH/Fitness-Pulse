"""
User SQLAlchemy ORM model.

Defines the 'users' table in the database with columns for id, username,
email, and created_at. Has a one-to-many relationship with the Workout model
(one user can have many workouts). Cascade delete ensures that when a user is
removed, all their workouts are automatically deleted.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # One user can have many workouts
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
