from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.channels.base import CommerceChannel
from app.models.schemas import ListingPack, ListingTask, TaskStatus
from app.tasks.repository import TaskRepository


class ListingTaskExecutor:
    """模块化任务执行器：可扩展步骤、自动执行、失败可审计。"""

    def __init__(self, channel: CommerceChannel, repo: TaskRepository, final_confirm_required: bool = True) -> None:
        self.channel = channel
        self.repo = repo
        self.final_confirm_required = final_confirm_required

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _save_step(self, task_id: str, step_name: str, status: str, payload: dict[str, Any], error: str | None = None) -> None:
        artifact = None
        artifacts = payload.get("artifacts") if isinstance(payload, dict) else None
        if isinstance(artifacts, list) and artifacts:
            artifact = str(artifacts[0])
        self.repo.save_step(
            task_id=task_id,
            step_name=step_name,
            status=status,
            retry_count=0,
            artifact_path=artifact,
            error=error,
            updated_at=self._now(),
        )

    def execute(self, task: ListingTask, listing_pack: ListingPack) -> ListingTask:
        task.status = TaskStatus.running
        task.updated_at = self._now()
        self.repo.save_task(task)

        try:
            create_res = self.channel.create_product(listing_pack.model_dump())
            self.repo.log_step(
                task.task_id,
                "create_product",
                bool(create_res.get("success", False)),
                "商品创建完成",
                create_res,
                self._now(),
            )
            self._save_step(task.task_id, "create_product", "done", create_res)

            item_id = str(create_res.get("data", {}).get("item_id", ""))
            task.output = {"create": create_res, "item_id": item_id}

            if self.final_confirm_required:
                task.status = TaskStatus.wait_manual_confirm
                task.output["manual_confirm_required"] = True
            else:
                online_res = self.channel.set_product_online(item_id)
                self.repo.log_step(
                    task.task_id,
                    "set_product_online",
                    bool(online_res.get("success", False)),
                    "商品自动上架完成",
                    online_res,
                    self._now(),
                )
                self._save_step(task.task_id, "set_product_online", "done", online_res)
                task.status = TaskStatus.done
                task.output["online"] = online_res
        except Exception as exc:  # noqa: BLE001
            task.status = TaskStatus.failed
            task.output = {"error": str(exc)}
            self.repo.log_step(
                task.task_id,
                "task_failed",
                False,
                "自动化任务失败",
                {"error": str(exc)},
                self._now(),
            )
            self._save_step(task.task_id, "task_failed", "failed", {}, error=str(exc))

        task.updated_at = self._now()
        self.repo.save_task(task)
        return task

    def confirm_and_publish(self, task_id: str) -> ListingTask:
        task = self.repo.get_task(task_id)
        if task is None:
            raise ValueError("任务不存在")
        if task.status != TaskStatus.wait_manual_confirm:
            raise ValueError("当前任务不在待人工确认状态")

        item_id = str(task.output.get("item_id", ""))
        online_res = self.channel.set_product_online(item_id)
        self.repo.log_step(
            task.task_id,
            "set_product_online",
            bool(online_res.get("success", False)),
            "人工确认后发布完成",
            online_res,
            self._now(),
        )
        self._save_step(task.task_id, "set_product_online", "done", online_res)

        task.status = TaskStatus.done
        task.output["online"] = online_res
        task.output["manual_confirmed"] = True
        task.updated_at = self._now()
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
            "默认开启发布前人工确认闸口",
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
