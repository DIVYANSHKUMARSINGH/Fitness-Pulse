import pytest
from app.services.user_service import create_user, get_user, get_users, update_user, delete_user
from app.schemas.user import UserCreate
from app.core.exceptions import NotFoundException, AlreadyExistsException


class TestCreateUser:
    """Tests for the create_user service function."""

    def test_create_user_success(self, db_session):
        """Creating a user with valid data returns a User with an ID."""
        user_data = UserCreate(username="alice", email="alice@example.com")
        user = create_user(db=db_session, user_data=user_data)

        assert user.id is not None
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.created_at is not None

    def test_create_user_duplicate_username(self, db_session):
        """Creating a user with an existing username raises 409."""
        user_data = UserCreate(username="bob", email="bob@example.com")
        create_user(db=db_session, user_data=user_data)

        duplicate = UserCreate(username="bob", email="different@example.com")
        with pytest.raises(AlreadyExistsException):
            create_user(db=db_session, user_data=duplicate)

    def test_create_user_duplicate_email(self, db_session):
        """Creating a user with an existing email raises 409."""
        user_data = UserCreate(username="charlie", email="charlie@example.com")
        create_user(db=db_session, user_data=user_data)

        duplicate = UserCreate(username="different_user", email="charlie@example.com")
        with pytest.raises(AlreadyExistsException):
            create_user(db=db_session, user_data=duplicate)


class TestGetUser:
    """Tests for the get_user service function."""

    def test_get_user_success(self, db_session):
        """Getting an existing user by ID returns the correct user."""
        user_data = UserCreate(username="diana", email="diana@example.com")
        created = create_user(db=db_session, user_data=user_data)

        fetched = get_user(db=db_session, user_id=created.id)
        assert fetched.id == created.id
        assert fetched.username == "diana"

    def test_get_user_not_found(self, db_session):
        """Getting a non-existent user raises 404."""
        with pytest.raises(NotFoundException):
            get_user(db=db_session, user_id=99999)


class TestGetUsers:
    """Tests for the get_users service function."""

    def test_get_users_returns_list(self, db_session):
        """get_users returns a list (possibly empty)."""
        users = get_users(db=db_session)
        assert isinstance(users, list)

    def test_get_users_pagination(self, db_session):
        """Pagination parameters (skip, limit) work correctly."""
        # Create 3 users
        for i in range(3):
            create_user(db=db_session, user_data=UserCreate(
                username=f"page_user_{i}", email=f"page{i}@example.com"
            ))

        # Fetch with limit=2 → should return at most 2
        result = get_users(db=db_session, skip=0, limit=2)
        assert len(result) <= 2


class TestUpdateUser:
    """Tests for the update_user service function."""

    def test_update_user_success(self, db_session):
        """Updating a user's username and email works."""
        user_data = UserCreate(username="eve", email="eve@example.com")
        created = create_user(db=db_session, user_data=user_data)

        updated_data = UserCreate(username="eve_updated", email="eve_new@example.com")
        updated = update_user(db=db_session, user_id=created.id, user_data=updated_data)

        assert updated.username == "eve_updated"
        assert updated.email == "eve_new@example.com"

    def test_update_user_not_found(self, db_session):
        """Updating a non-existent user raises 404."""
        update_data = UserCreate(username="ghost", email="ghost@example.com")
        with pytest.raises(NotFoundException):
            update_user(db=db_session, user_id=99999, user_data=update_data)

    def test_update_user_conflict(self, db_session):
        """Updating to a username that belongs to another user raises 409."""
        user_a = create_user(db=db_session, user_data=UserCreate(
            username="frank", email="frank@example.com"
        ))
        user_b = create_user(db=db_session, user_data=UserCreate(
            username="grace", email="grace@example.com"
        ))

        # Try to give user_b the same username as user_a
        with pytest.raises(AlreadyExistsException):
            update_user(db=db_session, user_id=user_b.id, user_data=UserCreate(
                username="frank", email="grace@example.com"
            ))


class TestDeleteUser:
    """Tests for the delete_user service function."""

    def test_delete_user_success(self, db_session):
        """Deleting an existing user succeeds, and they can't be fetched afterwards."""
        user_data = UserCreate(username="henry", email="henry@example.com")
        created = create_user(db=db_session, user_data=user_data)

        delete_user(db=db_session, user_id=created.id)

        with pytest.raises(NotFoundException):
            get_user(db=db_session, user_id=created.id)

    def test_delete_user_not_found(self, db_session):
        """Deleting a non-existent user raises 404."""
        with pytest.raises(NotFoundException):
            delete_user(db=db_session, user_id=99999)
