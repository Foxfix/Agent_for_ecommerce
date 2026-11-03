"""Every adapter must pass the same tests. Today: the demo store."""
import pytest

import config
from connectors import get_connector


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "APPROVALS_FILE", tmp_path / "approvals.json")
    return get_connector("demo")


def test_search_finds_waterproof_jackets(store):
    titles = [p["title"] for p in store.search_products("waterproof jacket")]
    assert "Storm Jacket" in titles and "City Parka" not in titles


def test_search_respects_max_price(store):
    assert all(p["price"] <= 100 for p in store.search_products("jacket", max_price=100))


def test_order_belongs_to_customer(store):
    assert store.get_order("1042", "c-7731")["status"] == "shipped"


def test_someone_elses_order_is_hidden(store):
    assert store.get_order("1044", "c-7731") is None


def test_stock_per_size(store):
    assert store.check_stock("p-100", "M")["stock"] == {"M": 0}


def test_return_waits_for_a_person(store):
    result = store.create_return("1043", "c-7731", "too small")
    assert result["status"] == "pending approval"


def test_no_return_before_delivery(store):
    assert "error" in store.create_return("1042", "c-7731", "changed my mind")
