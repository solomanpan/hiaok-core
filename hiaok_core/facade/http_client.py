"""Outbound HTTP facade. Implementations raise ``hiaok_core.exception.HttpClientError`` on transport errors."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from hiaok_core import json

from .lifecycle import Lifecycle


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: bytes = b""
    headers: Mapping[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    @property
    def text(self) -> str:
        return self.body.decode()

    def json(self) -> Any:
        return json.loads(self.body)


@runtime_checkable
class HttpClient(Lifecycle, Protocol):
    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any = None,
        headers: Mapping[str, str] | None = None,
        request_timeout: float | None = None,
    ) -> HttpResponse: ...

    async def get(self, url: str, **kwargs: Any) -> HttpResponse: ...

    async def post(self, url: str, **kwargs: Any) -> HttpResponse: ...
