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

    # Links back to the User model above
    user = relationship("User", back_populates="workouts")