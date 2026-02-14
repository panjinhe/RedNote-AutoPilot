from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.channels.base import CommerceChannel
from app.models.schemas import ListingPack, ListingTask, TaskStatus
from app.tasks.repository import TaskRepository


class ListingTaskExecutor:
    """模块化任务执行器：可扩展步骤、自动执行、失败可审计。"""

    def __init__(self, channel: CommerceChannel, repo: TaskRepository) -> None:
        self.channel = channel
        self.repo = repo

    def execute(self, task: ListingTask, listing_pack: ListingPack) -> ListingTask:
        now = datetime.now(timezone.utc).isoformat()
        task.status = TaskStatus.running
        task.updated_at = now
        self.repo.save_task(task)

        try:
            create_res = self.channel.create_product(listing_pack.model_dump())
            self.repo.log_step(
                task.task_id,
                "create_product",
                bool(create_res.get("success", False)),
                "商品创建完成",
                create_res,
                datetime.now(timezone.utc).isoformat(),
            )

            item_id = str(create_res.get("data", {}).get("item_id", ""))
            online_res = self.channel.set_product_online(item_id)
            self.repo.log_step(
                task.task_id,
                "set_product_online",
                bool(online_res.get("success", False)),
                "商品自动上架完成",
                online_res,
                datetime.now(timezone.utc).isoformat(),
            )

            task.status = TaskStatus.done
            task.output = {"create": create_res, "online": online_res}
        except Exception as exc:  # noqa: BLE001
            task.status = TaskStatus.failed
            task.output = {"error": str(exc)}
            self.repo.log_step(
                task.task_id,
                "task_failed",
                False,
                "自动化任务失败",
                {"error": str(exc)},
                datetime.now(timezone.utc).isoformat(),
            )

        task.updated_at = datetime.now(timezone.utc).isoformat()
        self.repo.save_task(task)
        return task

    @staticmethod
    def build_pack(product_id: str, payload: dict[str, Any]) -> ListingPack:
        checklist = [
            "标题已自动填充",
            "SKU已自动填充",
            "库存已自动填充",
            "价格已自动填充",
            "图片待补充时可扩展图片上传步骤",
        ]
        return ListingPack(
            product_id=product_id,
            title=str(payload["title"]),
            desc=str(payload["desc"]),
            tags=list(payload.get("tags", [])),
            sale_price=float(payload["sale_price"]),
            cost_price=float(payload["cost_price"]),
            sku_list=list(payload.get("sku_list", [])),
            images=list(payload.get("images", [])),
            checklist=checklist,
        )
