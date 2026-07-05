"""Application service — orchestrates data → scoring → view models.

Framework-agnostic (no Streamlit here) and dependency-injected, so every assembler is
unit-testable with fakes. The UI layer adds caching around these functions.
"""

from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass, field

from imd.config import Settings, get_settings
from imd.data.global_cues import GlobalCuesProvider
from imd.data.news import NewsProvider
from imd.data.nse import NSEProvider
from imd.data.prices import PriceProvider
from imd.domain import Bias, Candidate, NewsItem, ScoreResult, SectorPerf
from imd.scoring import build_context, score_market
from imd.scoring import indicators as ind
from imd.screener import screen_candidates, sector_strength_map
from imd.sentiment import SentimentModel, default_model

logger = logging.getLogger(__name__)


# ── view models ───────────────────────────────────────────
@dataclass
class MarketView:
    fear_greed: ScoreResult
    bias: Bias
    indices: dict[str, dict[str, float]] = field(default_factory=dict)
    flows: dict[str, float] = field(default_factory=dict)
    global_cues: dict[str, dict[str, float]] = field(default_factory=dict)
    pcr: float | None = None
    breadth: dict[str, int] = field(default_factory=dict)


@dataclass
class NewsView:
    items: list[NewsItem] = field(default_factory=list)

    @property
    def avg_sentiment(self) -> float:
        if not self.items:
            return 0.0
        return sum(i.sentiment_score for i in self.items) / len(self.items)


@dataclass
class SectorView:
    sectors: list[SectorPerf] = field(default_factory=list)


@dataclass
class SwingView:
    candidates: list[Candidate] = field(default_factory=list)


# ── assemblers ────────────────────────────────────────────
def score_news(items: list[NewsItem], model: SentimentModel) -> list[NewsItem]:
    """Return copies of the items with sentiment_score populated."""
    scored = model.score_batch([i.title for i in items])
    return [dataclasses.replace(it, sentiment_score=s) for it, s in zip(items, scored, strict=True)]


def assemble_news(provider: NewsProvider | None = None,
                  model: SentimentModel | None = None, limit: int = 40) -> NewsView:
    provider = provider or NewsProvider()
    model = model or default_model()
    return NewsView(items=score_news(provider.fetch(limit=limit), model))


def assemble_sectors(nse: NSEProvider | None = None) -> SectorView:
    return SectorView(sectors=(nse or NSEProvider()).fetch_sectors())


def assemble_market(
    *,
    news: NewsView | None = None,
    prices: PriceProvider | None = None,
    nse: NSEProvider | None = None,
    cues: GlobalCuesProvider | None = None,
    settings: Settings | None = None,
) -> MarketView:
    settings = settings or get_settings()
    prices = prices or PriceProvider()
    nse = nse or NSEProvider()
    cues = cues or GlobalCuesProvider()
    news = news if news is not None else NewsView()

    # Nifty trend inputs
    nifty_hist = prices.history("^NSEI", period="4mo")
    close = _last(nifty_hist, "Close")
    sma20 = _last_indicator(nifty_hist, 20)
    sma50 = _last_indicator(nifty_hist, 50)

    # Constituent quotes → breadth proxy
    quotes = prices.fetch()
    advances = sum(1 for q in quotes.values() if (q.change_pct or 0) > 0)
    declines = sum(1 for q in quotes.values() if (q.change_pct or 0) < 0)

    flows = nse.fetch_fii_dii()
    pcr = nse.fetch_pcr()
    cue_data = cues.fetch()
    gap_pct = cue_data.get("Dow Jones", {}).get("change_pct")  # overnight US as gap proxy

    ctx = build_context(
        settings=settings,
        market={
            "vix": _index_close(prices, "INDIA_VIX"),
            "breadth": {"advances": advances, "declines": declines},
            "nifty_close": close, "nifty_sma20": sma20, "nifty_sma50": sma50,
            "pcr": pcr,
        },
        news=news.items,
        flows=flows,
        global_cues={"gap_pct": gap_pct} if gap_pct is not None else {},
    )
    scores = score_market(ctx)

    return MarketView(
        fear_greed=scores.fear_greed,
        bias=scores.bias,
        indices=_index_block(prices, close),
        flows=flows,
        global_cues=cue_data,
        pcr=pcr,
        breadth={"advances": advances, "declines": declines},
    )


def assemble_swing(
    *,
    prices: PriceProvider | None = None,
    sectors: SectorView | None = None,
    universe: list[str] | None = None,
    settings: Settings | None = None,
    limit: int = 25,
) -> SwingView:
    from imd.data.universe import get_universe  # noqa: PLC0415

    prices = prices or PriceProvider()
    symbols = universe or get_universe((settings or get_settings()).universe)
    histories = prices.histories(symbols, period="6mo")

    sec_view = sectors if sectors is not None else assemble_sectors()
    strength = sector_strength_map(sec_view.sectors)

    candidates = screen_candidates(histories, sector_strength=strength, limit=limit)
    return SwingView(candidates=candidates)


# ── helpers ───────────────────────────────────────────────
def _last(df, col: str) -> float | None:
    try:
        return round(float(df[col].dropna().iloc[-1]), 2) if not df.empty else None
    except (KeyError, IndexError):
        return None


def _last_indicator(df, window: int) -> float | None:
    if df.empty or "Close" not in df:
        return None
    s = ind.sma(df["Close"], window).dropna()
    return round(float(s.iloc[-1]), 2) if not s.empty else None


def _index_close(prices: PriceProvider, key: str) -> float | None:
    q = prices.index_quote(key)
    return round(q.close, 2) if q else None


def _index_block(prices: PriceProvider, nifty_close: float | None) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for label, key in (("Nifty 50", "NIFTY50"), ("Bank Nifty", "BANKNIFTY"),
                       ("India VIX", "INDIA_VIX")):
        q = prices.index_quote(key)
        if q:
            out[label] = {"price": round(q.close, 2), "change_pct": q.change_pct or 0.0}
    return out
