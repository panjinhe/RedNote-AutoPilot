from app.channels.base import CommerceChannel
from app.channels.browser_rpa import BrowserRPAChannel
from app.config.settings import get_settings


def build_channel() -> CommerceChannel:
    settings = get_settings()
    return BrowserRPAChannel(mode=settings.operation_mode)
