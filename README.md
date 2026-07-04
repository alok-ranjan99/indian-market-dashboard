# 🇮🇳 Indian Market Sentiment & Swing-Trading Dashboard

![CI](https://github.com/alok-ranjan99/indian-market-dashboard/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A professional-grade, free-to-run dashboard that tracks daily Indian stock-market news,
scores market **fear vs. greed**, gauges **bullish/bearish** bias, ranks **hot sectors**,
and surfaces **swing-trade candidates** with built-in **risk management**.

> ⚠️ **Not financial advice.** This is a decision-support tool. No system can guarantee
> which stock rises today. It stacks *probabilities* in your favor and enforces risk
> discipline — which is what actually makes swing traders profitable.

## 🚦 Status
**Phase 3 — scaffold complete.** Runnable app shell (header, theme toggle, tab nav), the
interface-driven architecture, config, tests, and CI are in place. Feature tabs are wired
in later phases. See [`tasks/todo.md`](./tasks/todo.md) for the live roadmap and
[`PLAN.md`](./PLAN.md) for the full plan.

## ▶️ Quickstart
```bash
# 1. create a Python 3.11 env (uv shown; venv/pyenv also fine)
uv venv --python 3.11 .venv && source .venv/bin/activate

# 2. install (runtime + dev tooling)
uv pip install -e ".[dev]"          # add ".[ml]" for FinBERT, ".[ta]" for indicators

# 3. run the dashboard
streamlit run streamlit_app.py
```
Copy `.env.example` → `.env` to add news/alert credentials (all optional to run the shell).

## 🧱 Architecture
Interface-driven so new data sources, scorers, and alert channels drop in without rewrites
(see `docs/diagrams/`). Package layout under `src/imd/`:

| Module | Responsibility | Key seam |
|---|---|---|
| `domain/` | shared dataclasses (Quote, NewsItem, Candidate, Signal…) | — |
| `config.py` | env-driven settings (pydantic-settings) | — |
| `data/` | market/news acquisition + cache + store | `DataProvider` |
| `sentiment/` | financial-text sentiment | `SentimentModel` |
| `scoring/` | Fear/Greed, Bias, Swing (pure, explainable) | `Scorer` |
| `screener/` | technical indicators + candidate selection | — |
| `alerts/` | Telegram + email fan-out | `Notifier` + `AlertDispatcher` |
| `ui/` | Streamlit shell, theme, tabs | tab registry |

## 🧪 Dev
```bash
ruff check .      # lint
pytest -q         # tests
```

## 📚 Docs
- [`PLAN.md`](./PLAN.md) / [`plan.html`](./plan.html) — full master plan
- [`docs/design-system.md`](./docs/design-system.md) — color tokens & themes
- [`docs/diagrams/`](./docs/diagrams/) — HLD, LLD, data-flow (`.drawio`)
- [`prototype/index.html`](./prototype/index.html) — UI blueprint (open in a browser)
- [`docs/mcp-setup-guide.md`](./docs/mcp-setup-guide.md) — MCP setup

## License
MIT
