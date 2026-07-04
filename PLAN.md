# Indian Market Sentiment & Swing-Trading Dashboard — Master Plan

**Project folder:** `~/Documents/Projects/indian-market-dashboard`
**Created:** 2026-07-04
**Owner:** Alok
**Status:** Planning → awaiting your confirmation before build

---

## 0. Read this first — an honest reality check

You asked for a dashboard that can:
1. Track daily Indian stock-market news ✅ **Fully possible**
2. Score market fear vs. happiness (sentiment) ✅ **Fully possible**
3. Say whether the market will be bearish/bullish today ⚠️ **Possible as a *probability signal*, not a guarantee**
4. Predict *which sector* will move ⚠️ **Possible as a *ranking of momentum*, not certainty**
5. Predict *which specific stock* will rise 4–10% today ❌ **Not reliably predictable by anyone**

### Why point 5 is impossible to *guarantee* (and what we do instead)
No system on earth — including billion-dollar hedge funds with satellite data and PhD quants — can reliably tell you "Stock X will go up 4–10% today." If such a system existed, its owner would quietly become the richest person alive, not sell it.

Markets are driven by unpredictable events (news shocks, global cues, institutional orders, geopolitics). What professionals actually build is a **decision-support system**: it stacks *probabilities* in your favor by combining sentiment + technicals + news + momentum, then surfaces **candidates worth your own review**. You still make the final call and manage risk.

**So the goal of this project is reframed honestly:**
> Build a professional-grade dashboard that gives you a daily, data-driven *edge* — a shortlist of high-probability swing candidates with clear reasoning — while enforcing risk management so your winners outweigh your losers over time.

This is what actually makes swing traders profitable. A "predict the winner" toy makes people lose money. We're building the former.

---

## 1. Is it possible? — Feasibility summary

| Feature | Feasible? | How |
|---|---|---|
| Daily Indian news aggregation | ✅ Yes | RSS feeds (Moneycontrol, ET Markets, Livemint, Business Standard) + NewsAPI free tier |
| Fear/Greed sentiment score (0–100) | ✅ Yes | NLP sentiment on news headlines + India VIX + market breadth + put/call ratio |
| Bullish/Bearish daily bias | ✅ Yes (as probability) | Nifty/BankNifty trend + breadth + sentiment + FII/DII flows |
| Sector rotation / hot sectors | ✅ Yes | Sectoral indices performance ranking + relative strength |
| Swing-trade stock candidates | ✅ Yes (as shortlist) | Technical screen (RSI, MACD, volume, breakout) + sentiment overlay |
| "Guaranteed 4–10% today" | ❌ No | Nobody can. We give probabilities + risk management instead |

**Verdict: The dashboard is very buildable and genuinely useful.** We just set honest expectations on the prediction parts.

---

## 2. MCPs & Tools required (your explicit ask)

MCP = "Model Context Protocol" servers — plug-ins that let me (Claude Code) directly control external tools. Below is what's *useful*, what's *optional*, and honest notes on each.

### 2.1 MCPs that genuinely help this project

| MCP / Tool | Purpose | Cost | Priority |
|---|---|---|---|
| **GitHub MCP** | Host code, version control, backups, deploy hooks | Free | ⭐ High |
| **Filesystem MCP** | Let me read/write project files directly (already effectively available) | Free | ⭐ High |
| **Figma MCP** | Design the dashboard UI/mockups before coding | Free tier | 🔸 Optional (nice-to-have) |
| **Fetch / Web MCP** | Pull live web pages, news, NSE data during dev | Free | ⭐ High |
| **Puppeteer/Playwright MCP** | Scrape sites that lack APIs (e.g., some NSE pages) | Free | 🔸 Optional |
| **Sequential-Thinking MCP** | Helps me reason through complex scoring logic | Free | 🔹 Low |

### 2.2 Honest note on MCPs
For *this* project, you don't strictly need many MCPs to get a working dashboard — the app itself talks to data APIs directly in Python. MCPs mainly help **me build it faster** and help **you manage the project** (GitHub for code, Figma for design). We can start with **GitHub only** and add others if needed. I'll set these up with you when we build.

### 2.3 Services / accounts we'll actually use (the important list)

