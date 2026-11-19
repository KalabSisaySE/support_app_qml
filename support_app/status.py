"""Strongly typed values for the status strings exposed to QML."""

from enum import StrEnum


class Status(StrEnum):
    """Lifecycle states shown by ``StatusIndicator`` in the QML UI."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    CHECKING = "checking"
