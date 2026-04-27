from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.workout import WorkoutCreate, WorkoutResponse
from app.services import workout_service

router = APIRouter()


@router.post("/users/{user_id}/workouts", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED, tags=["Workouts"])
def create_workout(user_id: int, workout: WorkoutCreate, db: Session = Depends(get_db)):
    """
    Log a new workout for a specific user.
    - **workout_type**: e.g., "running", "weightlifting", "yoga"
    - **duration**: in minutes
    - **calories**: optional, estimated calories burned
    - **date**: when the workout occurred (YYYY-MM-DD)
    
    Returns 404 if the user does not exist.
    """
    return workout_service.create_workout(db=db, user_id=user_id, workout_data=workout)


@router.get("/users/{user_id}/workouts", response_model=list[WorkoutResponse], tags=["Workouts"])
def list_user_workouts(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all workouts for a specific user with optional pagination.
    Returns 404 if the user does not exist.
    """
    return workout_service.get_workouts_by_user(db=db, user_id=user_id, skip=skip, limit=limit)


@router.get("/workouts/{workout_id}", response_model=WorkoutResponse, tags=["Workouts"])
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    """
    Get a specific workout by its ID.
    Returns 404 if the workout does not exist.
    """
    return workout_service.get_workout(db=db, workout_id=workout_id)


@router.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Workouts"])
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific workout.
    Returns 404 if the workout does not exist.
    """
    workout_service.delete_workout(db=db, workout_id=workout_id)
