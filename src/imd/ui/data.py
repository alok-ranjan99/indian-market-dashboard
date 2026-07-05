"""Cached data access for the UI.

Thin Streamlit-caching layer over the framework-agnostic service. Each view is cached
with a TTL so reruns (and st.tabs' eager rendering) don't refetch, and the pre-market
cron warms these the same way. Cache-clearing is exposed for a manual refresh button.
"""

from __future__ import annotations

import streamlit as st

from imd import service


@st.cache_data(ttl=600, show_spinner="Fetching latest news…")
def news_view() -> service.NewsView:
    return service.assemble_news()


@st.cache_data(ttl=900, show_spinner="Loading sectors…")
def sector_view() -> service.SectorView:
    return service.assemble_sectors()


@st.cache_data(ttl=900, show_spinner="Scoring the market…")
def market_view() -> service.MarketView:
    return service.assemble_market(news=news_view())


@st.cache_data(ttl=1800, show_spinner="Screening swing candidates…")
def swing_view() -> service.SwingView:
    return service.assemble_swing(sectors=sector_view())


def clear_all() -> None:
    """Drop all cached views (used by the header refresh button)."""
    for fn in (news_view, sector_view, market_view, swing_view):
        fn.clear()
