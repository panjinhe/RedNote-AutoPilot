from __future__ import annotations

from app.channels.base import CommerceChannel
from app.channels.browser_rpa import BrowserRPAChannel
from app.config.settings import get_settings


def build_channel() -> CommerceChannel:
    settings = get_settings()
    if settings.operation_mode == "browser_rpa":
        return BrowserRPAChannel()

    from app.api_client.xhs_client import XHSClient

    return XHSClient()
