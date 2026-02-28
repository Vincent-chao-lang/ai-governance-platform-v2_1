from __future__ import annotations
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    database_url: str = Field(..., alias="DATABASE_URL")

    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="admin123", alias="ADMIN_PASSWORD")

    allowed_api_keys: List[str] = Field(default_factory=lambda: ["demo-key"], alias="ALLOWED_API_KEYS")

    # Provider envs (optional)
    openai_compat_base_url: str = Field(default="", alias="OPENAI_COMPAT_BASE_URL")
    openai_compat_api_key: str = Field(default="", alias="OPENAI_COMPAT_API_KEY")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
