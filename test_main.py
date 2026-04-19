import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)

def test_health_check():
    """Verifies health check is operational with correct mode metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["mode"] == "hybrid_v6_compliance"

@pytest.mark.asyncio
async def test_deterministic_utility_flow():
    """Verifies Layer 1 deterministic utility ranking (Similarity + Throughput)."""
    with patch("main.db_ref") as mock_ref:
        # State: Gate A is much faster
        mock_ref.get.return_value = {"gate_a": 5, "gate_b": 45}
        response = client.post("/chat", json={"message": "gate a"})
        assert response.status_code == 200
        data = response.json()
        assert "Gate A" in data["reply"]
        assert "L1 Utility" in data["thought_process"]

@pytest.mark.asyncio
async def test_llm_booster_activation():
    """Verifies that low confidence (<0.65) triggers the Layer 2 LLM Booster."""
    with patch("main.db_ref") as mock_ref:
        mock_ref.get.return_value = {"gate_a": 10, "food_court": 10}
        # Mock LLM call in HybridReasoningEngine
        with patch("main.HybridReasoningEngine._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "🎯 LLM REASONING SUCCESS"
            with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
                # Query "Where is help?" has low similarity to gate_a
                response = client.post("/chat", json={"message": "I need help"})
                assert response.status_code == 200
                assert response.json()["reply"] == "🎯 LLM REASONING SUCCESS"
                assert "L2 Booster Active" in response.json()["thought_process"]

def test_telemetry_offline_resilience():
    """Verifies graceful degradation when database is unreachable."""
    with patch("main.db_ref") as mock_ref:
        mock_ref.get.return_value = None
        response = client.post("/chat", json={"message": "hello"})
        assert response.status_code == 200
        assert "Telemetry link offline" in response.json()["reply"]

def test_request_validation():
    """Verifies FastAPI schema validation for malformed payloads."""
    response = client.post("/chat", json={"wrong_key": "data"})
    assert response.status_code == 422
