from __future__ import annotations

import sqlite3
from typing import Any


def table_names(conn: sqlite3.Connection) -> set[str]:
    return {str(row[0]) for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}


def schema_snapshot(conn: sqlite3.Connection) -> dict[str, Any]:
    tables = sorted(table_names(conn))
    migrations = []
    if "schema_migrations" in tables:
        migrations = [dict(row) for row in conn.execute("SELECT * FROM schema_migrations ORDER BY version").fetchall()]
    return {"tables": tables, "migrations": migrations}


def review_count(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()
    return int(row[0])
