"""Market Pulse tab — Fear/Greed gauge, daily bias, indices, flows, global cues."""

from __future__ import annotations

import streamlit as st

from imd.domain import BiasLabel
from imd.ui import data
from imd.ui.components import fear_greed_gauge, fmt_inr_cr, fmt_pct

_BIAS_STYLE = {
    BiasLabel.BULLISH: ("Bullish", "imd-up"),
    BiasLabel.BEARISH: ("Bearish", "imd-down"),
    BiasLabel.NEUTRAL: ("Neutral", "imd-flat"),
}


def render() -> None:
    theme = st.session_state.get("theme", "dark")
    view = data.market_view()

    gauge_col, bias_col = st.columns([1, 1.2])
    with gauge_col:
        st.markdown("**Fear & Greed Index** · composite")
        st.plotly_chart(
            fear_greed_gauge(view.fear_greed.value, view.fear_greed.label or "", theme),
            use_container_width=True, config={"displayModeBar": False},
        )
        if view.fear_greed.breakdown:
            st.caption(" · ".join(f"{k} {v:.0f}" for k, v in view.fear_greed.breakdown.items()))

    with bias_col:
        st.markdown("**Today's Bias** · probability, not a guarantee")
        text, css = _BIAS_STYLE[view.bias.label]
        st.markdown(
            f"<span class='{css}' style='font-size:1.9rem;font-weight:700'>{text}</span>"
            f"&nbsp;&nbsp;<span style='font-size:1.2rem'>{view.bias.confidence:.0%} confidence</span>",
            unsafe_allow_html=True,
        )
        for reason in view.bias.reasons:
            st.markdown(f"- {reason}")

    st.divider()
    st.markdown("**Key Indices & Flows**")
    cols = st.columns(5)
    for col, (label, vals) in zip(cols, view.indices.items(), strict=False):
        col.metric(label, f"{vals['price']:,.2f}", fmt_pct(vals["change_pct"]))
    if view.flows:
        idx = len(view.indices)
        if idx < 5:
            cols[idx].metric("FII (₹cr)", fmt_inr_cr(view.flows.get("FII", 0)))
        if idx + 1 < 5:
            cols[idx + 1].metric("DII (₹cr)", fmt_inr_cr(view.flows.get("DII", 0)))

    if view.global_cues:
        st.divider()
        st.markdown("**Global Cues** · morning tone-setters")
        gcols = st.columns(len(view.global_cues))
        for col, (label, vals) in zip(gcols, view.global_cues.items(), strict=True):
            col.metric(label, f"{vals['price']:,.2f}", fmt_pct(vals["change_pct"]))

    st.caption("Decision-support only — not financial advice. Scores are probabilities.")
