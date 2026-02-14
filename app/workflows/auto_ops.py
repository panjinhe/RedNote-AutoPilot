from app.ai_engine.content_generator import AIContentGenerator
from app.analytics.service import AnalyticsService
from app.channels.factory import build_channel
from app.config.settings import get_settings
from app.order_manager.service import OrderManager
from app.product_manager.service import ProductManager
from app.tasks.executor import ListingTaskExecutor
from app.tasks.repository import TaskRepository


class AutoOpsWorkflow:
    def __init__(self) -> None:
        settings = get_settings()
        channel = build_channel()
        task_repo = TaskRepository(settings.task_db_path)
        task_executor = ListingTaskExecutor(
            channel,
            task_repo,
            final_confirm_required=settings.final_confirm_required,
        )

        self.product_manager = ProductManager(
            channel=channel,
            ai_generator=AIContentGenerator(),
            task_repo=task_repo,
            task_executor=task_executor,
            operation_mode=settings.operation_mode,
        )
        self.order_manager = OrderManager(channel)
        self.analytics = AnalyticsService()

    def run_sales_loop(self) -> dict:
        recent_orders = self.order_manager.sync_recent_orders(minutes=60)
        return self.analytics.analyze_sales(recent_orders)
