"""Our own MCP server: four store tools that any MCP client can use.

Run over stdio (the agent starts it for us) or over HTTP:
    python -m mcp_server.server --http
"""
import os
import sys

from mcp.server import MCPServer

import config
from connectors import get_connector
from safety.log import log

server = MCPServer(
    name="store-tools",
    instructions="Tools for one online store: products, stock, orders and returns.",
)
store = get_connector()


def customer() -> str:
    # The customer comes from the session, never from the model. The model can't change it.
    return os.getenv("CUSTOMER_ID", config.CUSTOMER_ID)


@server.tool()
def search_products(query: str, max_price: float | None = None) -> list[dict]:
    """Find products by words like "waterproof jacket". Optional max_price in dollars."""
    result = store.search_products(query, max_price)
    log("tool", tool="search_products", query=query, max_price=max_price, found=len(result))
    return result


@server.tool()
def check_stock(product_id: str, size: str | None = None) -> dict:
    """How many items of a product are left, per size. Use the product id from search_products."""
    result = store.check_stock(product_id, size)
    log("tool", tool="check_stock", product_id=product_id, size=size)
    return result


@server.tool()
def get_order(order_id: str) -> dict:
    """Status, items and delivery date of one of the current customer's orders."""
    result = store.get_order(order_id, customer())
    log("tool", tool="get_order", order_id=order_id, found=result is not None)
    return result or {"error": "No order with this number for the current customer"}


@server.tool()
def create_return(order_id: str, reason: str) -> dict:
    """Start a return for a delivered order. It does NOT refund money: a person approves it later."""
    result = store.create_return(order_id, customer(), reason)
    log("tool", tool="create_return", order_id=order_id, result=result)
    return result


if __name__ == "__main__":
    if "--http" in sys.argv:
        server.run("streamable-http", port=8001)
    else:
        server.run("stdio")
