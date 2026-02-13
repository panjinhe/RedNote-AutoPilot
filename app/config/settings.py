from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="REDNOTE_")

    operation_mode: Literal["manual", "browser_assist"] = "manual"
    merchant_publish_url: str = "https://ark.xiaohongshu.com"

    openai_api_key: str = ""
    scheduler_order_sync_minutes: int = 10
    scheduler_sales_analysis_minutes: int = 60


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
