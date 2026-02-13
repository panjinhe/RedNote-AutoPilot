from __future__ import annotations

from typing import Any


class BrowserRPAChannel:
    """Human-in-the-loop browser workflow adapter.

    This adapter does not bypass platform controls.
    It only prepares draft tasks for manual confirmation.
    """

    def _queued(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "success": True,
            "mode": "browser_rpa",
            "action": action,
            "status": "queued_for_manual_confirmation",
            "payload": payload,
        }

    def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._queued("create_product", payload)

    def update_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._queued("update_product", payload)

    def set_product_online(self, xhs_product_id: str) -> dict[str, Any]:
        return self._queued("set_product_online", {"item_id": xhs_product_id})

    def set_product_offline(self, xhs_product_id: str) -> dict[str, Any]:
        return self._queued("set_product_offline", {"item_id": xhs_product_id})

    def get_orders(self, start_time: int, end_time: int) -> dict[str, Any]:
        return self._queued("get_orders", {"start_time": start_time, "end_time": end_time})

    def update_stock(self, xhs_product_id: str, sku_id: str, stock: int) -> dict[str, Any]:
        return self._queued(
            "update_stock", {"item_id": xhs_product_id, "sku_id": sku_id, "stock": stock}
        )
