"""Our agent inside Amazon Bedrock AgentCore Runtime.

AgentCore calls `invoke` for every message: {"prompt": "..."}.
The website's server adds "customer_id" from the login session; the customer never types it.
Without it (for example from `agentcore invoke`) we use the demo customer.
"""
from collections import OrderedDict

from bedrock_agentcore.runtime import BedrockAgentCoreApp

import config
from core.agent import build_agent, store_tools
from safety.guard import check
from safety.log import log

app = BedrockAgentCoreApp()
sessions: OrderedDict = OrderedDict()  # session id -> (mcp client, agent)


def agent_for(session_id: str, customer_id: str):
    key = f"{session_id}:{customer_id}"
    if key not in sessions:
        if len(sessions) >= 50:  # keep memory small: close the oldest conversation
            old_mcp, _ = sessions.popitem(last=False)[1]
            old_mcp.stop(None, None, None)
        mcp = store_tools(customer_id)
        mcp.start()
        sessions[key] = (mcp, build_agent(mcp, callback_handler=None))
    sessions.move_to_end(key)
    return sessions[key][1]


@app.entrypoint
def invoke(payload, context):
    text = payload.get("prompt", "")
    customer_id = payload.get("customer_id", config.CUSTOMER_ID)
    session_id = getattr(context, "session_id", None) or "default"
    log("customer", customer=customer_id, text=text)
    blocked = check(text, "INPUT")
    if blocked:
        return {"answer": blocked}
    answer = str(agent_for(session_id, customer_id)(text)).strip()
    answer = check(answer, "OUTPUT") or answer
    log("agent", customer=customer_id, text=answer)
    return {"answer": answer}


if __name__ == "__main__":
    app.run()
