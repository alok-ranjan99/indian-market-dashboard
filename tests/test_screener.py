"""Screener + sentiment tests — pure, no network."""

from __future__ import annotations

import pandas as pd

from imd.domain import SectorPerf
from imd.screener import screen_candidates, sector_strength_map
from imd.sentiment import VaderModel


def _hist(n: int, start: float, step: float) -> pd.DataFrame:
    close = [start + step * i for i in range(n)]
    return pd.DataFrame({
        "Open": [c - 0.5 for c in close], "High": [c + 1 for c in close],
        "Low": [c - 1 for c in close], "Close": close, "Volume": [1000] * n,
    })


def test_screen_ranks_by_swing_score() -> None:
    histories = {
        "UP.NS": _hist(60, 100, 1.5),    # strong uptrend
        "DOWN.NS": _hist(60, 200, -1.5),  # downtrend
    }
    cands = screen_candidates(histories)
    assert [c.symbol for c in cands] == ["UP", "DOWN"]  # uptrend ranks first
    assert cands[0].swing.value > cands[1].swing.value


def test_screen_skips_short_and_empty() -> None:
    histories = {"SHORT.NS": _hist(5, 100, 1), "EMPTY.NS": pd.DataFrame()}
    assert screen_candidates(histories) == []


def test_screen_min_score_and_limit() -> None:
    histories = {f"S{i}.NS": _hist(60, 100, 1.0) for i in range(5)}
    cands = screen_candidates(histories, limit=3)
    assert len(cands) == 3
    high = screen_candidates(histories, min_score=999)
    assert high == []


def test_screen_populates_signals_and_ltp() -> None:
    cands = screen_candidates({"AAA.NS": _hist(60, 100, 1.0)})
    c = cands[0]
    assert c.ltp == 159.0  # last close of the ramp
    assert "setup" in c.signals and "rsi" in c.signals
    assert c.swing.risk_reward == 2.0


def test_sector_strength_map() -> None:
    sectors = [SectorPerf("NIFTY IT", 1.8, 95), SectorPerf("NIFTY BANK", -0.5, 40),
               SectorPerf("NIFTY UNKNOWN", 2.0, 99)]
    m = sector_strength_map(sectors)
    assert m == {"IT": 95, "Bank": 40}  # unknown index dropped


def test_vader_polarity() -> None:
    m = VaderModel()
    assert m.score("Stocks surge on strong earnings and record profits") > 0
    assert m.score("Market crashes as losses mount and fear spikes") < 0
    assert m.score("") == 0.0
    batch = m.score_batch(["great gains", "heavy losses"])
    assert batch[0] > 0 > batch[1]
