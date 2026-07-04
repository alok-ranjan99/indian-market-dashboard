# MCPs, Tools & Data Sources — Quick Reference

## MCPs (help Claude Code build & you manage the project)
| MCP | Purpose | Cost | Need it? |
|---|---|---|---|
| GitHub MCP | Code hosting, version control, deploy | Free | ⭐ Yes |
| Filesystem MCP | Read/write project files | Free | ⭐ Yes (built-in) |
| Fetch/Web MCP | Pull live news & NSE data during dev | Free | ⭐ Yes |
| Figma MCP | Design UI mockups | Free tier | 🔸 Optional |
| Puppeteer/Playwright MCP | Scrape sites without APIs | Free | 🔸 Optional |
| Sequential-Thinking MCP | Reason through scoring logic | Free | 🔹 Low |

> **Reality:** the app talks to data APIs directly in Python. MCPs mostly speed up the
> *build* and help *manage* the project. We can start with just **GitHub**.

## Free data sources (the actual data engine)
| Source | Gives us | Key needed? |
|---|---|---|
| yfinance | Stock/index prices, India VIX | No |
| NSE India public endpoints | Sectoral indices, FII/DII, option chain, PCR | No |
| RSS (Moneycontrol/ET/Livemint/BS) | News headlines | No |
| NewsAPI.org | Aggregated news | Free key (100/day) |
| Hugging Face FinBERT | Financial sentiment scoring | No (local) |

## Hosting (free)
| Service | Role |
|---|---|
| Streamlit Community Cloud | Host the dashboard (phone/anywhere) |
| Render / Railway | Scheduled daily data pulls |
| GitHub Actions | Free cron for data refresh |

## Optional paid upgrades (later, if you want pro-grade)
| Upgrade | Benefit | Cost |
|---|---|---|
| Zerodha Kite Connect | Real-time Indian data | ~₹2000/mo |
| Upstox/Dhan API | Cheaper real-time data | Free–low |
| OpenAI/Anthropic API | LLM news summaries & smarter sentiment | Pay-as-go |
