"""The contract every store adapter signs. The agent only ever sees these four methods."""
from abc import ABC, abstractmethod


class StoreConnector(ABC):
    name = "base"

    @abstractmethod
    def search_products(self, query: str, max_price: float | None = None) -> list[dict]:
        """Products that match the words in `query`. Each: id, title, price, in_stock."""

    @abstractmethod
    def get_order(self, order_id: str, customer_id: str) -> dict | None:
        """One order, only if it belongs to this customer. Otherwise None."""

    @abstractmethod
    def check_stock(self, product_id: str, size: str | None = None) -> dict:
        """How many items are left, per size."""

    @abstractmethod
    def create_return(self, order_id: str, customer_id: str, reason: str) -> dict:
        """Never refunds by itself. Creates a request that waits for a person."""
