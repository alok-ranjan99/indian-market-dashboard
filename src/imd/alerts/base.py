"""Notifier interface + AlertDispatcher.

Adding a channel (Slack, WhatsApp, push) = implement Notifier and register it.
The dispatcher owns the single threshold/routing decision so scorers never talk to
channels directly.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from imd.domain import Signal

logger = logging.getLogger(__name__)


class Notifier(ABC):
    """A single alert channel (Telegram, Email, ...)."""

    name: str = "notifier"

    @abstractmethod
    def send(self, signal: Signal) -> None:
        """Deliver the signal. Should not raise on transient failure — log and move on."""
        raise NotImplementedError

    @property
    def enabled(self) -> bool:
        """Channels self-report readiness (e.g. creds present)."""
        return True


class AlertDispatcher:
    """Fans a signal out to all enabled notifiers above a strength threshold."""

    def __init__(self, notifiers: list[Notifier] | None = None, threshold: float = 70.0) -> None:
        self._notifiers = notifiers or []
        self.threshold = threshold

    def register(self, notifier: Notifier) -> None:
        self._notifiers.append(notifier)

    @property
    def active_channels(self) -> list[str]:
        return [n.name for n in self._notifiers if n.enabled]

    def dispatch(self, signal: Signal) -> int:
        """Send to all enabled channels if the signal clears the threshold.

        Returns the number of channels the signal was delivered to.
        """
        if signal.strength < self.threshold:
            logger.debug("signal %r below threshold (%.1f < %.1f)", signal.title,
                         signal.strength, self.threshold)
            return 0
        delivered = 0
        for n in self._notifiers:
            if not n.enabled:
                continue
            try:
                n.send(signal)
                delivered += 1
            except Exception:  # noqa: BLE001 — a bad channel must not block others
                logger.exception("notifier %s failed to send", n.name)
        return delivered
