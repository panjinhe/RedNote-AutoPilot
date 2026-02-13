from app.ai_engine.content_generator import AIContentGenerator
from app.analytics.service import AnalyticsService
from app.channels.factory import build_channel
from app.order_manager.service import OrderManager
from app.product_manager.service import ProductManager


class AutoOpsWorkflow:
    def __init__(self) -> None:
        channel = build_channel()
        self.product_manager = ProductManager(channel, AIContentGenerator())
        self.order_manager = OrderManager(channel)
        self.analytics = AnalyticsService()

    def run_sales_loop(self) -> dict:
        recent_orders = self.order_manager.sync_recent_orders(minutes=60)
        return self.analytics.analyze_sales(recent_orders)
