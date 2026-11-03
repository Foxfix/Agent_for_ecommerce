"""The web service, with the same fake Claude endpoint as the agent test."""
import httpx2
from fastapi.testclient import TestClient

import config
import core.agent
from core.model import make_model
from tests import test_agent_offline as fake


def test_chat_endpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LOG_FILE", tmp_path / "agent.log")
    fake.calls.clear()
    monkeypatch.setattr(core.agent, "make_model", lambda: make_model(
        skip_auth=True, base_url="http://fake-mantle/anthropic",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(fake.fake_claude))))
    from api.app import app
    with TestClient(app) as client:
        assert client.get("/health").json()["model"] == config.MODEL_ID
        r = client.post("/chat", json={"message": "Where is my order 1042?"}, headers={"X-Customer-Id": "c-7731"})
    assert "shipped" in r.json()["answer"]
    assert "Storm Jacket" in str(fake.calls[1]["messages"][-1])
