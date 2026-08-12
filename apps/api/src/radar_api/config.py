from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Radar Tech IA"
    app_env: str = "development"
    public_app_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"

    database_url: str = "sqlite:///./radar.db"
    storage_dir: Path = Path("./storage")
    timezone: str = "America/Rio_Branco"

    openai_api_key: str | None = None
    openai_summary_model: str = "gpt-5-mini"
    openai_tts_model: str = "gpt-4o-mini-tts"
    openai_tts_voice_lia: str = "nova"
    openai_tts_voice_secondary: str = "onyx"

    evolution_api_url: str = "http://localhost:8080"
    evolution_api_key: str | None = None
    evolution_instance: str | None = None
    whatsapp_target_number: str | None = None

    daily_run_time: str = "07:00"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    return settings
