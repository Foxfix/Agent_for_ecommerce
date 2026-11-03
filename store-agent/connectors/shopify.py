"""Shopify adapter.

Products come from the store's public catalog over MCP (Shopify's UCP Storefront Catalog).
Orders come from the Admin API, with a token from your Dev Dashboard app.
"""
import time

import requests

import config
from connectors.base import StoreConnector
from safety.approvals import add_request


class ShopifyStore(StoreConnector):
    name = "shopify"

    def __init__(self):
        if not config.SHOPIFY_STORE:
            raise RuntimeError("Set SHOPIFY_STORE in the .env file")
        self.shop = config.SHOPIFY_STORE
        self._token, self._token_until = None, 0

    # ---------- public catalog (MCP) ----------
    def _catalog(self, tool: str, catalog: dict) -> dict:
        body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool, "arguments": {
            "meta": {"ucp-agent": {"profile": config.SHOPIFY_AGENT_PROFILE}}, "catalog": catalog}}}
        r = requests.post(f"https://{self.shop}/api/ucp/mcp", json=body, timeout=20)
        r.raise_for_status()
        result = r.json()["result"]
        if result.get("isError"):
            raise RuntimeError(result["content"][0]["text"])
        return result["structuredContent"]

    def search_products(self, query, max_price=None):
        try:
            return self._catalog_search(query, max_price)
        except Exception:  # e.g. a password-protected dev store: ask the Admin API instead
            return self._admin_search(query, max_price)

    def _catalog_search(self, query, max_price):
        catalog = {"query": query}
        if max_price is not None:
            catalog["filters"] = {"price": {"max": int(max_price * 100)}}  # Shopify counts in cents
        found = self._catalog("search_catalog", catalog).get("products", [])
        return [{
            "id": p["id"], "title": p["title"],
            "price": p["price_range"]["min"]["amount"] / 100,
            "in_stock": any(v.get("availability", {}).get("available") for v in p.get("variants", [])),
        } for p in found]

    def check_stock(self, product_id, size=None):
        try:
            return self._catalog_stock(product_id, size)
        except Exception:
            return self._admin_stock(product_id, size)

    def _catalog_stock(self, product_id, size):
        # The catalog shows one variant at a time, so we ask about each size we care about.
        p = self._catalog("get_product", {"id": product_id})["product"]
        sizes = next((o["values"] for o in p.get("options", []) if o["name"].lower() == "size"), [])
        labels = [v["label"] for v in sizes if size is None or v["label"].lower() == str(size).lower()]
        if sizes and not labels:
            return {"error": f"Size {size} is not offered", "sizes": [v["label"] for v in sizes]}
        if not labels:  # no sizes: one variant for the whole product
            v = p["variants"][0]
            return {"product_id": product_id, "title": p["title"],
                    "stock": {"all": "available" if v["availability"]["available"] else "sold out"}}
        stock = {}
        for label in labels:
            v = self._catalog("get_product", {"id": product_id, "selected": [{"name": "Size", "label": label}]})
            ok = v["product"]["variants"][0]["availability"]["available"]
            stock[label] = "available" if ok else "sold out"
        return {"product_id": product_id, "title": p["title"], "stock": stock}

    # ---------- orders (Admin API) ----------
    def _admin_token(self) -> str:
        # Dev Dashboard apps trade their Client ID and secret for a token that lives 24 hours.
        if self._token and time.time() < self._token_until:
            return self._token
        r = requests.post(f"https://{self.shop}/admin/oauth/access_token", timeout=20, data={
            "grant_type": "client_credentials",
            "client_id": config.SHOPIFY_CLIENT_ID,
            "client_secret": config.SHOPIFY_CLIENT_SECRET,
        })
        r.raise_for_status()
        data = r.json()
        self._token, self._token_until = data["access_token"], time.time() + data["expires_in"] - 60
        return self._token

    def _admin(self, query: str, variables: dict) -> dict:
        r = requests.post(
            f"https://{self.shop}/admin/api/{config.SHOPIFY_API_VERSION}/graphql.json",
            json={"query": query, "variables": variables},
            headers={"X-Shopify-Access-Token": self._admin_token()}, timeout=20)
        r.raise_for_status()
        body = r.json()
        if body.get("data") is None:
            raise RuntimeError(f"Shopify Admin API error: {body.get('errors')}")
        return body["data"]

    ORDER_QUERY = """
    query ($q: String!) {
      orders(first: 1, query: $q) { nodes {
        name createdAt displayFinancialStatus displayFulfillmentStatus
        customer { email }
        lineItems(first: 10) { nodes { title variantTitle quantity } }
      } }
    }"""

    PRODUCTS_QUERY = """
    query ($q: String!) {
      products(first: 10, query: $q) { nodes {
        id title totalInventory
        priceRangeV2 { minVariantPrice { amount } }
      } }
    }"""

    STOCK_QUERY = """
    query ($id: ID!) {
      product(id: $id) { title variants(first: 50) { nodes { title inventoryQuantity } } }
    }"""

    def _admin_search(self, query, max_price):
        q = " ".join(f"title:*{w}*" for w in query.split())
        if max_price is not None:
            q += f" price:<={max_price}"
        nodes = self._admin(self.PRODUCTS_QUERY, {"q": q})["products"]["nodes"]
        return [{"id": p["id"], "title": p["title"],
                 "price": float(p["priceRangeV2"]["minVariantPrice"]["amount"]),
                 "in_stock": (p["totalInventory"] or 0) > 0} for p in nodes]

    def _admin_stock(self, product_id, size):
        p = self._admin(self.STOCK_QUERY, {"id": product_id})["product"]
        if p is None:
            return {"error": f"No product with id {product_id}"}
        stock = {v["title"]: v["inventoryQuantity"] for v in p["variants"]["nodes"]
                 if size is None or str(size).lower() in v["title"].lower()}
        return {"product_id": product_id, "title": p["title"], "stock": stock}

    def get_order(self, order_id, customer_id):
        # In Shopify we know the customer by email.
        name = "#" + order_id.lstrip("#").strip()
        nodes = self._admin(self.ORDER_QUERY, {"q": f"name:{name}"})["orders"]["nodes"]
        if not nodes or (nodes[0]["customer"] or {}).get("email", "").lower() != customer_id.lower():
            return None
        o = nodes[0]
        return {
            "id": o["name"].lstrip("#"), "placed_on": o["createdAt"][:10],
            "status": o["displayFulfillmentStatus"].lower(), "payment": o["displayFinancialStatus"].lower(),
            "items": [{"title": i["title"], "size": i["variantTitle"], "quantity": i["quantity"]}
                      for i in o["lineItems"]["nodes"]],
        }

    def create_return(self, order_id, customer_id, reason):
        order = self.get_order(order_id, customer_id)
        if order is None:
            return {"error": "Order not found for this customer"}
        if order["status"] != "fulfilled":
            return {"error": f"Order is {order['status']}, a return can start after it is shipped"}
        return add_request(store=self.name, order_id=order["id"], customer_id=customer_id, reason=reason)
 