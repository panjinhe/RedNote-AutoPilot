from __future__ import annotations

import time
from typing import Any


class DeviceAutoChannel:
    """全自动手机端上架通道（可扩展为ADB/UIAutomator/视觉识别）。"""

    def __init__(self, device_id: str = "emulator-5554", dry_run: bool = True) -> None:
        self.device_id = device_id
        self.dry_run = dry_run

    def _ok(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "success": True,
            "mode": "auto_device",
            "device_id": self.device_id,
            "action": action,
            "status": "done",
            "payload": payload,
            "timestamp": int(time.time() * 1000),
        }

    def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        item_id = f"auto_{int(time.time() * 1000)}"
        result = self._ok("create_product", payload)
        result["data"] = {"item_id": item_id}
        return result

    def update_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._ok("update_product", payload)

    def set_product_online(self, xhs_product_id: str) -> dict[str, Any]:
        return self._ok("set_product_online", {"item_id": xhs_product_id})

    def set_product_offline(self, xhs_product_id: str) -> dict[str, Any]:
        return self._ok("set_product_offline", {"item_id": xhs_product_id})

    def get_orders(self, start_time: int, end_time: int) -> dict[str, Any]:
        return self._ok("get_orders", {"start_time": start_time, "end_time": end_time})

    def update_stock(self, xhs_product_id: str, sku_id: str, stock: int) -> dict[str, Any]:
        return self._ok(
            "update_stock", {"item_id": xhs_product_id, "sku_id": sku_id, "stock": stock}
        )
