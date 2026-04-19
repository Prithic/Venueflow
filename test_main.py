import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)


def test_health_check():
    """Verify system uptime endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_response_structure():
    """Verify chat endpoint structure."""
    with patch("main.db.reference") as mock_ref:
        mock_ref.return_value.get.return_value = {"gate_a": 5, "gate_b": 10}
        response = client.post("/chat", json={"message": "test"})
        assert response.status_code == 200
        assert "reply" in response.json()


def test_empty_state():
    """Edge case: empty Firebase data."""
    with patch("main.db.reference") as mock_ref:
        mock_ref.return_value.get.return_value = {}
        response = client.post("/chat", json={"message": "status"})
        assert response.status_code == 200


def test_malformed_input():
    """Edge case: empty user message."""
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 200


def test_firebase_failure():
    """Edge case: Firebase failure simulation."""
    with patch("main.db.reference") as mock_ref:
        mock_ref.side_effect = Exception("DB down")
        response = client.post("/chat", json={"message": "status"})
        assert response.status_code == 500
