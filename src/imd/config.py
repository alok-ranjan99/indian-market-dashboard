"""Env-driven configuration (pydantic-settings).

Everything the app needs to run is here, with sensible defaults so the shell runs
with zero configuration. Secrets/keys come from the environment or a .env file,
prefixed with IMD_ (nested settings use __ , e.g. IMD_TELEGRAM__BOT_TOKEN).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScoringWeights(BaseModel):
    """Weights for the Fear/Greed composite (must sum to ~1.0)."""

    vix: float = 0.25
    breadth: float = 0.20
    news: float = 0.20
    momentum: float = 0.20
    pcr: float = 0.15


class SwingWeights(BaseModel):
    """Weights for the per-stock Swing Score."""

    trend: float = 0.25
    momentum: float = 0.20
    volume: float = 0.15
    breakout: float = 0.20
    sector: float = 0.10
    news: float = 0.10


class TelegramConfig(BaseModel):
    bot_token: str = ""
    chat_id: str = ""

    @property
    def enabled(self) -> bool:
        return bool(self.bot_token and self.chat_id)


class EmailConfig(BaseModel):
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    from_addr: str = ""
    to_addr: str = ""

    @property
    def enabled(self) -> bool:
        return bool(self.username and self.password and self.to_addr)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="IMD_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Universe & thresholds
    universe: str = "NIFTY50"
    signal_threshold: float = 70.0  # min swing score to raise an alert

    # Data
    news_api_key: str = ""
    cache_ttl_seconds: int = 900

    # Weights
    fear_greed_weights: ScoringWeights = Field(default_factory=ScoringWeights)
    swing_weights: SwingWeights = Field(default_factory=SwingWeights)

    # Alerts
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)


@lru_cache
def get_settings() -> Settings:
    """Cached singleton so we parse the environment once per process."""
    return Settings()
