"""
Workout SQLAlchemy ORM model.

Defines the 'workouts' table in the database. Each workout is linked to a user
via a foreign key (many-to-one). Tracks workout type, duration in minutes,
optional calories burned, and the date the workout occurred.
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    workout_type = Column(String, index=True, nullable=False)  # e.g., "running", "weightlifting"
    duration = Column(Integer, nullable=False)                 # in minutes
    calories = Column(Integer, nullable=True)                  # optional field
    date = Column(Date, nullable=False)                        # when it happened

    # Links back to the User model
    user = relationship("User", back_populates="workouts")