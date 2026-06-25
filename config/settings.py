"""Application configuration."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "WORKPULSE AI"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-this-to-a-secure-random-key-in-production"
    jwt_secret_key: str = "change-this-jwt-secret-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    refresh_token_expire_days: int = 7

    database_url: str = "postgresql://workpulse:workpulse_secret@localhost:5432/workpulse_db"
    db_pool_size: int = 20
    db_max_overflow: int = 40

    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_base_url: str = "http://localhost:8000"
    streamlit_server_port: int = 8501

    work_start_hour: int = 9
    work_start_minute: int = 0
    late_threshold_minutes: int = 15
    standard_work_hours: float = 8.0
    overtime_threshold_hours: float = 8.0

    cors_origins: str = "http://localhost:8501,http://localhost:8000"
    csrf_secret: str = "change-this-csrf-secret"
    ai_insights_enabled: bool = True

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
