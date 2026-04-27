from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    - **username**: must be unique
    - **email**: must be a valid email and unique
    """
    return user_service.create_user(db=db, user_data=user)


@router.get("/users", response_model=list[UserResponse], tags=["Users"])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users with optional pagination.
    - **skip**: number of records to skip (default: 0)
    - **limit**: max number of records to return (default: 100)
    """
    return user_service.get_users(db=db, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by their ID.
    Returns 404 if the user does not exist.
    """
    return user_service.get_user(db=db, user_id=user_id)


@router.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    """
    Update an existing user's username and email.
    Returns 404 if the user does not exist.
    Returns 409 if the new username/email conflicts with another user.
    """
    return user_service.update_user(db=db, user_id=user_id, user_data=user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user and all their associated workouts.
    Returns 404 if the user does not exist.
    """
    user_service.delete_user(db=db, user_id=user_id)
