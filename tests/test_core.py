from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

import pytest

from hiaok_core import json
from hiaok_core.exception import DomainException, HiaokError, HttpClientError, conflict, not_found
from hiaok_core.facade import HttpResponse


class Color(StrEnum):
    RED = "red"


@dataclass(frozen=True)
class Point:
    x: int
    y: int


def test_json_handles_project_types():
    raw = json.dumps({"at": datetime(2026, 1, 1, tzinfo=UTC), "c": Color.RED, "s": {"b", "a"}, "p": Point(1, 2)})
    assert json.loads(raw) == {"at": "2026-01-01T00:00:00+00:00", "c": "red", "s": ["a", "b"], "p": {"x": 1, "y": 2}}
    assert json.dumps({"name": "権限"}) == '{"name": "権限"}'  # no \\u escapes


def test_json_rejects_unknown_types():
    with pytest.raises(TypeError):
        json.dumps({"x": object()})


def test_exception_hierarchy():
    exc = DomainException(conflict("dup", "duplicate"))
    assert isinstance(exc, HiaokError) and exc.code == "dup" and exc.message == "duplicate"
    assert not_found("Role", "r1").code == "role_not_found"
    assert isinstance(HttpClientError("boom", status=503), HiaokError)


def test_http_response_helpers():
    resp = HttpResponse(status=200, body=b'{"a": 1}')
    assert resp.ok and resp.json() == {"a": 1} and resp.text == '{"a": 1}'
    assert not HttpResponse(status=404).ok


def test_request_context_carries_org_tenant_user():
    from hiaok_core.context import current_context, request_context

    assert current_context().org_uuid is None
    with request_context("taro", "t-1", org_uuid="o1", tenant_uuid="t1", user_uuid="u1") as ctx:
        assert current_context() is ctx
        assert (ctx.operator, ctx.org_uuid, ctx.tenant_uuid, ctx.user_uuid) == ("taro", "o1", "t1", "u1")
    assert current_context().operator == "system"
