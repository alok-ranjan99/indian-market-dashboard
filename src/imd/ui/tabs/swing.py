"""Swing Candidates tab — screened shortlist with score + entry/stop/target."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from imd.ui import data


def render() -> None:
    st.info(
        "Screened **candidates** ranked by a transparent Swing Score — a shortlist for "
        "**your own review**, not buy calls. Each row shows entry / stop / target so you "
        "size risk first.",
        icon="🎯",
    )
    view = data.swing_view()
    if not view.candidates:
        st.warning("No candidates available right now (market data may be unavailable).")
        return

    rows = [
        {
            "Stock": c.symbol,
            "LTP": c.ltp,
            "Swing Score": round(c.swing.value, 1),
            "Setup": c.signals.get("setup", "—"),
            "RSI": c.signals.get("rsi", "—"),
            "Sector": c.sector,
            "Entry": c.swing.entry,
            "Stop": c.swing.stop,
            "Target": c.swing.target,
            "R:R": c.swing.risk_reward,
        }
        for c in view.candidates
    ]
    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Swing Score": st.column_config.ProgressColumn(
                "Swing Score", min_value=0, max_value=100, format="%d"
            ),
            "LTP": st.column_config.NumberColumn(format="₹%.2f"),
            "Entry": st.column_config.NumberColumn(format="₹%.2f"),
            "Stop": st.column_config.NumberColumn(format="₹%.2f"),
            "Target": st.column_config.NumberColumn(format="₹%.2f"),
            "R:R": st.column_config.NumberColumn(format="%.1f"),
        },
    )
    st.caption(
        "Swing Score = trend 25% · momentum 20% · volume 15% · breakout 20% · "
        "sector 10% · news 10%. Stop = 1.5×ATR below entry; target at 2:1."
    )
