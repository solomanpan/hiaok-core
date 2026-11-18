import pytest
from expression import Error

from hiaok_core.exception import DomainError, DomainException
from hiaok_core.factory import ErrorCatalog, ErrorSpec


class RoleErrors(ErrorCatalog):
    system_role = ErrorSpec.conflict("system_role", "system role '{code}' cannot be deleted")
    required = ErrorSpec.validation("{field}_required", "{field} is required")


def test_spec_produces_a_domain_error():
    assert RoleErrors.system_role(code="ADMIN") == DomainError(
        "conflict", "system_role", "system role 'ADMIN' cannot be deleted"
    )


def test_placeholders_in_code_and_message():
    err = RoleErrors.required(field="role_name")
    assert (err.kind, err.code, err.message) == ("validation", "role_name_required", "role_name is required")
    assert RoleErrors.required.placeholders == {"field"}


def test_err_and_raise():
    result = RoleErrors.system_role.err(code="X")
    assert isinstance(result, Error) and result.error.code == "system_role"
    with pytest.raises(DomainException) as exc:
        RoleErrors.system_role.raise_(code="X")
    assert exc.value.error.kind == "conflict"


def test_missing_parameter_is_a_programming_error():
    with pytest.raises(TypeError, match="code"):
        RoleErrors.system_role()


def test_catalog_lists_specs_and_rejects_duplicate_codes():
    assert dict(RoleErrors.specs()).keys() == {"system_role", "required"}
    with pytest.raises(TypeError, match="duplicate"):

        class Broken(ErrorCatalog):  # pyright: ignore[reportUnusedClass]
            a = ErrorSpec.conflict("same", "a")
            b = ErrorSpec.validation("same", "b")
