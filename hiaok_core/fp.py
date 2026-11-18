"""Functional toolbox: typed ``curry`` and the chainable ``AsyncResult`` railway."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Generator, Iterable
from typing import Any

from expression import Error, Ok, Option, Result
from toolz import curry as _curry


def curry(fn: Callable[..., Any]) -> Any:
    """``toolz.curry`` with a signature pyright accepts.

    ``f(a)(b)(c)`` / ``f(a, b)(c)`` cannot be expressed in the type system, so a curried function is
    typed as ``Any``; the *uncurried* body stays fully typed.
    """
    return _curry(fn)


def _is_async(value: Any) -> bool:
    # Expression's Result/Option define __await__ (for effect builders) - they are plain values here.
    return inspect.isawaitable(value) and not hasattr(value, "tag")


async def _resolve(value: Any) -> Any:
    return await value if _is_async(value) else value


class AsyncResult[T, E]:
    """Fluent, awaitable railway: ``AsyncResult.of(x).bind(f).tap(g).map(h)``.

    Each step accepts a sync *or* async callable; the first ``Error`` short-circuits the rest.
    """

    __slots__ = ("_aw",)

    def __init__(self, aw: Awaitable[Result[T, E]]) -> None:
        self._aw = aw

    # ---- constructors ----
    @classmethod
    def of(cls, result: Result[T, E] | Awaitable[Result[T, E]]) -> AsyncResult[T, E]:
        return cls(_resolve(result))

    @classmethod
    def ok(cls, value: T) -> AsyncResult[T, E]:
        return cls.of(Ok(value))

    @classmethod
    def from_option(cls, option: Option[T] | Awaitable[Option[T]], error: E) -> AsyncResult[T, E]:
        async def run() -> Result[T, E]:
            return (await _resolve(option)).to_result(error)

        return cls(run())

    # ---- chain ----
    def map[U](self, f: Callable[[T], U | Awaitable[U]]) -> AsyncResult[U, E]:
        async def run() -> Result[U, E]:
            r = await self._aw
            if isinstance(r, Error):
                return Error(r.error)
            return Ok(await _resolve(f(r.ok)))

        return AsyncResult(run())

    def bind[U](self, f: Callable[[T], Result[U, E] | Awaitable[Result[U, E]]]) -> AsyncResult[U, E]:
        async def run() -> Result[U, E]:
            r = await self._aw
            if isinstance(r, Error):
                return Error(r.error)
            return await _resolve(f(r.ok))

        return AsyncResult(run())

    def ensure(self, check: Callable[[T], Result[Any, E] | Awaitable[Result[Any, E]]]) -> AsyncResult[T, E]:
        """Run a validation step; keep the current value when it succeeds."""

        async def run() -> Result[T, E]:
            r = await self._aw
            if isinstance(r, Error):
                return r
            checked = await _resolve(check(r.ok))
            return Error(checked.error) if isinstance(checked, Error) else r

        return AsyncResult(run())

    def tap(self, f: Callable[[T], Any]) -> AsyncResult[T, E]:
        """Run a side effect on Ok and keep the value (save, publish, log ...)."""

        async def run() -> Result[T, E]:
            r = await self._aw
            if isinstance(r, Ok):
                await _resolve(f(r.ok))
            return r

        return AsyncResult(run())

    def map_error[F](self, f: Callable[[E], F]) -> AsyncResult[T, F]:
        async def run() -> Result[T, F]:
            r = await self._aw
            if isinstance(r, Error):
                return Error(f(r.error))
            return Ok(r.ok)

        return AsyncResult(run())

    def __await__(self) -> Generator[Any, None, Result[T, E]]:
        return self._aw.__await__()


def sequence[T, E](results: Iterable[Result[T, E]]) -> Result[list[T], E]:
    """[Result] -> Result[list] (first Error wins)."""
    values: list[T] = []
    for r in results:
        if isinstance(r, Error):
            return Error(r.error)
        values.append(r.ok)
    return Ok(values)
