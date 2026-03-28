"""Tests for the air quality endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestAirQualityEndpoint:
    """Tests for GET /api/air-quality."""

    def test_returns_200(self):
        response = client.get("/api/air-quality")
        assert response.status_code == 200

    def test_response_has_required_keys(self):
        response = client.get("/api/air-quality")
        data = response.json()
        assert "data" in data
        assert "source" in data
        assert "country" in data

    def test_country_is_india(self):
        response = client.get("/api/air-quality")
        data = response.json()
        assert data["country"] == "India"

    def test_source_is_openaq(self):
        response = client.get("/api/air-quality")
        data = response.json()
        assert data["source"] == "OpenAQ"

    def test_data_is_list(self):
        response = client.get("/api/air-quality")
        data = response.json()
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_each_item_has_required_fields(self):
        response = client.get("/api/air-quality")
        items = response.json()["data"]
        for item in items:
            assert "city" in item
            assert "station" in item
            assert "pollutant" in item
            assert "value" in item
            assert "unit" in item
            assert "timestamp" in item

    def test_values_are_numeric(self):
        response = client.get("/api/air-quality")
        items = response.json()["data"]
        for item in items:
            assert isinstance(item["value"], (int, float))

    def test_no_null_values(self):
        response = client.get("/api/air-quality")
        items = response.json()["data"]
        for item in items:
            assert item["city"] is not None and item["city"] != ""
            assert item["pollutant"] is not None and item["pollutant"] != ""
            assert item["value"] is not None
