class TestCreateUserEndpoint:
    """Integration tests for POST /api/v1/users."""

    def test_create_user_success(self, client, sample_user_data):
        """Creating a user returns 201 with the user data."""
        response = client.post("/api/v1/users", json=sample_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert "id" in data
        assert "created_at" in data

    def test_create_user_duplicate_username(self, client, sample_user_data):
        """Creating a user with a duplicate username returns 409."""
        client.post("/api/v1/users", json=sample_user_data)

        duplicate = {"username": sample_user_data["username"], "email": "other@example.com"}
        response = client.post("/api/v1/users", json=duplicate)

        assert response.status_code == 409

    def test_create_user_duplicate_email(self, client, sample_user_data):
        """Creating a user with a duplicate email returns 409."""
        client.post("/api/v1/users", json=sample_user_data)

        duplicate = {"username": "other_user", "email": sample_user_data["email"]}
        response = client.post("/api/v1/users", json=duplicate)

        assert response.status_code == 409

    def test_create_user_invalid_email(self, client):
        """Creating a user with an invalid email returns 422."""
        response = client.post("/api/v1/users", json={
            "username": "bad_email_user",
            "email": "not-an-email"
        })

        assert response.status_code == 422

    def test_create_user_missing_fields(self, client):
        """Creating a user without required fields returns 422."""
        response = client.post("/api/v1/users", json={})

        assert response.status_code == 422


class TestListUsersEndpoint:
    """Integration tests for GET /api/v1/users."""

    def test_list_users_empty(self, client):
        """Listing users when none exist returns an empty list."""
        response = client.get("/api/v1/users")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_users_after_creation(self, client, sample_user_data):
        """Listing users after creating one returns a non-empty list."""
        client.post("/api/v1/users", json=sample_user_data)

        response = client.get("/api/v1/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["username"] == sample_user_data["username"]

    def test_list_users_pagination(self, client):
        """Pagination parameters skip and limit work correctly."""
        # Create 3 users
        for i in range(3):
            client.post("/api/v1/users", json={
                "username": f"paginated_{i}",
                "email": f"paginated_{i}@example.com"
            })

        response = client.get("/api/v1/users?skip=0&limit=2")

        assert response.status_code == 200
        assert len(response.json()) <= 2


class TestGetUserEndpoint:
    """Integration tests for GET /api/v1/users/{user_id}."""

    def test_get_user_success(self, client, created_user):
        """Getting an existing user returns 200 with the user data."""
        user_id = created_user["id"]

        response = client.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 200
        assert response.json()["username"] == created_user["username"]

    def test_get_user_not_found(self, client):
        """Getting a non-existent user returns 404."""
        response = client.get("/api/v1/users/99999")

        assert response.status_code == 404


class TestUpdateUserEndpoint:
    """Integration tests for PUT /api/v1/users/{user_id}."""

    def test_update_user_success(self, client, created_user):
        """Updating an existing user returns 200 with updated data."""
        user_id = created_user["id"]
        update_data = {"username": "updated_name", "email": "updated@example.com"}

        response = client.put(f"/api/v1/users/{user_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updated_name"
        assert data["email"] == "updated@example.com"

    def test_update_user_not_found(self, client):
        """Updating a non-existent user returns 404."""
        response = client.put("/api/v1/users/99999", json={
            "username": "ghost", "email": "ghost@example.com"
        })

        assert response.status_code == 404


class TestDeleteUserEndpoint:
    """Integration tests for DELETE /api/v1/users/{user_id}."""

    def test_delete_user_success(self, client, created_user):
        """Deleting an existing user returns 204 No Content."""
        user_id = created_user["id"]

        response = client.delete(f"/api/v1/users/{user_id}")

        assert response.status_code == 204

        # Verify user is gone
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client):
        """Deleting a non-existent user returns 404."""
        response = client.delete("/api/v1/users/99999")

        assert response.status_code == 404
