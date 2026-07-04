"""Scorer interface + shared scoring context.

Every scorer is a pure function of its context → a result with a breakdown, so it is
trivial to unit-test with golden files and to explain in the UI. New scores (e.g. a
"liquidity" score) are added by implementing Scorer; the engine iterates over them.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from imd.config import Settings


@dataclass
class ScoringContext:
    """Bundle of inputs a scorer may need. Populated by the data layer.

    Kept as a loose bag now; individual scorers pull the keys they care about.
    Concrete typed fields will firm up in Phase 5 as scorers are implemented.
    """

    settings: Settings
    market: dict[str, Any] = field(default_factory=dict)  # prices, indices, VIX, breadth, PCR
    news: list[Any] = field(default_factory=list)         # list[NewsItem]
    sectors: list[Any] = field(default_factory=list)      # list[SectorPerf]
    flows: dict[str, Any] = field(default_factory=dict)   # FII/DII
    global_cues: dict[str, Any] = field(default_factory=dict)


class Scorer(ABC):
    """Produces a ScoreResult (or Bias/SwingScore) from a ScoringContext."""

    name: str = "scorer"

    @abstractmethod
    def compute(self, ctx: ScoringContext) -> Any:
        """Return a domain result object (ScoreResult / Bias / SwingScore)."""
        raise NotImplementedError
