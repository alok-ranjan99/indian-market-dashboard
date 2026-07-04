"""Indian Market Dashboard (imd) — sentiment & swing-trading decision-support.

Package layout (mirrors docs/diagrams/lld.drawio):
    imd.domain    — dataclasses / value objects shared across layers
    imd.config    — env-driven settings (pydantic-settings)
    imd.data      — DataProvider interface + implementations, Cache, Store
    imd.sentiment — SentimentModel interface (FinBERT / VADER)
    imd.scoring   — Scorer interface + Fear/Greed, Bias, Swing scorers
    imd.screener  — technical indicators + candidate screener
    imd.alerts    — Notifier interface + AlertDispatcher (Telegram, Email)
    imd.ui        — Streamlit presentation (app shell, theme, tabs)
"""

__version__ = "0.1.0"
