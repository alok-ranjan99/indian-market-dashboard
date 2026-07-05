"""Streamlit app shell — header, theme toggle, refresh, and the tab nav.

Run locally:   streamlit run streamlit_app.py
"""

from __future__ import annotations

import streamlit as st

from imd import __version__
from imd.config import get_settings
from imd.ui import data
from imd.ui.tabs import RENDERERS, TAB_REGISTRY
from imd.ui.theme import css_variables


def _init_state() -> None:
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"


def _render_header() -> str:
    """Render header + controls and return the (possibly just-toggled) theme."""
    settings = get_settings()
    left, right = st.columns([0.8, 0.2])
    with left:
        st.markdown("### 📈 IMD · Market Radar")
        st.caption(
            f"Indian Market Dashboard v{__version__} · universe: {settings.universe} · "
            "decision-support, **not financial advice**"
        )
    with right:
        # Read the toggle's value on THIS run so CSS (injected after) uses the new theme.
        dark = st.toggle("🌙 Dark", value=(st.session_state.theme == "dark"))
        st.session_state.theme = "dark" if dark else "light"
        if st.button("🔄 Refresh data", use_container_width=True):
            data.clear_all()
            st.rerun()
    return st.session_state.theme


def main() -> None:
    st.set_page_config(page_title="Indian Market Dashboard", page_icon="📈", layout="wide")
    _init_state()

    # Render header first so the theme toggle is processed, THEN inject CSS (global <style>
    # applies regardless of DOM position) so the selected theme takes effect this run.
    theme = _render_header()
    st.markdown(css_variables(theme), unsafe_allow_html=True)
    st.divider()

    labels = [label for _, label in TAB_REGISTRY]
    tabs = st.tabs(labels)
    for tab, (key, _label) in zip(tabs, TAB_REGISTRY, strict=True):
        with tab:
            RENDERERS[key]()


if __name__ == "__main__":
    main()
