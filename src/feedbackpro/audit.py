from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Mapping


def append_audit_event(
    conn: sqlite3.Connection,
    *,
    event_type: str,
    entity_type: str,
    entity_id: str | int | None = None,
    actor: str | None = None,
    payload: Mapping[str, Any] | None = None,
) -> int:
    """Persist one immutable audit event. Requires schema v3."""
    cur = conn.execute(
        "INSERT INTO audit_events(event_type,entity_type,entity_id,actor,payload_json,created_at) VALUES(?,?,?,?,?,?)",
        (
            event_type.strip(),
            entity_type.strip(),
            None if entity_id is None else str(entity_id),
            actor,
            json.dumps(dict(payload or {}), ensure_ascii=False, sort_keys=True),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def list_audit_events(conn: sqlite3.Connection, entity_type: str, entity_id: str | int | None = None) -> list[dict[str, Any]]:
    if entity_id is None:
        rows = conn.execute("SELECT * FROM audit_events WHERE entity_type=? ORDER BY id", (entity_type,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM audit_events WHERE entity_type=? AND entity_id=? ORDER BY id",
            (entity_type, str(entity_id)),
        ).fetchall()
    return [dict(row) for row in rows]
