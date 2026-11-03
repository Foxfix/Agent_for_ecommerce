"""A pretend store that lives in one JSON file. Safe to break, free to run."""
import json
import re

import config
from connectors.base import StoreConnector
from safety.approvals import add_request

WORDS = re.compile(r"[a-z0-9]+")
STOP = {"a", "an", "the", "for", "with", "and", "or", "i", "me", "need", "want", "some", "any", "under", "to", "of", "in"}


class DemoStore(StoreConnector):
    name = "demo"

    def __init__(self, path=config.DATA_FILE):
        self.data = json.loads(path.read_text())

    def _product(self, product_id):
        return next((p for p in self.data["products"] if p["id"] == product_id), None)

    def search_products(self, query, max_price=None):
        # Every word of the query must appear in the product ("jackets" also matches "jacket").
        words = {w.rstrip("s") for w in WORDS.findall(query.lower())} - STOP
        results = []
        for p in self.data["products"]:
            text = f'{p["title"]} {p["category"]} {p["description"]}'.lower()
            if "waterproof" in words and not p["waterproof"]:
                continue
            if not words - {"waterproof"} <= {w.rstrip("s") for w in WORDS.findall(text)}:
                continue
            if max_price is not None and p["price"] > max_price:
                continue
            results.append({
                "id": p["id"], "title": p["title"], "price": p["price"],
                "in_stock": sum(p["stock"].values()) > 0,
            })
        return results

    def get_order(self, order_id, customer_id):
        order_id = order_id.lstrip("#").strip()
        for o in self.data["orders"]:
            if o["id"] == order_id and o["customer_id"] == customer_id:
                return {k: v for k, v in o.items() if k != "customer_id"}
        return None

    def check_stock(self, product_id, size=None):
        p = self._product(product_id)
        if p is None:
            return {"error": f"No product with id {product_id}"}
        stock = p["stock"] if size is None else {size: p["stock"].get(size, 0)}
        return {"product_id": product_id, "title": p["title"], "stock": stock}

    def create_return(self, order_id, customer_id, reason):
        order = self.get_order(order_id, customer_id)
        if order is None:
            return {"error": "Order not found for this customer"}
        if order["status"] != "delivered":
            return {"error": f"Order is {order['status']}, a return can start after delivery"}
        return add_request(store=self.name, order_id=order["id"], customer_id=customer_id, reason=reason)
