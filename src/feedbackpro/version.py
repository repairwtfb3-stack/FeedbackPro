from __future__ import annotations

import json
from pathlib import Path
from typing import Any

VERSION = "0.4.0rc1"
CHANNEL = "pilot-rc"


def build_metadata() -> dict[str, Any]:
    path = Path(__file__).with_name("build_meta.json")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {"version": VERSION, "channel": CHANNEL, "commit": "development", "built_at": None}


def version_label() -> str:
    meta = build_metadata()
    commit = str(meta.get("commit") or "development")
    short_commit = commit[:8] if commit != "development" else commit
    return f"FeedbackPro {meta.get('version', VERSION)} · {meta.get('channel', CHANNEL)} · {short_commit}"
