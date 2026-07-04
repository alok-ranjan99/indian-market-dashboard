"""Smoke tests — the package imports and core objects behave."""

from __future__ import annotations

import imd
from imd.alerts import AlertDispatcher, Notifier
from imd.domain import (
    Bias,
    BiasLabel,
    Sentiment,
    Signal,
    SignalKind,
    SwingScore,
)


def test_version() -> None:
    assert isinstance(imd.__version__, str)


def test_sentiment_from_score() -> None:
    assert Sentiment.from_score(0.5) is Sentiment.POSITIVE
    assert Sentiment.from_score(-0.5) is Sentiment.NEGATIVE
    assert Sentiment.from_score(0.0) is Sentiment.NEUTRAL


def test_swing_risk_reward() -> None:
    s = SwingScore(value=80, entry=100, stop=95, target=115)
    assert s.risk_reward == 3.0  # (115-100)/(100-95)


def test_swing_risk_reward_zero_risk() -> None:
    s = SwingScore(value=50, entry=100, stop=100, target=110)
    assert s.risk_reward is None


class _RecordingNotifier(Notifier):
    name = "recording"

    def __init__(self) -> None:
        self.sent: list[Signal] = []

    def send(self, signal: Signal) -> None:
        self.sent.append(signal)


def _signal(strength: float) -> Signal:
    return Signal(kind=SignalKind.SWING, title="test", strength=strength)


def test_dispatcher_respects_threshold() -> None:
    n = _RecordingNotifier()
    d = AlertDispatcher([n], threshold=70)
    assert d.dispatch(_signal(50)) == 0
    assert d.dispatch(_signal(80)) == 1
    assert len(n.sent) == 1


def test_dispatcher_isolates_failing_channel() -> None:
    class _Boom(Notifier):
        name = "boom"

        def send(self, signal: Signal) -> None:
            raise RuntimeError("channel down")

    good = _RecordingNotifier()
    d = AlertDispatcher([_Boom(), good], threshold=10)
    # one channel raises, the other still receives.
    assert d.dispatch(_signal(90)) == 1
    assert len(good.sent) == 1


def test_bias_construction() -> None:
    b = Bias(label=BiasLabel.BULLISH, confidence=0.62, reasons=["trend intact"])
    assert b.label is BiasLabel.BULLISH
    assert b.confidence == 0.62
