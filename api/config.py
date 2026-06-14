"""Загрузка настроек из .env."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Primary — 302.ai
    llm_primary_base_url: str = "https://api.302.ai/v1"
    llm_primary_api_key: str = ""
    llm_primary_model: str = "gpt-4o-mini"
    llm_primary_embed_model: str = "text-embedding-3-small"

    # Fallback — MAI Qwen
    llm_fallback_base_url: str = ""
    llm_fallback_api_key: str = ""
    llm_fallback_model: str = "qwen2.5-72b-instruct"
    llm_fallback_embed_model: str = "qwen-embedding"

    # Роли моделей (используют primary base_url+key)
    llm_fast_model: str = "gpt-4.1-mini"
    llm_deep_model: str = "gpt-5"
    llm_search_model: str = "sonar-pro"

    # Storage
    paideia_db_path: str = "db/paideia.db"
    paideia_content_dir: str = "content"
    paideia_raw_dir: str = "raw"

    # Auth
    auth_secret: str = "change-me"
    auth_token_lifetime_seconds: int = 3600

    log_level: str = "INFO"

    # F12: ЮKassa
    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    yookassa_return_url: str = ""

    # F12: СБП
    sbp_phone: str = ""
    sbp_bank_name: str = ""
    sbp_holder_name: str = ""

    # F12: Тинькофф donate-страница (tbank.ru/cf/... или tinkoff.ru/cf/...)
    tinkoff_donate_url: str = ""

    # F11: bypass-код для тестеров (раздаёшь руками). Пусто = выкл.
    # Несколько кодов через запятую: BYPASS_CODES=test1,test2,vip
    bypass_codes: str = ""

    @property
    def db_path(self) -> Path:
        return ROOT / self.paideia_db_path

    @property
    def content_dir(self) -> Path:
        return ROOT / self.paideia_content_dir

    @property
    def raw_dir(self) -> Path:
        return ROOT / self.paideia_raw_dir


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