| Service | Role | Free tier? | Notes |
|---|---|---|---|
| **GitHub** | Code hosting + version control | ✅ Free | Create one repo |
| **Streamlit Community Cloud** | Free hosting for the dashboard (open from phone/anywhere) | ✅ Free | Easiest deploy for Python dashboards |
| **Render.com / Railway** | Alt free host for background jobs (fetch news daily) | ✅ Free tier | For scheduled data pulls |
| **yfinance (Yahoo Finance)** | Free Indian stock + index price data | ✅ Free | Good enough to start; ~15min delayed |
| **NSE India public data** | Sectoral indices, F&O, option chain, FII/DII | ✅ Free | Public endpoints; scrape politely |
| **NewsAPI.org** | News headlines aggregation | ✅ Free tier | 100 req/day free |
| **RSS feeds** | Moneycontrol / ET / Livemint / BS news | ✅ Free | No key needed |
| **Hugging Face model** (FinBERT) | Financial-news sentiment scoring | ✅ Free | Runs locally or via free inference |
| **India VIX** | The market "fear index" (via NSE/yfinance) | ✅ Free | Core input to fear score |
| **Figma** | UI design/mockups | ✅ Free tier | Optional |
| *(Later / paid upgrades)* | | | |
| Zerodha Kite Connect | Real-time pro data | ~₹2000/mo | Optional upgrade |
| OpenAI/Anthropic API | LLM-based news summarization & sentiment | Pay-as-go | Optional upgrade for smarter analysis |

---

## 3. Tech stack (chosen for a free, fast, professional build)

| Layer | Technology | Why |
|---|---|---|
| Language | **Python 3.11** | Best for finance data + fastest to build |
| Dashboard UI | **Streamlit** | Professional dashboards with minimal code; free hosting |
| Data — prices | yfinance + NSE endpoints | Free Indian market data |
| Data — news | RSS + NewsAPI + `feedparser` | Free daily news |
| Sentiment NLP | **FinBERT** (Hugging Face) / VADER fallback | Purpose-built for financial text |
| Technicals | `pandas-ta` / `ta` library | RSI, MACD, Bollinger, ATR, breakouts |
| Charts | Plotly | Interactive, pro-looking |
| Storage | SQLite (local) → Postgres (if cloud) | Store daily history for backtesting |
| Scheduler | Streamlit cache + cron / GitHub Actions | Auto-refresh data daily |
| Hosting | Streamlit Cloud (free) | Access from anywhere incl. phone |
| Code host | GitHub | Version control + deploy |

---

## 4. What the dashboard will include (the fun part)

Organized as tabs/sections. Everything below is buildable on free tiers.

### 📊 Tab 1 — Market Pulse (top of dashboard)
- **Fear & Greed Meter (0–100 gauge):** Big dial showing today's market emotion. Inputs: India VIX, market breadth (advances/declines), put/call ratio, news sentiment, momentum. Green = greed/bullish, Red = fear/bearish.
- **Today's Bias card:** "Bullish / Neutral / Bearish" with a confidence % and the *reasons why* (transparent, not a black box).
- **Nifty 50 & Bank Nifty** live-ish snapshot: price, % change, trend arrow.
- **India VIX** with interpretation ("Fear rising / calm").
- **FII/DII flows** (foreign & domestic institutional buying/selling) — huge for Indian market direction.

### 📰 Tab 2 — News & Sentiment
- Live feed of top Indian market news (headlines + source + time).
- Each headline **auto-scored** positive / neutral / negative.
- **Sentiment trend chart** over the day/week.
- Filter by: whole market / specific sector / specific stock.
- Auto-generated **daily summary** ("What's moving the market today").

### 🔥 Tab 3 — Sector Rotation
- Heatmap of all NSE sectoral indices (IT, Banks, Auto, Pharma, FMCG, Metal, Energy, Realty…).
- Ranked table: today's % change + relative strength + momentum score.
- **"Hot sectors today"** highlight — where money is flowing.
- Sector sentiment (news-driven) overlay.

### 🎯 Tab 4 — Swing Candidates (the shortlist)
- Screener output: stocks passing a technical + sentiment filter.
- For each candidate: RSI, MACD signal, volume spike, breakout status, sentiment, sector strength.
- **A transparent "Swing Score"** (0–100) combining all signals — *not* a promise, a ranking.
- Suggested **entry zone, stop-loss, and target** based on ATR/support-resistance (so you know your risk before entering).
- Risk/reward ratio shown for each.

### 🛡️ Tab 5 — Risk & Position Sizing (this is what makes you profitable)
- Position-size calculator: given your capital + risk-per-trade %, how many shares to buy.
- Stop-loss & target calculator.
- Portfolio risk overview.
- Trading rules checklist (discipline > prediction).

### 📈 Tab 6 — Journal & Backtest (grow over time)
- Log your actual trades; track win rate, avg profit, avg loss.
- The dashboard stores daily signals so we can **backtest** whether the Swing Score actually works — and improve it. This is the professional feedback loop.

### ⚙️ Extras I'd recommend adding (my ideas for your strategy)
- **Global cues panel:** US markets (Dow/Nasdaq), SGX Nifty/GIFT Nifty, crude oil, USD/INR — these set the morning tone for Indian markets.
- **Event calendar:** RBI meets, earnings dates, budget, expiry days — avoid trading blind into big events.
- **Options data signals:** PCR (put-call ratio), max pain, OI buildup — advanced but powerful for direction.
- **Alerts:** email/Telegram ping when a strong signal appears (free via Telegram bot).
- **"Avoid list":** stocks with bad news / circuit limits / high risk today.
- **Pre-market briefing:** one-screen morning summary at 9:00 AM before market opens at 9:15.

