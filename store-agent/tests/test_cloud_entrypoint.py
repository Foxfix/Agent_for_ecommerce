"""The AgentCore entrypoint, with the fake Claude endpoint. Nothing goes to AWS."""
import importlib.util
from types import SimpleNamespace

import httpx2

import config
import core.agent
from core.model import make_model
from tests import test_agent_offline as fake


def test_entrypoint_answers(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LOG_FILE", tmp_path / "agent.log")
    fake.calls.clear()
    monkeypatch.setattr(core.agent, "make_model", lambda: make_model(
        skip_auth=True, base_url="http://fake-mantle/anthropic",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(fake.fake_claude))))
    spec = importlib.util.spec_from_file_location("cloud_main", config.ROOT / "deploy" / "main.py")
    cloud = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cloud)
    try:
        out = cloud.invoke({"prompt": "Where is my order 1042?", "customer_id": "c-7731"},
                           SimpleNamespace(session_id="s1"))
        assert "shipped" in out["answer"]
    finally:
        for mcp, _ in cloud.sessions.values():
            mcp.stop(None, None, None)
