from app.channels.browser_rpa import BrowserRPAChannel
from app.channels.device_auto import DeviceAutoChannel
from app.channels.factory import build_channel


def test_factory_returns_device_channel_in_auto_mode(monkeypatch) -> None:
    monkeypatch.setenv("REDNOTE_OPERATION_MODE", "auto_device")
    monkeypatch.setenv("REDNOTE_DEVICE_ID", "test-device")

    from app.config.settings import get_settings

    get_settings.cache_clear()
    channel = build_channel()
    assert isinstance(channel, DeviceAutoChannel)


def test_factory_returns_browser_channel_in_manual_mode(monkeypatch) -> None:
    monkeypatch.setenv("REDNOTE_OPERATION_MODE", "manual")

    from app.config.settings import get_settings

    get_settings.cache_clear()
    channel = build_channel()
    assert isinstance(channel, BrowserRPAChannel)
