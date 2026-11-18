from typing import Protocol, runtime_checkable


@runtime_checkable
class Lifecycle(Protocol):
    """Opened at startup, closed at shutdown."""

    async def start(self) -> None: ...

    async def stop(self) -> None: ...
