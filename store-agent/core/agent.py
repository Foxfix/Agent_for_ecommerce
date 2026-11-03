"""The agent core: model + prompt + tools. Store-agnostic: it only knows our MCP server."""
import os
import sys

from mcp.client.stdio import StdioServerParameters, stdio_client
from strands import Agent
from strands.tools.mcp import MCPClient

import config
from core.model import make_model
from core.prompt import SYSTEM_PROMPT


def store_tools(customer_id: str = config.CUSTOMER_ID) -> MCPClient:
    """Start our MCP server as a small side process and connect to it."""
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
        cwd=str(config.ROOT),
        env={**os.environ, "CUSTOMER_ID": customer_id},
    )
    return MCPClient(lambda: stdio_client(params))


def extra_tools() -> list:
    """Tools that live outside MCP: the policy search, once its index is built."""
    tools = []
    if config.CHROMA_DIR.exists() or config.KNOWLEDGE == "keyword":
        from knowledge.search import search_policies
        tools.append(search_policies)
    return tools


def build_agent(mcp: MCPClient, model=None, **kwargs) -> Agent:
    """Call this inside `with store_tools() as mcp:` so the MCP server is running."""
    from safety.hooks import AuditHooks
    return Agent(
        model=model or make_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=[*mcp.list_tools_sync(), *extra_tools()],
        hooks=[AuditHooks()],
        **kwargs,
    )
