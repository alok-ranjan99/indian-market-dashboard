"""Reusable UI components (Plotly figures, formatters) built from theme tokens."""

from __future__ import annotations

import plotly.graph_objects as go

from imd.ui.theme import tokens


def fear_greed_gauge(value: float, label: str, theme: str = "dark") -> go.Figure:
    """Semicircular Fear/Greed gauge (red→amber→green) matching the prototype."""
    t = tokens(theme)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"font": {"size": 40, "color": t["text"]}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": t["muted"],
                         "tickfont": {"color": t["muted"], "size": 10}},
                "bar": {"color": "rgba(0,0,0,0)"},  # hide default bar; use steps + threshold
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 25], "color": t["bear"]},
                    {"range": [25, 45], "color": "#e8710a"},
                    {"range": [45, 55], "color": t["neutral"]},
                    {"range": [55, 75], "color": "#8bc34a"},
                    {"range": [75, 100], "color": t["bull"]},
                ],
                "threshold": {"line": {"color": t["text"], "width": 4},
                              "thickness": 0.85, "value": value},
            },
            title={"text": label, "font": {"size": 16, "color": t["text"]}},
        )
    )
    fig.update_layout(
        height=240, margin={"t": 40, "b": 10, "l": 20, "r": 20},
        paper_bgcolor="rgba(0,0,0,0)", font={"color": t["text"]},
    )
    return fig


def pct_color(value: float, theme: str = "dark") -> str:
    t = tokens(theme)
    if value > 0:
        return t["bull"]
    if value < 0:
        return t["bear"]
    return t["neutral"]


def fmt_pct(value: float) -> str:
    return f"{value:+.2f}%"


def fmt_inr_cr(value: float) -> str:
    return f"₹{value:,.0f} cr"
