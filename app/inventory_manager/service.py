from app.api_client.xhs_client import XHSClient


class InventoryManager:
    def __init__(self, xhs_client: XHSClient) -> None:
        self.xhs_client = xhs_client

    def sync_stock(self, xhs_product_id: str, sku_id: str, expected_stock: int) -> dict:
        return self.xhs_client.update_stock(xhs_product_id, sku_id, expected_stock)
