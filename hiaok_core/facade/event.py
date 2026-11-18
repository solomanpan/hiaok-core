"""Event bus facade. Any class with ``event_type()`` + ``event_id`` is an event (domain events qualify)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol, runtime_checkable

from .lifecycle import Lifecycle


class Event(Protocol):
    @property
    def event_id(self) -> str: ...

    @classmethod
    def event_type(cls) -> str: ...


type EventHandler[E: Event] = Callable[[E], Awaitable[None]]


@runtime_checkable
class EventPublisher(Protocol):
    async def publish(self, event: Event) -> None: ...


@runtime_checkable
class EventSubscriber(Protocol):
    def subscribe[E: Event](self, event_type: type[E], handler: EventHandler[E]) -> None: ...


@runtime_checkable
class EventBus(EventPublisher, EventSubscriber, Lifecycle, Protocol): ...
