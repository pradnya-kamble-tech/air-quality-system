"""Tests for health and root endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root / endpoint."""

    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_message(self):
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "environment" in data

    def test_root_message_content(self):
        response = client.get("/")
        data = response.json()
        assert data["message"] == "Air Quality API is running 🚀"
        assert data["environment"] == "development"


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_contains_keys(self):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "region" in data

    def test_health_response_content(self):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "OK"
        assert data["service"] == "Air Quality Backend"
        assert data["region"] == "India"
