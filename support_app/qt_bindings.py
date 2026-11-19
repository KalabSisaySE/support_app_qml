"""Helpers for declaring QML-facing Qt properties with less boilerplate."""

from __future__ import annotations

from typing import Any, Callable

from PySide6.QtCore import Property


def notifying_property(
    qtype: Any,
    attribute: str,
    notify_signal: str,
    transform: Callable[[Any], Any] | None = None,
) -> Property:
    """Build a Qt ``Property`` backed by ``self.<attribute>``.

    The property emits the signal named by ``notify_signal`` only when the
    incoming value differs from the current one, which is exactly the
    behaviour the backend used to implement by hand for every field.
    ``transform`` may normalize the value before it is stored (for example,
    turning an empty username into the localized fallback).
    """

    def getter(self) -> Any:
        return getattr(self, attribute)

    def setter(self, value: Any) -> None:
        current = getattr(self, attribute)
        if current != value:
            new_value = transform(value) if transform is not None else value
            setattr(self, attribute, new_value)
            getattr(self, notify_signal).emit(new_value)

    return Property(qtype, getter, setter, None, notify_signal)
