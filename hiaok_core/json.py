"""JSON helpers that understand the types used across hiaok (datetime, Enum, set, dataclass)."""

from __future__ import annotations

import json as _json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any


def json_default(value: Any) -> Any:
    """``json.dumps(..., default=json_default)``."""
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, frozenset | set):
        return sorted(value)
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    raise TypeError(f"not JSON serialisable: {type(value)!r}")


def dumps(value: Any, **kwargs: Any) -> str:
    return _json.dumps(value, default=json_default, ensure_ascii=False, **kwargs)


def loads(raw: str | bytes) -> Any:
    return _json.loads(raw)


def to_jsonable(value: Any) -> Any:
    """Plain ``dict`` / ``list`` / scalars only (e.g. for a JSONB column or a log payload)."""
    return _json.loads(dumps(value))
