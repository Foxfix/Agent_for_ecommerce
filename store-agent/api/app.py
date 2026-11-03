"""The agent as a web service: uvicorn api.app:app --port 8000

POST /chat {"message": "..."} with the header X-Customer-Id. In a real shop the
website's login sets that header, the customer never types it.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header
from pydantic import BaseModel

import config
from core.agent import build_agent, store_tools
from safety.guard import check
from safety.log import log

sessions: dict[str, object] = {}
mcp_clients: dict[str, object] = {}


@asynccontextmanager
async def lifespan(app):
    yield
    for client in mcp_clients.values():
        client.stop(None, None, None)


app = FastAPI(title="Store agent", lifespan=lifespan)


class ChatIn(BaseModel):
    message: str


def agent_for(customer_id: str):
    # One MCP server + one conversation per customer, so nobody sees someone else's orders.
    if customer_id not in sessions:
        client = store_tools(customer_id)
        client.start()
        mcp_clients[customer_id] = client
        sessions[customer_id] = build_agent(client, callback_handler=None)
    return sessions[customer_id]


@app.get("/health")
def health():
    return {"ok": True, "model": config.MODEL_ID, "store": config.STORE}


@app.post("/chat")
def chat(body: ChatIn, x_customer_id: str = Header(default=config.CUSTOMER_ID)):
    log("customer", customer=x_customer_id, text=body.message)
    blocked = check(body.message, "INPUT")
    if blocked:
        return {"answer": blocked}
    answer = str(agent_for(x_customer_id)(body.message)).strip()
    answer = check(answer, "OUTPUT") or answer
    log("agent", customer=x_customer_id, text=answer)
    return {"answer": answer}
