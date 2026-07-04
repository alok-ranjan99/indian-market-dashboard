"""Streamlit app shell.

Phase 3 deliverable: a runnable skeleton — header, theme toggle, and the full tab
nav with placeholders — proving structure + theming before feature work.

Run locally:   streamlit run streamlit_app.py
"""

from __future__ import annotations

import streamlit as st

from imd import __version__
from imd.config import get_settings
from imd.ui.tabs import RENDERERS, TAB_REGISTRY
from imd.ui.theme import css_variables


def _init_state() -> None:
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"


def _render_header() -> None:
    settings = get_settings()
    left, right = st.columns([0.8, 0.2])
    with left:
        st.markdown("### 📈 IMD · Market Radar")
        st.caption(
            f"Indian Market Dashboard v{__version__} · universe: {settings.universe} · "
            "decision-support, **not financial advice**"
        )
    with right:
        is_dark = st.session_state.theme == "dark"
        if st.toggle("🌙 Dark", value=is_dark, key="theme_toggle"):
            st.session_state.theme = "dark"
        else:
            st.session_state.theme = "light"


def main() -> None:
    st.set_page_config(page_title="Indian Market Dashboard", page_icon="📈", layout="wide")
    _init_state()

    # Apply theme tokens before rendering content.
    st.markdown(css_variables(st.session_state.theme), unsafe_allow_html=True)

    _render_header()
    st.divider()

    labels = [label for _, label in TAB_REGISTRY]
    tabs = st.tabs(labels)
    for tab, (key, _label) in zip(tabs, TAB_REGISTRY, strict=True):
        with tab:
            RENDERERS[key]()


if __name__ == "__main__":
    main()
