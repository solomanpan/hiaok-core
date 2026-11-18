"""Factories: declarative error catalogs (``ErrorCatalog``).

Test-data factories are not here on purpose: they belong to each service's tests (e.g. with polyfactory).
"""

from .error import ErrorCatalog, ErrorSpec

__all__ = ["ErrorCatalog", "ErrorSpec"]
