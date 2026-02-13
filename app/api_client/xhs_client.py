"""XHS Open API client wrapper.

Docs:
- https://open.xiaohongshu.com
- https://ark.xiaohongshu.com/ark/open_api/v3/common_controller
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any

import requests

from app.config.settings import get_settings


@dataclass
class OAuthToken:
    access_token: str
    refresh_token: str
    expires_in: int


class XHSClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.api_gateway

    def _sign(self, method: str, timestamp: int) -> str:
        raw = (
            f"{method}?appId={self.settings.app_id}&timestamp={timestamp}"
            f"&version={self.settings.api_version}{self.settings.app_secret}"
        )
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def _request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        timestamp = int(time.time() * 1000)
        sign = self._sign(method=path, timestamp=timestamp)
        body = {
            "appId": self.settings.app_id,
            "timestamp": timestamp,
            "version": self.settings.api_version,
            "sign": sign,
            **payload,
        }
        response = requests.post(
            self.base_url,
            json={"method": path, "params": body},
            timeout=self.settings.request_timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_access_token(self, code: str) -> dict[str, Any]:
        return self._request("POST", "oauth.token", {"code": code})

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        return self._request("POST", "oauth.refresh", {"refresh_token": refresh_token})

    def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "item.create", payload)

    def update_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "item.update", payload)

    def set_product_online(self, xhs_product_id: str) -> dict[str, Any]:
        return self._request("POST", "item.on_shelf", {"item_id": xhs_product_id})

    def set_product_offline(self, xhs_product_id: str) -> dict[str, Any]:
        return self._request("POST", "item.off_shelf", {"item_id": xhs_product_id})

    def get_orders(self, start_time: int, end_time: int) -> dict[str, Any]:
        return self._request(
            "POST",
            "order.list",
            {"start_time": start_time, "end_time": end_time},
        )

    def update_stock(self, xhs_product_id: str, sku_id: str, stock: int) -> dict[str, Any]:
        return self._request(
            "POST",
            "item.stock.update",
            {"item_id": xhs_product_id, "sku_id": sku_id, "stock": stock},
        )
