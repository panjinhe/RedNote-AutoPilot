from apscheduler.schedulers.blocking import BlockingScheduler

from app.config.settings import get_settings
from app.workflows.auto_ops import AutoOpsWorkflow


class TaskScheduler:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.workflow = AutoOpsWorkflow()
        self.scheduler = BlockingScheduler(timezone="Asia/Shanghai")

    def register(self) -> None:
        self.scheduler.add_job(
            self.workflow.order_manager.sync_recent_orders,
            "interval",
            minutes=self.settings.scheduler_order_sync_minutes,
            id="sync_orders",
        )
        self.scheduler.add_job(
            self.workflow.run_sales_loop,
            "interval",
            minutes=self.settings.scheduler_sales_analysis_minutes,
            id="analyze_sales",
        )

    def start(self) -> None:
        self.register()
        self.scheduler.start()
