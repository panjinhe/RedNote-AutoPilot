import time

from app.api_client.xhs_client import XHSClient


class OrderManager:
    def __init__(self, xhs_client: XHSClient) -> None:
        self.xhs_client = xhs_client

    def sync_recent_orders(self, minutes: int = 10) -> dict:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - minutes * 60 * 1000
        return self.xhs_client.get_orders(start_ms, end_ms)
