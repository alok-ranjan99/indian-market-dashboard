"""Tab renderers + registry. Adding a tab is a one-line change here.

Market Pulse and Swing Candidates are live (Phase 6 pass 1); the rest are placeholders
until pass 2. Each renderer is a zero-arg ``render()`` that pulls its own cached data.
"""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from imd.ui.tabs import market_pulse, swing

# (key, label) — order defines nav order.
TAB_REGISTRY: list[tuple[str, str]] = [
    ("pulse", "📊 Market Pulse"),
    ("news", "📰 News & Sentiment"),
    ("sector", "🔥 Sector Rotation"),
    ("swing", "🎯 Swing Candidates"),
    ("risk", "🛡️ Risk & Sizing"),
    ("journal", "📈 Journal"),
]


def _placeholder(title: str, blurb: str) -> Callable[[], None]:
    def render() -> None:
        st.subheader(title)
        st.info(blurb)
        st.caption("Coming in Phase 6 pass 2.")
    return render


RENDERERS: dict[str, Callable[[], None]] = {
    "pulse": market_pulse.render,
    "news": _placeholder(
        "News & Sentiment", "Auto-scored headlines, sentiment trend, daily summary."
    ),
    "sector": _placeholder(
        "Sector Rotation", "Sector heatmap and momentum/relative-strength ranking."
    ),
    "swing": swing.render,
    "risk": _placeholder(
        "Risk & Sizing", "Position-size calculator and a trading-discipline checklist."
    ),
    "journal": _placeholder(
        "Journal", "Trade log with win-rate/expectancy stats feeding the backtest loop."
    ),
}
