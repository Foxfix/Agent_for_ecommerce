"""The whole loop without AWS: a fake Claude endpoint asks for get_order, then answers."""
import json

import httpx2 as httpx

import config
from core.agent import build_agent, store_tools
from core.model import make_model

calls = []


def sse(events):
    return "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events)


def start():
    return {"type": "message_start", "message": {"id": "msg_1", "type": "message", "role": "assistant",
            "model": config.MODEL_ID, "content": [], "stop_reason": None, "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 1}}}


def end(reason):
    return [{"type": "message_delta", "delta": {"stop_reason": reason, "stop_sequence": None},
             "usage": {"output_tokens": 5}}, {"type": "message_stop"}]


def fake_claude(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    calls.append(body)
    if len(calls) == 1:  # first turn: call the tool
        events = [start(),
                  {"type": "content_block_start", "index": 0,
                   "content_block": {"type": "tool_use", "id": "toolu_1", "name": "get_order", "input": {}}},
                  {"type": "content_block_delta", "index": 0,
                   "delta": {"type": "input_json_delta", "partial_json": '{"order_id": "1042"}'}},
                  {"type": "content_block_stop", "index": 0}, *end("tool_use")]
    else:  # second turn: answer with text
        events = [start(),
                  {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
                  {"type": "content_block_delta", "index": 0,
                   "delta": {"type": "text_delta", "text": "Your order 1042 has shipped."}},
                  {"type": "content_block_stop", "index": 0}, *end("end_turn")]
    return httpx.Response(200, text=sse(events), headers={"content-type": "text/event-stream"})


def test_agent_calls_store_tool(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LOG_FILE", tmp_path / "agent.log")
    model = make_model(skip_auth=True, base_url="http://fake-mantle/anthropic",
                       http_client=httpx.AsyncClient(transport=httpx.MockTransport(fake_claude)))
    with store_tools() as mcp:
        agent = build_agent(mcp, model=model, callback_handler=None)
        answer = str(agent("Where is my order 1042?"))
    assert "shipped" in answer
    assert calls[0]["model"] == config.MODEL_ID
    tool_names = {t["name"] for t in calls[0]["tools"]}
    assert {"search_products", "check_stock", "get_order", "create_return"} <= tool_names
    tool_result = json.dumps(calls[1]["messages"][-1])
    assert "Storm Jacket" in tool_result  # the real demo store answered through MCP


def test_model_route_by_id(monkeypatch):
    from strands.models.bedrock import BedrockModel
    monkeypatch.setattr(config, "MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
    assert isinstance(make_model(), BedrockModel)  # only built, never called
    monkeypatch.setattr(config, "MODEL_ID", "anthropic.claude-sonnet-5-5")
    assert not isinstance(make_model(skip_auth=True), BedrockModel)
