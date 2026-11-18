from typing import Protocol, runtime_checkable


@runtime_checkable
class PasswordHasher(Protocol):
    def hash(self, raw: str) -> str: ...

    def verify(self, raw: str, hashed: str) -> bool: ...
