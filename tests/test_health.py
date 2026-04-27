class TestHealthEndpoint:
    """Integration tests for the health check endpoint."""

    def test_health_check_returns_200(self, client):
        """GET /api/v1/health returns 200 with healthy status."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint(self, client):
        """GET / returns the welcome message."""
        response = client.get("/")

        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to FitnessPulse API!"}
