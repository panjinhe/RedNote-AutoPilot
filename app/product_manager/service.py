from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.ai_engine.content_generator import AIContentGenerator
from app.channels.base import CommerceChannel
from app.models.schemas import ListingTask, ProductCreate
from app.tasks.executor import ListingTaskExecutor
from app.tasks.repository import TaskRepository


class ProductManager:
    def __init__(
        self,
        channel: CommerceChannel,
        ai_generator: AIContentGenerator,
        task_repo: TaskRepository,
        task_executor: ListingTaskExecutor,
        operation_mode: str,
    ) -> None:
        self.channel = channel
        self.ai_generator = ai_generator
        self.task_repo = task_repo
        self.task_executor = task_executor
        self.operation_mode = operation_mode

    def auto_create_product(self, product: ProductCreate) -> dict[str, Any]:
        draft = self.ai_generator.generate_product_content(product)
        product_id = str(uuid4())
        payload = {
            "title": draft.optimized_title,
            "category": product.category,
            "desc": draft.detail_copy,
            "tags": draft.tags,
            "sale_price": product.sale_price,
            "cost_price": product.cost_price,
            "sku_list": [{"name": sku, "stock": 100} for sku in draft.recommended_skus],
            "images": [],
        }

        listing_pack = self.task_executor.build_pack(product_id=product_id, payload=payload)
        task = ListingTask.create(
            product_id=product_id,
            listing_pack_version=listing_pack.version,
            input_snapshot=listing_pack.model_dump(),
            channel=self.operation_mode,
        )
        self.task_repo.save_task(task)

        if self.operation_mode == "auto_device":
            task = self.task_executor.execute(task, listing_pack)

        return {
            "draft": draft.model_dump(),
            "listing_pack": listing_pack.model_dump(),
            "task": task.model_dump(),
        }

    def auto_update_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.channel.update_product(payload)

    def auto_set_online(self, xhs_product_id: str) -> dict[str, Any]:
        return self.channel.set_product_online(xhs_product_id)

    def auto_set_offline(self, xhs_product_id: str) -> dict[str, Any]:
        return self.channel.set_product_offline(xhs_product_id)

    def get_task(self, task_id: str) -> dict[str, Any]:
        task = self.task_repo.get_task(task_id)
        if not task:
            return {"task": None, "steps": []}
        return {"task": task.model_dump(), "steps": self.task_repo.list_steps(task_id)}

    def confirm_task(self, task_id: str) -> dict[str, Any]:
        task = self.task_executor.confirm_and_publish(task_id)
        return {"task": task.model_dump(), "steps": self.task_repo.list_steps(task_id)}
