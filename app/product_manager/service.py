from __future__ import annotations

from typing import Any

from app.ai_engine.content_generator import AIContentGenerator
from app.api_client.xhs_client import XHSClient
from app.models.schemas import ProductCreate


class ProductManager:
    def __init__(self, xhs_client: XHSClient, ai_generator: AIContentGenerator) -> None:
        self.xhs_client = xhs_client
        self.ai_generator = ai_generator

    def auto_create_product(self, product: ProductCreate) -> dict[str, Any]:
        draft = self.ai_generator.generate_product_content(product)

        payload = {
            "title": draft.optimized_title,
            "category": product.category,
            "desc": draft.detail_copy,
            "tags": draft.tags,
            "sale_price": product.sale_price,
            "cost_price": product.cost_price,
            "sku_list": [{"name": sku, "stock": 100} for sku in draft.recommended_skus],
        }
        created = self.xhs_client.create_product(payload)

        item_id = created.get("data", {}).get("item_id", "")
        if item_id:
            self.xhs_client.set_product_online(item_id)
        return {"draft": draft.model_dump(), "created": created}

    def auto_update_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.xhs_client.update_product(payload)

    def auto_set_online(self, xhs_product_id: str) -> dict[str, Any]:
        return self.xhs_client.set_product_online(xhs_product_id)

    def auto_set_offline(self, xhs_product_id: str) -> dict[str, Any]:
        return self.xhs_client.set_product_offline(xhs_product_id)
