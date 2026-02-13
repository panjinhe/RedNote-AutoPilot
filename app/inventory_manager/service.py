from app.channels.base import CommerceChannel


class InventoryManager:
    def __init__(self, channel: CommerceChannel) -> None:
        self.channel = channel

    def sync_stock(self, xhs_product_id: str, sku_id: str, expected_stock: int) -> dict:
        return self.channel.update_stock(xhs_product_id, sku_id, expected_stock)
