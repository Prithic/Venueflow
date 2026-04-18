import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Verify that the API root is accessible and returns 200 OK."""
    response = client.get("/")
    assert response.status_code == 200

def test_mock_firebase_interaction():
    """Verify that the concierge logic functions with mocked data."""
    with patch("main.db.reference") as mock_ref:
        mock_ref.return_value.get.return_value = {"gate_a": 5, "gate_b": 50}
        response = client.post("/chat", json={"message": "Which gate is fastest?"})
        assert response.status_code == 200
        assert "reply" in response.json()
        assert "Gate A" in response.json()["reply"]
