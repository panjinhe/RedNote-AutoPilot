from app.channels.base import CommerceChannel
from app.channels.browser_rpa import BrowserRPAChannel
from app.channels.device_auto import DeviceAutoChannel
from app.config.settings import get_settings


def build_channel() -> CommerceChannel:
    settings = get_settings()
    if settings.operation_mode == "auto_device":
        return DeviceAutoChannel(device_id=settings.device_id, dry_run=settings.device_dry_run)
    return BrowserRPAChannel(mode=settings.operation_mode)
