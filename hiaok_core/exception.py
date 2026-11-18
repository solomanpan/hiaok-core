"""Errors.

* ``DomainError`` is a *value*: business rules return it inside ``Result.Error`` (no exceptions).
* ``HiaokError`` and its subclasses are *raised*: unexpected / technical failures, or a ``DomainError``
  that must cross a boundary that cannot carry a ``Result`` (``DomainException``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ErrorKind = Literal["validation", "not_found", "conflict", "forbidden"]


@dataclass(frozen=True)
class DomainError:
    kind: ErrorKind
    code: str
    message: str


def validation(code: str, message: str) -> DomainError:
    return DomainError("validation", code, message)


def not_found(entity: str, entity_id: str) -> DomainError:
    return DomainError("not_found", f"{entity.lower()}_not_found", f"{entity} '{entity_id}' not found")


def conflict(code: str, message: str) -> DomainError:
    return DomainError("conflict", code, message)


def forbidden(code: str, message: str) -> DomainError:
    return DomainError("forbidden", code, message)


class HiaokError(Exception):
    """Root of every exception raised by hiaok code."""

    code: str = "internal_error"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code

    @property
    def message(self) -> str:
        return str(self)


class DomainException(HiaokError):
    """A ``DomainError`` raised as an exception (prefer returning ``Result.Error``)."""

    def __init__(self, error: DomainError) -> None:
        super().__init__(error.message, code=error.code)
        self.error = error


class InfrastructureError(HiaokError):
    """Failure of an external system (database, broker, cache, HTTP)."""

    code = "infrastructure_error"


class HttpClientError(InfrastructureError):
    code = "http_client_error"

    def __init__(self, message: str, *, status: int | None = None, url: str | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.url = url
