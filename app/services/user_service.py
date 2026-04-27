from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.exceptions import NotFoundException, AlreadyExistsException


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user.
    Raises AlreadyExistsException if username or email is already taken.
    """
    # Check for duplicate username
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise AlreadyExistsException(detail=f"Username '{user_data.username}' is already taken")

    # Check for duplicate email
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise AlreadyExistsException(detail=f"Email '{user_data.email}' is already registered")

    db_user = User(
        username=user_data.username,
        email=user_data.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> User:
    """
    Get a single user by ID.
    Raises NotFoundException if user does not exist.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise NotFoundException(detail=f"User with id {user_id} not found")
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Get a paginated list of all users.
    """
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_data: UserCreate) -> User:
    """
    Update an existing user's username and email.
    Raises NotFoundException if user does not exist.
    Raises AlreadyExistsException if the new username/email conflicts.
    """
    db_user = get_user(db, user_id)  # raises 404 if not found

    # Check for conflicts with OTHER users (not self)
    conflict = db.query(User).filter(
        User.username == user_data.username,
        User.id != user_id
    ).first()
    if conflict:
        raise AlreadyExistsException(detail=f"Username '{user_data.username}' is already taken")

    conflict = db.query(User).filter(
        User.email == user_data.email,
        User.id != user_id
    ).first()
    if conflict:
        raise AlreadyExistsException(detail=f"Email '{user_data.email}' is already registered")

    db_user.username = user_data.username
    db_user.email = user_data.email
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> None:
    """
    Delete a user by ID.
    Raises NotFoundException if user does not exist.
    Cascade deletes all associated workouts.
    """
    db_user = get_user(db, user_id)  # raises 404 if not found
    db.delete(db_user)
    db.commit()
