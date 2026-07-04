"""Alerts layer — Notifier interface + AlertDispatcher fan-out."""

from imd.alerts.base import AlertDispatcher, Notifier

__all__ = ["AlertDispatcher", "Notifier"]