---

## 5. How the scoring actually works (transparency, no black box)

### Fear/Greed Score (0–100)
Weighted blend of:
- India VIX (inverted) — 25%
- Market breadth (advances vs declines) — 20%
- News sentiment (FinBERT) — 20%
- Nifty momentum (vs moving averages) — 20%
- Put/Call ratio — 15%

### Daily Bias (Bullish/Neutral/Bearish)
- Nifty & Bank Nifty trend vs 20/50 DMA
- FII/DII net flow direction
- Fear/Greed score
- Global cues (SGX/GIFT Nifty gap)
→ Combined into a probability, shown with reasoning.

### Swing Score per stock (0–100)
- Trend alignment (price vs MAs) — 25%
- Momentum (RSI, MACD) — 20%
- Volume confirmation — 15%
- Breakout/setup quality — 20%
- Sector strength — 10%
- News sentiment — 10%

**Every number shows *why* it is what it is.** You'll never see a mystery signal.

---

## 6. Build roadmap (phased — you see progress fast)

| Phase | What we build | Outcome |
|---|---|---|
| **Phase 0** | Project setup, GitHub repo, folder structure, this plan | Foundation ready |
| **Phase 1** | Data layer: fetch prices, indices, news, VIX (free sources) | Data flowing |
| **Phase 2** | Market Pulse tab: Fear/Greed meter + bias card | First visible dashboard |
| **Phase 3** | News & Sentiment tab with FinBERT scoring | Sentiment working |
| **Phase 4** | Sector Rotation + Swing Candidates screener | Core trading value |
| **Phase 5** | Risk calculator + Journal | Profitability tools |
| **Phase 6** | Deploy to Streamlit Cloud (free) — access anywhere | Live dashboard |
| **Phase 7** | Backtesting + refine scoring + alerts | Continuous improvement |

We build incrementally — you'll have something usable by Phase 2, not after months.

---

## 7. Requirements checklist (what YOU need to provide)

### Accounts to create (all free)
- [ ] GitHub account (for code)
- [ ] Streamlit Community Cloud account (free hosting — sign in with GitHub)
- [ ] NewsAPI.org free API key
- [ ] (Optional) Figma account for design
- [ ] (Optional) Telegram account for alerts
- [ ] (Optional later) Broker API (Zerodha/Upstox/Dhan) for pro data

### On your machine (I'll help install)
- [ ] Python 3.11+
- [ ] The project dependencies (I'll create `requirements.txt`)

### Decisions — CONFIRMED (2026-07-04)
- [x] **Skill level:** Experienced software engineer → peer-to-peer collaboration, architecture + code
- [x] **Budget:** Free-first with a documented paid upgrade path
- [x] **Hosting:** Both — local first, then free cloud (Streamlit Cloud)
- [x] **Broker:** None yet → free data sources; add broker API later
- [x] **Stock universe:** Nifty 50 to start
- [x] **Alerts:** Yes — Telegram + email
- [x] **Deliverables:** step-by-step MCP setup guide + HTML plan doc (openable locally)

---

## 8. Important disclaimers (please read)
- This dashboard is a **decision-support tool**, not financial advice.
- No signal guarantees profit. Markets carry real risk of loss.
- The 4–10% swing target is *achievable on winning trades*, but **not on every trade** — profitability comes from good risk management (cutting losses small, letting winners run), not from prediction accuracy.
- Always use stop-losses. Never risk more than 1–2% of capital per trade.
- Past performance / backtests don't guarantee future results.

---

## 9. My open questions for you
1. **Skill level, budget, hosting, broker** — the 4 questions I asked (please answer so I tune the build).
2. **Which stocks/universe?** Nifty 50 only, Nifty 500, or a custom watchlist? (Smaller = faster, cleaner signals to start.)
3. **Your capital & risk appetite?** (Only needed for the position-size calculator — you can keep it private and enter it locally.)
4. **Do you want alerts** (Telegram/email) or just the dashboard?
5. **Intraday or only end-of-day swing?** (Affects data refresh frequency.)

---

## 10. Proposed next step
Once you confirm the 4 setup questions, I'll:
1. Scaffold the full project folder (code structure, `requirements.txt`, README).
2. Build **Phase 1 + Phase 2** so you *see* a working Fear/Greed meter and news feed running locally within the first session.
3. Set up the GitHub repo.

Then we iterate tab by tab.

> **Tell me your answers to the questions and I'll start building.** 🚀
