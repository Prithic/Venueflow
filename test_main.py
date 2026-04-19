import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)

def test_health_check():
    """Verifies health check is operational in hybrid mode."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "hybrid_v6"

@pytest.mark.asyncio
async def test_deterministic_flow():
    """Verifies Layer 1 deterministic utility ranking."""
    with patch("main.db_ref") as mock_ref:
        mock_ref.get.return_value = {"gate_a": 5, "gate_b": 20}
        response = client.post("/chat", json={"message": "Gate A status"})
        assert response.status_code == 200
        data = response.json()
        assert "Gate A" in data["reply"]
        assert "Confidence" in data["thought_process"]

@pytest.mark.asyncio
async def test_llm_booster_trigger():
    """Verifies that low confidence triggers LLM booster (Layer 2)."""
    with patch("main.db_ref") as mock_ref:
        mock_ref.get.return_value = {"gate_a": 10, "food_court": 10}
        with patch("main.HybridReasoningEngine._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "LLM Optimized Response"
            with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
                response = client.post("/chat", json={"message": "I need help"})
                assert response.status_code == 200
                assert response.json()["reply"] == "LLM Optimized Response"
                assert "L2 Booster Active" in response.json()["thought_process"]

def test_empty_state_resilience():
    """Verifies fallback when state is missing."""
    with patch("main.db_ref") as mock_ref:
        mock_ref.get.return_value = {}
        response = client.post("/chat", json={"message": "hello"})
        assert response.status_code == 200
        assert "Telemetry link offline" in response.json()["reply"]

def test_malformed_input():
    """Verifies system stability with empty input."""
    with patch("main.db_ref") as mock_ref:
        mock_ref.get.return_value = {"gate_a": 10}
        response = client.post("/chat", json={"message": ""})
        assert response.status_code == 200
        assert "Autonomous Decision" in response.json()["reply"]
