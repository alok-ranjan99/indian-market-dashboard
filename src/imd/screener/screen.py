"""Candidate screener — turns per-stock histories into ranked Candidates.

Pure over its inputs (histories dict + sector strengths + a news score), so it is fully
unit-testable with no network. The screener owns *selection*; SwingScorer owns *scoring*.
"""

from __future__ import annotations

import logging

import pandas as pd

from imd.domain import Candidate, SectorPerf
from imd.scoring import indicators as ind
from imd.scoring.swing import SwingScorer

logger = logging.getLogger(__name__)

# Map a Nifty sector index name → the constituent's sector tag (extended as needed).
_SECTOR_HINTS: dict[str, str] = {
    "NIFTY IT": "IT", "NIFTY BANK": "Bank", "NIFTY AUTO": "Auto",
    "NIFTY FMCG": "FMCG", "NIFTY PHARMA": "Pharma", "NIFTY METAL": "Metal",
    "NIFTY ENERGY": "Energy", "NIFTY REALTY": "Realty", "NIFTY PSU BANK": "PSU Bank",
}


def _setup_label(df: pd.DataFrame) -> str:
    if ind.is_breakout(df):
        return "Breakout"
    close = float(df["Close"].iloc[-1])
    sma20 = ind.sma(df["Close"], 20).dropna()
    if not sma20.empty and close < float(sma20.iloc[-1]):
        return "Pullback"
    return "Range"


def screen_candidates(
    histories: dict[str, pd.DataFrame],
    *,
    sector_strength: dict[str, float] | None = None,
    stock_sector: dict[str, str] | None = None,
    news_score: float = 50.0,
    min_score: float = 0.0,
    limit: int | None = None,
) -> list[Candidate]:
    """Score every stock with usable history and return Candidates ranked by swing score.

    Args:
        histories: {symbol: OHLCV DataFrame (oldest→newest)}.
        sector_strength: {sector_tag: 0-100}; defaults to neutral (50).
        stock_sector: {symbol: sector_tag} for the sector sub-score.
        news_score: per-stock news score (0-100); refined per-symbol in a later phase.
        min_score: drop candidates below this swing score.
        limit: keep only the top N after ranking.
    """
    scorer = SwingScorer()
    sector_strength = sector_strength or {}
    stock_sector = stock_sector or {}
    out: list[Candidate] = []

    for symbol, df in histories.items():
        if df is None or df.empty or len(df) < 20:
            continue
        try:
            sector = stock_sector.get(symbol, "—")
            strength = sector_strength.get(sector, 50.0)
            swing = scorer.score(df, sector_strength=strength, news_score=news_score)
        except Exception:  # noqa: BLE001 — one bad symbol must not sink the screen
            logger.exception("failed to score %s", symbol)
            continue
        if swing.value < min_score:
            continue
        rsi = ind.rsi(df["Close"]).dropna()
        out.append(
            Candidate(
                symbol=symbol.replace(".NS", ""),
                ltp=round(float(df["Close"].iloc[-1]), 2),
                swing=swing,
                sector=sector,
                signals={
                    "setup": _setup_label(df),
                    "rsi": f"{rsi.iloc[-1]:.0f}" if not rsi.empty else "—",
                    "rr": f"{swing.risk_reward:.1f}" if swing.risk_reward else "—",
                },
            )
        )

    out.sort(key=lambda c: c.swing.value, reverse=True)
    return out[:limit] if limit else out


def sector_strength_map(sectors: list[SectorPerf]) -> dict[str, float]:
    """Build {sector_tag: relative_strength} from NSE sector performance."""
    return {
        _SECTOR_HINTS[s.name]: s.relative_strength
        for s in sectors
        if s.name in _SECTOR_HINTS
    }
