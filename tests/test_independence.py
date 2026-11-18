"""hiaok-core must stay reusable: it never imports a service package or a web/ORM framework."""

import ast
from pathlib import Path

PKG = Path(__file__).resolve().parents[1] / "hiaok_core"
FORBIDDEN = ("hiaok.", "src.", "fastapi", "sqlalchemy", "starlette")


def test_no_service_or_framework_imports():
    bad = []
    for path in PKG.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            names = (
                [a.name for a in node.names]
                if isinstance(node, ast.Import)
                else [node.module]
                if isinstance(node, ast.ImportFrom) and node.module and node.level == 0
                else []
            )
            bad += [f"{path.name}: {n}" for n in names if n.startswith(FORBIDDEN) or n in ("hiaok", "src")]
    assert bad == []
