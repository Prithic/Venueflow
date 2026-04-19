import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_chat_basic():
    res = client.post("/chat", json={"message": "Where should I go?"})
    assert res.status_code == 200
    assert "reply" in res.json()


@pytest.mark.asyncio
async def test_llm_primary_path():
    with patch("main.db_ref") as mock_ref:
        mock_ref.get.return_value = {"gate_a": 10, "gate_b": 5}
        with patch("main.Agent.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "🎯 Gate B\n💡 Faster"
            res = client.post("/chat", json={"message": "fastest gate"})
            assert res.status_code == 200
            assert "Gate B" in res.json()["reply"]


def test_empty_state():
    with patch("main.db_ref") as mock_ref:
        mock_ref.get.return_value = {}
        res = client.post("/chat", json={"message": "hello"})
        assert res.status_code == 200


def test_malformed_input():
    res = client.post("/chat", json={"msg": "wrong"})
    assert res.status_code == 422


def test_fallback_logic():
    with patch("main.db_ref") as mock_ref:
        mock_ref.get.return_value = {"gate_a": 10, "gate_b": 3}
        with patch("main.Agent.call_llm", return_value=None):
            res = client.post("/chat", json={"message": "fastest"})
            assert res.status_code == 200
            assert "gate_b" in res.json()["reply"].lower()
