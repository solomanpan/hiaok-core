import uuid
from collections.abc import Callable

type IdGenerator = Callable[[], str]


def uuid_hex() -> str:
    return uuid.uuid4().hex
