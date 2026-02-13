from app.ai_engine.content_generator import AIContentGenerator
from app.analytics.service import AnalyticsService
from app.api_client.xhs_client import XHSClient
from app.order_manager.service import OrderManager
from app.product_manager.service import ProductManager


class AutoOpsWorkflow:
    def __init__(self) -> None:
        xhs_client = XHSClient()
        self.product_manager = ProductManager(xhs_client, AIContentGenerator())
        self.order_manager = OrderManager(xhs_client)
        self.analytics = AnalyticsService()

    def run_sales_loop(self) -> dict:
        recent_orders = self.order_manager.sync_recent_orders(minutes=60)
        return self.analytics.analyze_sales(recent_orders)
