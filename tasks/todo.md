# Project TODO — Indian Market Dashboard

> Convention (Alok's working-style playbook): plan here with checkable items, verify plan
> before implementing, mark complete as we go, add a Review entry at the end of each phase,
> capture corrections in `tasks/lessons.md`.
>
> **Flow:** Design blueprint → scaffold + repo → data layer → build tabs (design-driven) →
> risk/journal → deploy + alerts → backtest. We don't write feature code until the blueprint
> and the data contracts are signed off.

Legend: `[ ]` todo · `[x]` done · ⛳ = phase gate (get sign-off before moving on)

---

## Phase 0 — Foundations ✅ (done)
- [x] Project folder + structure
- [x] Master plan (`PLAN.md`) + HTML plan (`plan.html`)
- [x] MCP setup guide + **all 5 MCPs connected** (github, fetch, playwright, figma, sequential-thinking)
- [x] Memory saved (user profile, project, working-style playbook)
- [x] `tasks/todo.md` + `tasks/lessons.md` established

---

## Phase 1 — Architecture Diagrams: HLD & LLD 📐  ⛳
*Goal: agree the system design on paper (draw.io) BEFORE UI or code. Deliverables are
versioned `.drawio` files in `docs/diagrams/`, editable by Alok in draw.io.*
- [x] Decide draw.io approach: **generate `.drawio` XML files** (version-controlled) — MCP live-edit optional later
- [x] **HLD** — system architecture (`docs/diagrams/hld.drawio`) — ✅ reviewed & approved by Alok
- [x] **LLD** — module/class design (`docs/diagrams/lld.drawio`): packages, interfaces (DataProvider,
      Scorer, Notifier), classes, domain dataclasses, relationships — delivered
- [x] **Data-flow diagram** (`docs/diagrams/data-flow.drawio`): cron → fetch → normalize → persist →
      sentiment → score → signals → (alert branch / UI render / history→backtest) — delivered
- [ ] ⛳ **Review & sign off** LLD + data-flow (HLD already approved)

## Phase 2 — Design & UI Blueprint 🎨  ⛳
*Goal: know how every screen looks BEFORE feature code. Path = coded HTML prototype.*
- [x] Define **design system**: tokens for bull/bear/neutral + fear→greed scale + chart palette,
      **both dark & light** — `docs/design-system.md`
- [x] **Information architecture**: 6 tabs + global header + pre-market briefing (finalized in prototype)
- [x] **HTML prototype** of every screen — `prototype/index.html` (Market Pulse, News & Sentiment,
      Sector Rotation, Swing Candidates, Risk & Sizing, Journal + header ticker + event radar)
- [x] Theme toggle (dark ⇄ light) — working + verified via Playwright, both themes screenshotted
- [x] Verified in-browser: all tabs render, gauge/tables/calculator work, no real console errors
      (screenshots in `prototype/screenshots/`)
- [ ] Map each UI element → its data source + refresh cadence (design ↔ data contract) — do at Phase 3 boundary
- [ ] ⛳ **Review & sign off** the blueprint (open `prototype/index.html`)

## Phase 3 — Scaffold & Repo 🏗️  ✅ DONE
*Goal: a clean, professional skeleton pushed to GitHub with CI green on an empty app.*
- [x] Project structure: `src/imd/` (domain, data, sentiment, scoring, screener, alerts, ui/tabs), `tests/`, `.streamlit/`
- [x] `pyproject.toml` + `requirements.txt`; Python 3.11 venv (uv). Extras: `[dev]`, `[ml]` (FinBERT), `[ta]` (indicators)
- [x] `.gitignore`, `.env.example`, `config.py` (pydantic-settings, IMD_ env prefix), secrets never committed
- [x] `.streamlit/config.toml` (dark base) + runtime theme tokens in `ui/theme.py` (dark + light)
- [x] Interface seams from LLD: `DataProvider`, `SentimentModel`, `Scorer`, `Notifier` + `AlertDispatcher`
- [x] **PUBLIC repo**: https://github.com/alok-ranjan99/indian-market-dashboard (pushed via `gh`)
- [x] Runnable Streamlit shell (header + dark/light toggle + 6-tab nav) — booted headless, HTTP 200
- [x] **CI green**: GitHub Actions (ruff + 9 pytest + import check) — verified passing
- [x] README with badges + quickstart + architecture table
- [x] ⛳ **Review**: repo live (public), CI green, app shell verified locally ✅

## Phase 4 — Data Layer 📡  ⛳
*Goal: reliable, cached, tested access to every input the dashboard needs.*
- [ ] `data/prices.py` (yfinance): Nifty 50 constituents, Nifty, Bank Nifty, India VIX
- [ ] `data/nse.py`: sectoral indices, FII/DII flows, option chain / PCR (Playwright MCP for blocked pages)
- [ ] `data/news.py`: RSS (Moneycontrol/ET/Livemint/BS) + NewsAPI, dedup + normalize
- [ ] `data/global_cues.py`: Dow/Nasdaq, GIFT Nifty, crude, USD/INR
- [ ] Caching layer (Streamlit cache + on-disk) + graceful fallbacks / rate-limit handling
- [ ] SQLite schema + writers for daily history (enables later backtest)
- [ ] Unit tests + a "data health" check script
- [ ] ⛳ **Review**: one command pulls a full day's data snapshot

## Phase 5 — Scoring Engine 🧮  ⛳
*Built as pure, testable functions BEFORE wiring to UI (transparent, no black box).*
- [ ] Fear/Greed score (VIX 25% + breadth 20% + news sentiment 20% + momentum 20% + PCR 15%)
- [ ] Daily Bias (trend vs 20/50 DMA + FII/DII + Fear/Greed + global-cues gap) w/ reasons + confidence
- [ ] Per-stock Swing Score (trend 25 / momentum 20 / volume 15 / breakout 20 / sector 10 / news 10)
- [ ] Each score returns a **breakdown** (the "why") for UI display
- [ ] Golden-file unit tests on known inputs
- [ ] ⛳ **Review**: scores reproducible + explainable

## Phase 6 — Build Tabs (design-driven) 🖥️
*Port the Phase 1 blueprint into Streamlit, one screen at a time.*
- [ ] Tab 1 — **Market Pulse**: Fear/Greed gauge, Bias card w/ reasons, Nifty/BankNifty/VIX/FII-DII
- [ ] Tab 2 — **News & Sentiment**: FinBERT scoring, scored feed, trend chart, daily summary
- [ ] Tab 3 — **Sector Rotation**: heatmap + relative-strength ranking + sentiment overlay
- [ ] Tab 4 — **Swing Candidates**: screener table, Swing Score, entry/stop/target (ATR), R:R
- [ ] Global header: live indices ticker + pre-market briefing + event/expiry flags
- [ ] ⛳ **Review**: hero screens match blueprint

## Phase 7 — Risk, Sizing & Journal 🛡️
- [ ] Position-size calculator (capital + risk% → shares), stop/target calc, portfolio risk view
- [ ] Trade journal (SQLite): log trades, win rate, avg P/L
- [ ] Discipline checklist + "avoid list" (bad news / circuit / high risk)

## Phase 8 — Deploy + Alerts 🚀  ⛳
- [ ] Deploy to **Streamlit Community Cloud** (secrets via dashboard, not repo)
- [ ] **Alerts from the start**: Telegram bot (BotFather token + chat ID) **+** email (SMTP) on strong signals
- [ ] **GitHub Actions cron** for daily pre-market data refresh + alert push
- [ ] ⛳ **Review**: live URL works on phone; both Telegram + email fire on a test signal

## Phase 9 — Backtest & Refine 📈
- [ ] Backtest Swing Score / Bias vs realized next-N-day moves on stored history
- [ ] Tune weights; report hit-rate + expectancy honestly
- [ ] Iterate scoring based on results

---

## Decisions — LOCKED (2026-07-04)
1. ✅ **Design path** — coded **HTML prototype** for UI + **draw.io `.drawio` XML** for HLD/LLD (version-controlled). Draw.io MCP (`drawio-mcp-server`) available for optional live editing later; not required.
2. ✅ **Alerts** — **Telegram + email from the start**.
3. ✅ **GitHub repo** — `indian-market-dashboard`, **public** (can flip to private later).
4. ✅ **Theme** — **both dark & light**, user-toggleable in the app.
5. ✅ **Universe** — Nifty 50 to ship; design UI to scale to Nifty 500 later.

6. ✅ **Accent/palette** — **standard finance palette** (green=bull, red=bear, amber=neutral). Tokens in `docs/design-system.md`.

## Open decisions (minor, can decide during the phase)
- Telegram: create the bot now (BotFather) or when we reach Phase 8? (token needed only at alert wiring)

---

## Review log
- 2026-07-04 — Phase 0 complete. Plan (MD+HTML), MCP guide, memory, task scaffolding done.
- 2026-07-04 — Fixed fetch MCP (was wrong npm pkg; now `uvx mcp-server-fetch`). All 5 MCPs connected.
- 2026-07-04 — Revised roadmap to **design-first**; split Scoring Engine into its own testable phase.
- 2026-07-04 — Reordered to put **HLD/LLD (Phase 1, draw.io)** before UI blueprint (Phase 2). Locked all 5 setup decisions. Chose versioned `.drawio` XML over live draw.io MCP for architecture docs. Delivered **HLD v1** (`docs/diagrams/hld.drawio`, valid XML) for review.
- 2026-07-04 — HLD **approved** by Alok. Delivered **LLD** (`lld.drawio`) + **data-flow** (`data-flow.drawio`), both valid XML. Locked palette = standard finance (green/red/amber); tokens for dark+light in `docs/design-system.md`. Next gate: sign off LLD + data-flow, then Phase 2 (UI blueprint).
- 2026-07-04 — LLD + data-flow **approved**. Standing directive saved: build like a senior architect, flexible & scalable. Delivered **Phase 2 UI blueprint** `prototype/index.html` — all 6 tabs, both themes, finance palette, Fear/Greed gauge, swing screener, risk calc. **Verified in-browser via Playwright** (both themes, tabs, no real errors); screenshots in `prototype/screenshots/`. Awaiting blueprint sign-off → then Phase 3 (scaffold + public repo).
- 2026-07-05 — Prototype **approved**. **Phase 3 complete**: interface-driven `src/imd` scaffold, config, tests, Streamlit shell. Verified locally (ruff clean, 9/9 pytest, app boots HTTP 200). Pushed to **public repo** alok-ranjan99/indian-market-dashboard; **CI green**. Next: Phase 4 (data layer).
