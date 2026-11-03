import config


def get_connector(name: str | None = None):
    """Pick the store adapter by name. The rest of the code never changes."""
    name = name or config.STORE
    if name == "demo":
        from connectors.demo import DemoStore
        return DemoStore()
    if name == "shopify":
        from connectors.shopify import ShopifyStore
        return ShopifyStore()
    raise ValueError(f"Unknown store: {name}")
