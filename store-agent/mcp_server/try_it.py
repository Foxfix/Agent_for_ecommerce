"""Talk to our MCP server like any MCP client would, no AI involved: python -m mcp_server.try_it"""
import asyncio
import json
import sys

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main():
    server = StdioServerParameters(command=sys.executable, args=["-m", "mcp_server.server"])
    async with stdio_client(server) as (read, write), ClientSession(read, write) as session:
        await session.initialize()

        print("Tools this server offers:")
        for t in (await session.list_tools()).tools:
            print(f"  - {t.name}: {t.description}")

        for name, args in [("search_products", {"query": "waterproof jacket"}),
                           ("get_order", {"order_id": "1042"}),
                           ("get_order", {"order_id": "1044"})]:
            result = await session.call_tool(name, args)
            print(f"\n{name}({json.dumps(args)}) ->")
            data = result.structured_content if hasattr(result, "structured_content") else result.structuredContent
            print(json.dumps(data, indent=2) if data else result.content[0].text)


asyncio.run(main())
