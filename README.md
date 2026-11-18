# hiaok-core

Core library for the [hiaok](https://github.com/solomanpan/hiaok) project: business-agnostic building blocks
that services depend on (never the other way round).

| Module | Contents |
|---|---|
| `hiaok_core.facade` | Interfaces for external capabilities: `Cache`, `EventBus`, `TransactionManager`, `PasswordHasher`, `IdGenerator`, `HttpClient`. Implementations live in each service's infrastructure layer |
| `hiaok_core.exception` | `DomainError` (a value carried by `Result.Error`) and the raisable `HiaokError` hierarchy (`DomainException`, `InfrastructureError`, `HttpClientError`) |
| `hiaok_core.factory` | `ErrorCatalog` / `ErrorSpec`: declare each business error once (kind, code, message template), produce it as a value (`Spec(...)`), a `Result` error (`.err(...)`) or an exception (`.raise_(...)`) |
| `hiaok_core.json` | JSON encode/decode that understands datetime / Enum / set / dataclass |
| `hiaok_core.fp` | `curry`, chainable `AsyncResult`, `sequence` |
| `hiaok_core.context` | Per-request / per-message context: operator, trace id, org / tenant / user (filled once authentication is in place) |

## Layout

Flat layout (no `src/`): the package is `./hiaok_core`, imported as `hiaok_core`.

```
hiaok-core/
├─ hiaok_core/   # facade/, context.py, exception.py, fp.py, json.py
└─ tests/
```

## Install (uv)

```bash
uv add "hiaok-core @ git+https://github.com/solomanpan/hiaok-core" --tag v0.2.0
```

## Error catalog

```python
from hiaok_core.factory import ErrorCatalog, ErrorSpec


class RoleErrors(ErrorCatalog):
    system_role = ErrorSpec.conflict("system_role", "system role '{code}' cannot be deleted")


return RoleErrors.system_role.err(code=role.role_code)  # inside Result-returning code
```

## Develop

```bash
uv sync
uv run ruff check . && uv run pyright && uv run pytest
```

## Release

Versions follow semver and are published as git tags:

1. bump `version` in `pyproject.toml`, commit
2. `git tag vX.Y.Z && git push && git push --tags`
3. in consumers: change the tag in `[tool.uv.sources]`, then `uv lock --upgrade-package hiaok-core`
