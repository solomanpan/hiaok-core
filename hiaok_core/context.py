"""Per-request / per-message context (who is acting, correlation id).

Set by the presentation middleware or the event consumer; read by repositories to fill ``opr``.
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RequestContext:
    """Who is acting, for which organization / tenant, and the correlation id.

    ``org_uuid`` / ``tenant_uuid`` / ``user_uuid`` stay ``None`` until authentication fills them in.
    """

    operator: str = "system"
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    org_uuid: str | None = None
    tenant_uuid: str | None = None
    user_uuid: str | None = None


_context: ContextVar[RequestContext | None] = ContextVar("hiaok_request_context", default=None)
_ANONYMOUS = RequestContext(operator="system", trace_id="-")


def current_context() -> RequestContext:
    return _context.get() or _ANONYMOUS


@contextmanager
def request_context(
    operator: str = "system",
    trace_id: str | None = None,
    *,
    org_uuid: str | None = None,
    tenant_uuid: str | None = None,
    user_uuid: str | None = None,
) -> Generator[RequestContext, None, None]:
    ctx = RequestContext(
        operator=operator,
        trace_id=trace_id or uuid.uuid4().hex,
        org_uuid=org_uuid,
        tenant_uuid=tenant_uuid,
        user_uuid=user_uuid,
    )
    token = _context.set(ctx)
    try:
        yield ctx
    finally:
        _context.reset(token)
