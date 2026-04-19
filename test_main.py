import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_health_check():
    """
    Verifies that the health check endpoint is operational.
    
    Args:
        None
    Returns:
        None
    Raises:
        AssertionError: If status code is not 200 or status is not 'operational'.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_valid_flow():
    """
    Verifies the standard reasoning flow with valid telemetry data.
    
    Args:
        None
    Returns:
        None
    Raises:
        AssertionError: If response structure is invalid.
    """
    with patch("main.queues_ref") as mock_ref:
        mock_ref.get.return_value = {"gate_a": 5, "food_court": 20}
        response = client.post("/chat", json={"message": "Where should I enter?"})
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "thought_process" in data
        assert "Gate A" in data["reply"]

def test_empty_state():
    """
    Verifies system resilience when Firebase returns an empty state.
    
    Args:
        None
    Returns:
        None
    Raises:
        AssertionError: If system crashes or fails to return a fallback message.
    """
    with patch("main.queues_ref") as mock_ref:
        mock_ref.get.return_value = {}
        response = client.post("/chat", json={"message": "Help"})
        assert response.status_code == 200
        assert "Telemetry stream interrupted" in response.json()["reply"]

def test_malformed_input():
    """
    Verifies that the system handles malformed or empty user input gracefully.
    
    Args:
        None
    Returns:
        None
    Raises:
        AssertionError: If system fails to process an empty string query.
    """
    with patch("main.queues_ref") as mock_ref:
        mock_ref.get.return_value = {"gate_a": 10}
        response = client.post("/chat", json={"message": ""})
        assert response.status_code == 200
        assert "Autonomous Decision" in response.json()["reply"]

def test_firebase_failure():
    """
    Verifies graceful fallback when the persistence layer throws an exception.
    
    Args:
        None
    Returns:
        None
    Raises:
        AssertionError: If system returns 500 instead of a graceful 200 fallback.
    """
    with patch("main.queues_ref") as mock_ref:
        mock_ref.get.side_effect = Exception("Connection Timeout")
        response = client.post("/chat", json={"message": "status"})
        # Should return a valid response even if DB fails
        assert response.status_code == 200
        assert "Telemetry stream interrupted" in response.json()["reply"]
