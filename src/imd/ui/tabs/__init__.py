"""Tab renderers. Each is a pure `render(ctx)` function so the app shell stays thin.

Phase 3 ships placeholders; real content lands in Phase 6, wired to the scoring
engine and data layer. The tab registry below drives the nav so adding a tab is a
one-line change.
"""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

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
        st.caption("Placeholder — wired up in a later phase.")
    return render


RENDERERS: dict[str, Callable[[], None]] = {
    "pulse": _placeholder(
        "Market Pulse",
        "Fear/Greed meter, daily bias, key indices, FII/DII flows, global cues.",
    ),
    "news": _placeholder(
        "News & Sentiment",
        "Auto-scored headlines, sentiment trend, and a daily market summary.",
    ),
    "sector": _placeholder(
        "Sector Rotation",
        "Sector heatmap and momentum/relative-strength ranking.",
    ),
    "swing": _placeholder(
        "Swing Candidates",
        "Screened shortlist with a transparent Swing Score and entry/stop/target.",
    ),
    "risk": _placeholder(
        "Risk & Sizing",
        "Position-size calculator and a trading-discipline checklist.",
    ),
    "journal": _placeholder(
        "Journal",
        "Trade log with win-rate/expectancy stats feeding the backtest loop.",
    ),
}
