"""Every test runs offline, whatever is in your .env: no AWS, no real stores."""
import pytest

import config


@pytest.fixture(autouse=True)
def offline_settings(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "MODEL_ID", "anthropic.claude-sonnet-5-5")  # the fake Claude speaks this API
    monkeypatch.setattr(config, "STORE", "demo")
    monkeypatch.setattr(config, "CUSTOMER_ID", "c-7731")
    monkeypatch.setattr(config, "GUARDRAIL_ID", "")
    monkeypatch.setattr(config, "APPROVALS_FILE", tmp_path / "approvals.json")
    monkeypatch.setattr(config, "LOG_FILE", tmp_path / "agent.log")
    for name in ("STORE", "CUSTOMER_ID", "MODEL_ID"):
        monkeypatch.setenv(name, getattr(config, name))  # the MCP server side process reads these
