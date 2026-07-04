"""Config loads with defaults and reads env overrides."""

from __future__ import annotations

from imd.config import Settings


def test_defaults() -> None:
    s = Settings()
    assert s.universe == "NIFTY50"
    assert 0.99 <= sum(vars(s.fear_greed_weights).values()) <= 1.01
    assert not s.telegram.enabled
    assert not s.email.enabled


def test_env_override(monkeypatch) -> None:
    monkeypatch.setenv("IMD_UNIVERSE", "NIFTY500")
    monkeypatch.setenv("IMD_TELEGRAM__BOT_TOKEN", "abc")
    monkeypatch.setenv("IMD_TELEGRAM__CHAT_ID", "123")
    s = Settings()
    assert s.universe == "NIFTY500"
    assert s.telegram.enabled is True
