class TestCreateWorkoutEndpoint:
    """Integration tests for POST /api/v1/users/{user_id}/workouts."""

    def test_create_workout_success(self, client, created_user, sample_workout_data):
        """Creating a workout for a valid user returns 201."""
        user_id = created_user["id"]

        response = client.post(f"/api/v1/users/{user_id}/workouts", json=sample_workout_data)

        assert response.status_code == 201
        data = response.json()
        assert data["workout_type"] == sample_workout_data["workout_type"]
        assert data["duration"] == sample_workout_data["duration"]
        assert data["calories"] == sample_workout_data["calories"]
        assert data["user_id"] == user_id
        assert "id" in data

    def test_create_workout_no_calories(self, client, created_user):
        """Creating a workout without calories (optional) returns 201."""
        user_id = created_user["id"]
        workout_data = {
            "workout_type": "yoga",
            "duration": 60,
            "date": "2026-04-27"
        }

        response = client.post(f"/api/v1/users/{user_id}/workouts", json=workout_data)

        assert response.status_code == 201
        assert response.json()["calories"] is None

    def test_create_workout_user_not_found(self, client, sample_workout_data):
        """Creating a workout for a non-existent user returns 404."""
        response = client.post("/api/v1/users/99999/workouts", json=sample_workout_data)

        assert response.status_code == 404

    def test_create_workout_missing_fields(self, client, created_user):
        """Creating a workout without required fields returns 422."""
        user_id = created_user["id"]

        response = client.post(f"/api/v1/users/{user_id}/workouts", json={})

        assert response.status_code == 422


class TestListUserWorkoutsEndpoint:
    """Integration tests for GET /api/v1/users/{user_id}/workouts."""

    def test_list_workouts_success(self, client, created_user, created_workout):
        """Listing workouts for a user with workouts returns them."""
        user_id = created_user["id"]

        response = client.get(f"/api/v1/users/{user_id}/workouts")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_workouts_empty(self, client, created_user):
        """Listing workouts for a user with no workouts returns empty list."""
        user_id = created_user["id"]

        response = client.get(f"/api/v1/users/{user_id}/workouts")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_workouts_user_not_found(self, client):
        """Listing workouts for a non-existent user returns 404."""
        response = client.get("/api/v1/users/99999/workouts")

        assert response.status_code == 404


class TestGetWorkoutEndpoint:
    """Integration tests for GET /api/v1/workouts/{workout_id}."""

    def test_get_workout_success(self, client, created_workout):
        """Getting an existing workout returns 200."""
        workout_id = created_workout["id"]

        response = client.get(f"/api/v1/workouts/{workout_id}")

        assert response.status_code == 200
        assert response.json()["workout_type"] == created_workout["workout_type"]

    def test_get_workout_not_found(self, client):
        """Getting a non-existent workout returns 404."""
        response = client.get("/api/v1/workouts/99999")

        assert response.status_code == 404


class TestDeleteWorkoutEndpoint:
    """Integration tests for DELETE /api/v1/workouts/{workout_id}."""

    def test_delete_workout_success(self, client, created_workout):
        """Deleting an existing workout returns 204."""
        workout_id = created_workout["id"]

        response = client.delete(f"/api/v1/workouts/{workout_id}")

        assert response.status_code == 204

        # Verify workout is gone
        get_response = client.get(f"/api/v1/workouts/{workout_id}")
        assert get_response.status_code == 404

    def test_delete_workout_not_found(self, client):
        """Deleting a non-existent workout returns 404."""
        response = client.delete("/api/v1/workouts/99999")

        assert response.status_code == 404


class TestCascadeDelete:
    """Test that deleting a user also deletes their workouts."""

    def test_delete_user_cascades_workouts(self, client, created_user, created_workout):
        """When a user is deleted, their workouts are also deleted."""
        user_id = created_user["id"]
        workout_id = created_workout["id"]

        # Delete the user
        delete_response = client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == 204

        # Verify the workout is also gone
        workout_response = client.get(f"/api/v1/workouts/{workout_id}")
        assert workout_response.status_code == 404
