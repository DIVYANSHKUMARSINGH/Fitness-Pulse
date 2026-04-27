import pytest
from datetime import date
from app.services.workout_service import create_workout, get_workouts_by_user, get_workout, delete_workout
from app.services.user_service import create_user
from app.schemas.user import UserCreate
from app.schemas.workout import WorkoutCreate
from app.core.exceptions import NotFoundException


@pytest.fixture()
def test_user(db_session):
    """Create a user in the test DB that workouts can be attached to."""
    user_data = UserCreate(username="workout_tester", email="workout_tester@example.com")
    return create_user(db=db_session, user_data=user_data)


class TestCreateWorkout:
    """Tests for the create_workout service function."""

    def test_create_workout_success(self, db_session, test_user):
        """Creating a workout for an existing user succeeds."""
        workout_data = WorkoutCreate(
            workout_type="running", duration=30, calories=250, date=date(2026, 4, 27)
        )
        workout = create_workout(db=db_session, user_id=test_user.id, workout_data=workout_data)

        assert workout.id is not None
        assert workout.user_id == test_user.id
        assert workout.workout_type == "running"
        assert workout.duration == 30
        assert workout.calories == 250

    def test_create_workout_no_calories(self, db_session, test_user):
        """Creating a workout without calories (optional field) succeeds."""
        workout_data = WorkoutCreate(
            workout_type="yoga", duration=60, date=date(2026, 4, 27)
        )
        workout = create_workout(db=db_session, user_id=test_user.id, workout_data=workout_data)

        assert workout.calories is None

    def test_create_workout_user_not_found(self, db_session):
        """Creating a workout for a non-existent user raises 404."""
        workout_data = WorkoutCreate(
            workout_type="running", duration=30, calories=200, date=date(2026, 4, 27)
        )
        with pytest.raises(NotFoundException):
            create_workout(db=db_session, user_id=99999, workout_data=workout_data)


class TestGetWorkoutsByUser:
    """Tests for the get_workouts_by_user service function."""

    def test_get_workouts_by_user_success(self, db_session, test_user):
        """Listing workouts for a user returns the correct workouts."""
        workout_data = WorkoutCreate(
            workout_type="swimming", duration=45, calories=300, date=date(2026, 4, 27)
        )
        create_workout(db=db_session, user_id=test_user.id, workout_data=workout_data)

        workouts = get_workouts_by_user(db=db_session, user_id=test_user.id)
        assert len(workouts) >= 1
        assert workouts[0].workout_type == "swimming"

    def test_get_workouts_empty(self, db_session, test_user):
        """A user with no workouts returns an empty list."""
        # test_user has no workouts yet in a fresh session
        new_user = create_user(db=db_session, user_data=UserCreate(
            username="no_workouts_user", email="noworkouts@example.com"
        ))
        workouts = get_workouts_by_user(db=db_session, user_id=new_user.id)
        assert workouts == []

    def test_get_workouts_user_not_found(self, db_session):
        """Listing workouts for a non-existent user raises 404."""
        with pytest.raises(NotFoundException):
            get_workouts_by_user(db=db_session, user_id=99999)


class TestGetWorkout:
    """Tests for the get_workout service function."""

    def test_get_workout_success(self, db_session, test_user):
        """Getting an existing workout by ID returns the correct workout."""
        workout_data = WorkoutCreate(
            workout_type="cycling", duration=60, calories=400, date=date(2026, 4, 27)
        )
        created = create_workout(db=db_session, user_id=test_user.id, workout_data=workout_data)

        fetched = get_workout(db=db_session, workout_id=created.id)
        assert fetched.id == created.id
        assert fetched.workout_type == "cycling"

    def test_get_workout_not_found(self, db_session):
        """Getting a non-existent workout raises 404."""
        with pytest.raises(NotFoundException):
            get_workout(db=db_session, workout_id=99999)


class TestDeleteWorkout:
    """Tests for the delete_workout service function."""

    def test_delete_workout_success(self, db_session, test_user):
        """Deleting an existing workout succeeds."""
        workout_data = WorkoutCreate(
            workout_type="weightlifting", duration=45, calories=350, date=date(2026, 4, 27)
        )
        created = create_workout(db=db_session, user_id=test_user.id, workout_data=workout_data)

        delete_workout(db=db_session, workout_id=created.id)

        with pytest.raises(NotFoundException):
            get_workout(db=db_session, workout_id=created.id)

    def test_delete_workout_not_found(self, db_session):
        """Deleting a non-existent workout raises 404."""
        with pytest.raises(NotFoundException):
            delete_workout(db=db_session, workout_id=99999)
