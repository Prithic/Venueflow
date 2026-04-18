import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_root_health_check():
    """Verify system uptime and service status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_chat_response_structure():
    """Verify that the chat endpoint returns the expected JSON structure."""
    with patch("main.db.reference") as mock_ref:
        mock_ref.return_value.get.return_value = {"gate_a": 5, "gate_b": 10}
        response = client.post("/chat", json={"message": "test message"})
        assert response.status_code == 200
        assert "reply" in response.json()

def test_proactive_routing_logic():
    """Verify that the AI suggests alternatives when congestion is detected."""
    with patch("main.db.reference") as mock_ref:
        # Simulate Gate A being very busy
        mock_ref.return_value.get.return_value = {"gate_a": 45, "gate_b": 5}
        response = client.post("/chat", json={"message": "How is Gate A?"})
        assert response.status_code == 200
        # The reply should contain a recommendation for Gate B
        assert "Gate B" in response.json()["reply"]
