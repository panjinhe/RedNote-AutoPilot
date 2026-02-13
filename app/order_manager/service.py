import time

from app.channels.base import CommerceChannel


class OrderManager:
    def __init__(self, channel: CommerceChannel) -> None:
        self.channel = channel

    def sync_recent_orders(self, minutes: int = 10) -> dict:
        end_ms = int(time.time() * 1000)
        start_ms = end_ms - minutes * 60 * 1000
        return self.channel.get_orders(start_ms, end_ms)
