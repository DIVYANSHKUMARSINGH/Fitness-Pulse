from sqlalchemy.orm import Session
from app.models.workout import Workout
from app.schemas.workout import WorkoutCreate
from app.services.user_service import get_user
from app.core.exceptions import NotFoundException


def create_workout(db: Session, user_id: int, workout_data: WorkoutCreate) -> Workout:
    """
    Log a new workout for a user.
    Raises NotFoundException if the user does not exist.
    """
    # Verify the user exists before creating the workout
    get_user(db, user_id)  # raises 404 if not found

    db_workout = Workout(
        user_id=user_id,
        workout_type=workout_data.workout_type,
        duration=workout_data.duration,
        calories=workout_data.calories,
        date=workout_data.date
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


def get_workouts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Workout]:
    """
    Get all workouts for a specific user, with pagination.
    Raises NotFoundException if the user does not exist.
    """
    get_user(db, user_id)  # raises 404 if not found
    return db.query(Workout).filter(
        Workout.user_id == user_id
    ).offset(skip).limit(limit).all()


def get_workout(db: Session, workout_id: int) -> Workout:
    """
    Get a single workout by its ID.
    Raises NotFoundException if workout does not exist.
    """
    db_workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not db_workout:
        raise NotFoundException(detail=f"Workout with id {workout_id} not found")
    return db_workout


def delete_workout(db: Session, workout_id: int) -> None:
    """
    Delete a workout by its ID.
    Raises NotFoundException if workout does not exist.
    """
    db_workout = get_workout(db, workout_id)  # raises 404 if not found
    db.delete(db_workout)
    db.commit()
