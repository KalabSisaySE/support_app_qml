"""Aggregate progress values reported by independent worker tasks."""

from __future__ import annotations


class ProgressAggregator:
    """Track one progress value per process and expose their average."""

    def __init__(self) -> None:
        self._values: dict[str, float] = {}

    def update(self, process_name: str, value: float) -> float:
        """Record *value* for *process_name* and return the new average."""
        self._values[process_name] = value
        return self.average

    @property
    def average(self) -> float:
        """Average of all tracked values (0.0 when nothing is tracked)."""
        if not self._values:
            return 0.0
        return sum(self._values.values()) / len(self._values)

    @property
    def is_empty(self) -> bool:
        return not self._values

    @property
    def values(self) -> dict[str, float]:
        """Snapshot of the tracked values (safe to inspect)."""
        return dict(self._values)

    def clear(self) -> None:
        self._values.clear()
