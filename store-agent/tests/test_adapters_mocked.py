"""Shopify orders, with fake HTTP answers. Real stores are tested in their lessons."""
import pytest

import config


class Resp:
    def __init__(self, data, status=200):
        self.data, self.status_code = data, status

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


@pytest.fixture(autouse=True)
def tmp_approvals(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "APPROVALS_FILE", tmp_path / "approvals.json")


# ---------------- Shopify ----------------
SHOP_ORDER = {"data": {"orders": {"nodes": [{
    "name": "#1001", "createdAt": "2026-10-01T10:00:00Z", "displayFinancialStatus": "PAID",
    "displayFulfillmentStatus": "FULFILLED", "customer": {"email": "alex.j@example.com"},
    "lineItems": {"nodes": [{"title": "Storm Jacket", "variantTitle": "L", "quantity": 1}]}}]}}}


@pytest.fixture
def shopify(monkeypatch):
    monkeypatch.setattr(config, "SHOPIFY_STORE", "test-shop.myshopify.com")
    seen = []

    def post(url, **kw):
        seen.append((url, kw))
        if url.endswith("/admin/oauth/access_token"):
            assert kw["data"]["grant_type"] == "client_credentials"
            return Resp({"access_token": "tok", "scope": "read_orders", "expires_in": 86399})
        if "/graphql.json" in url:
            assert kw["headers"]["X-Shopify-Access-Token"] == "tok"
            return Resp(SHOP_ORDER)
        raise AssertionError(url)

    monkeypatch.setattr("connectors.shopify.requests.post", post)
    from connectors.shopify import ShopifyStore
    store = ShopifyStore()
    store.seen = seen
    return store


def test_shopify_order_for_owner(shopify):
    o = shopify.get_order("1001", "alex.j@example.com")
    assert o["status"] == "fulfilled" and o["items"][0]["size"] == "L"


def test_shopify_hides_other_customers_order(shopify):
    assert shopify.get_order("1001", "someone@else.com") is None


def test_shopify_token_reused(shopify):
    shopify.get_order("1001", "alex.j@example.com")
    shopify.get_order("1001", "alex.j@example.com")
    assert sum(u.endswith("access_token") for u, _ in shopify.seen) == 1


def test_shopify_return_waits(shopify):
    assert shopify.create_return("1001", "alex.j@example.com", "too big")["status"] == "pending approval"
