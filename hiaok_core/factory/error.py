"""Error catalog: define every business error once (kind + code + message template), produce it anywhere.

    class RoleErrors(ErrorCatalog):
        system_role = ErrorSpec.conflict("system_role", "system role '{code}' cannot be deleted")

    RoleErrors.system_role(code="ADMIN")        # -> DomainError (a value)
    RoleErrors.system_role.err(code="ADMIN")    # -> Error(DomainError) as a Result, for `return` in Result code
    RoleErrors.system_role.raise_(code="ADMIN") # -> raises DomainException

Codes and messages may both contain ``{placeholders}``; codes are stable identifiers clients can rely on,
messages are for humans (and the place to plug in i18n later).
"""

from __future__ import annotations

import string
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, ClassVar, NoReturn

from expression import Error, Result

from hiaok_core.exception import DomainError, DomainException, ErrorKind


@dataclass(frozen=True)
class ErrorSpec:
    kind: ErrorKind
    code: str
    template: str

    # ---- constructors, one per kind ----
    @classmethod
    def validation(cls, code: str, template: str) -> ErrorSpec:
        return cls("validation", code, template)

    @classmethod
    def not_found(cls, code: str, template: str) -> ErrorSpec:
        return cls("not_found", code, template)

    @classmethod
    def conflict(cls, code: str, template: str) -> ErrorSpec:
        return cls("conflict", code, template)

    @classmethod
    def forbidden(cls, code: str, template: str) -> ErrorSpec:
        return cls("forbidden", code, template)

    # ---- produce ----
    @property
    def placeholders(self) -> frozenset[str]:
        found = string.Formatter().parse(self.code + self.template)
        return frozenset(name for _, name, _, _ in found if name)

    def __call__(self, **params: Any) -> DomainError:
        missing = self.placeholders - params.keys()
        if missing:
            raise TypeError(f"error '{self.code}' needs {sorted(missing)}")
        return DomainError(self.kind, self.code.format(**params), self.template.format(**params))

    def err(self, **params: Any) -> Result[Any, DomainError]:
        return Error(self(**params))

    def raise_(self, **params: Any) -> NoReturn:
        raise DomainException(self(**params))


class ErrorCatalog:
    """Group of ``ErrorSpec`` class attributes. Codes must be unique inside a catalog (checked at import)."""

    _specs: ClassVar[dict[str, ErrorSpec]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        specs = {name: value for name, value in vars(cls).items() if isinstance(value, ErrorSpec)}
        codes = [s.code for s in specs.values()]
        duplicates = sorted({c for c in codes if codes.count(c) > 1})
        if duplicates:
            raise TypeError(f"{cls.__name__}: duplicate error codes {duplicates}")
        cls._specs = specs

    @classmethod
    def specs(cls) -> Iterator[tuple[str, ErrorSpec]]:
        yield from cls._specs.items()
