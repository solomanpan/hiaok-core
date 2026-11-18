"""Datasource routing + transaction facade (implementation: hiaok ``infrastructure/database/routing.py``)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from enum import StrEnum
from typing import Protocol

from expression import Option


class DataSource(StrEnum):
    MASTER = "master"  # read-write
    SLAVE = "slave"  # read-only replica


class Transaction(Protocol):
    @property
    def datasource(self) -> DataSource: ...

    @property
    def is_root(self) -> bool:
        """False when this scope joined an outer one (only the root commits / rolls back)."""
        ...

    def set_rollback_only(self) -> None: ...

    def after_commit(self, callback: Callable[[], Awaitable[None]]) -> None:
        """Run after the ROOT transaction commits (never on rollback). Used to publish domain events."""
        ...


class TransactionManager(Protocol):
    def begin(self, datasource: DataSource) -> AbstractAsyncContextManager[Transaction]: ...

    def current(self) -> Option[Transaction]: ...


class HasTransactionManager(Protocol):
    """Anything decorated with ``@master`` / ``@slave`` must expose ``tx``."""

    @property
    def tx(self) -> TransactionManager: ...
