from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="REDNOTE_")

    app_id: str = Field(default="", description="小红书开放平台 App ID")
    app_secret: str = Field(default="", description="小红书开放平台 App Secret")
    api_gateway: str = Field(
        default="https://ark.xiaohongshu.com/ark/open_api/v3/common_controller"
    )
    api_version: str = "2.0"
    request_timeout: int = 15

    openai_api_key: str = ""
    scheduler_order_sync_minutes: int = 10
    scheduler_sales_analysis_minutes: int = 60


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
