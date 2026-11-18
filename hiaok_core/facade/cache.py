from __future__ import annotations

from typing import Protocol, runtime_checkable

from expression import Option

from .lifecycle import Lifecycle


@runtime_checkable
class Cache(Lifecycle, Protocol):
    async def get(self, key: str) -> Option[str]: ...

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None: ...

    async def delete(self, *keys: str) -> None: ...
