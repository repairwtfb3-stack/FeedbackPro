from __future__ import annotations

from datetime import datetime
import sqlite3

MIGRATION_V1 = """
CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reviews(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 source TEXT NOT NULL, channel TEXT NOT NULL, review_date TEXT NULL, author TEXT NULL,
 rating REAL NULL, text TEXT NOT NULL, normalized_text TEXT NOT NULL,
 fingerprint TEXT NOT NULL UNIQUE, external_id TEXT NULL, source_file TEXT NULL,
 imported_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""

MIGRATION_V2 = """
CREATE TABLE IF NOT EXISTS analysis_results(
 review_id INTEGER PRIMARY KEY, sentiment TEXT NOT NULL, sentiment_score REAL NOT NULL,
 confidence REAL NOT NULL, aspects_json TEXT NOT NULL, criticality TEXT NOT NULL,
 explanation TEXT NOT NULL, analysis_version TEXT NOT NULL, analyzed_at TEXT NOT NULL,
 FOREIGN KEY(review_id) REFERENCES reviews(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS topics(code TEXT PRIMARY KEY, title TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS decisions(
 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT NOT NULL,
 priority TEXT NOT NULL, status TEXT NOT NULL, due_date TEXT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decision_reviews(
 decision_id INTEGER NOT NULL, review_id INTEGER NOT NULL,
 PRIMARY KEY(decision_id,review_id),
 FOREIGN KEY(decision_id) REFERENCES decisions(id) ON DELETE CASCADE,
 FOREIGN KEY(review_id) REFERENCES reviews(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS control_items(
 id INTEGER PRIMARY KEY AUTOINCREMENT, decision_id INTEGER NOT NULL UNIQUE,
 status TEXT NOT NULL, due_date TEXT NULL, outcome TEXT NULL, verified_at TEXT NULL,
 FOREIGN KEY(decision_id) REFERENCES decisions(id) ON DELETE CASCADE
);
"""

MIGRATION_V3 = """
CREATE TABLE IF NOT EXISTS expert_labels(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 review_id INTEGER NOT NULL,
 sentiment TEXT NOT NULL,
 aspects_json TEXT NOT NULL,
 criticality TEXT NOT NULL,
 comment TEXT NULL,
 reviewer TEXT NULL,
 revision INTEGER NOT NULL,
 is_current INTEGER NOT NULL DEFAULT 1,
 created_at TEXT NOT NULL,
 FOREIGN KEY(review_id) REFERENCES reviews(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_expert_labels_current
ON expert_labels(review_id) WHERE is_current=1;
CREATE INDEX IF NOT EXISTS ix_expert_labels_review_revision
ON expert_labels(review_id, revision DESC);

CREATE TABLE IF NOT EXISTS analysis_overrides(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 review_id INTEGER NOT NULL,
 expert_label_id INTEGER NOT NULL,
 field_name TEXT NOT NULL,
 auto_value TEXT NULL,
 verified_value TEXT NOT NULL,
 created_at TEXT NOT NULL,
 FOREIGN KEY(review_id) REFERENCES reviews(id) ON DELETE CASCADE,
 FOREIGN KEY(expert_label_id) REFERENCES expert_labels(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_analysis_overrides_review ON analysis_overrides(review_id);

CREATE TABLE IF NOT EXISTS audit_events(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 event_type TEXT NOT NULL,
 entity_type TEXT NOT NULL,
 entity_id TEXT NULL,
 actor TEXT NULL,
 payload_json TEXT NOT NULL,
 created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_audit_events_entity ON audit_events(entity_type, entity_id, id DESC);

CREATE TABLE IF NOT EXISTS import_batches(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 source_file TEXT NOT NULL,
 file_sha256 TEXT NULL,
 total_rows INTEGER NOT NULL DEFAULT 0,
 accepted_rows INTEGER NOT NULL DEFAULT 0,
 duplicate_rows INTEGER NOT NULL DEFAULT 0,
 rejected_rows INTEGER NOT NULL DEFAULT 0,
 started_at TEXT NOT NULL,
 completed_at TEXT NULL
);

CREATE TABLE IF NOT EXISTS quality_runs(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 analysis_version TEXT NOT NULL,
 sample_manifest_json TEXT NOT NULL,
 sample_size INTEGER NOT NULL,
 labeled_count INTEGER NOT NULL,
 created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quality_run_metrics(
 quality_run_id INTEGER NOT NULL,
 metric_group TEXT NOT NULL,
 metric_name TEXT NOT NULL,
 metric_value REAL NOT NULL,
 PRIMARY KEY(quality_run_id, metric_group, metric_name),
 FOREIGN KEY(quality_run_id) REFERENCES quality_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_reviews_review_date ON reviews(review_date);
CREATE INDEX IF NOT EXISTS ix_reviews_source_channel ON reviews(source, channel);
CREATE INDEX IF NOT EXISTS ix_analysis_sentiment ON analysis_results(sentiment);
CREATE INDEX IF NOT EXISTS ix_analysis_criticality ON analysis_results(criticality);
CREATE INDEX IF NOT EXISTS ix_controls_status_due ON control_items(status, due_date);
"""

DEFAULT_TOPICS = {
    "quality": "Качество товара",
    "price": "Цена",
    "delivery": "Доставка",
    "service": "Сервис",
    "staff": "Персонал",
    "support": "Поддержка",
    "return": "Возврат и обмен",
    "digital": "Сайт/приложение",
    "availability": "Наличие",
    "other": "Прочее",
}

SUPPORTED_SCHEMA_VERSIONS = (1, 2, 3)


def current_version(conn: sqlite3.Connection) -> int:
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_migrations'").fetchone() is None:
        return 0
    row = conn.execute("SELECT MAX(version) AS v FROM schema_migrations").fetchone()
    return int(row["v"] or 0)


def migrate(conn: sqlite3.Connection, target: int = 2) -> int:
    if target not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError("supported schema targets are 1, 2 and 3")
    current = current_version(conn)
    if current < 1 and target >= 1:
        conn.executescript(MIGRATION_V1)
        conn.execute("INSERT OR IGNORE INTO schema_migrations VALUES(1,?)", (datetime.utcnow().isoformat(),))
        conn.commit()
        current = 1
    if current < 2 and target >= 2:
        conn.executescript(MIGRATION_V2)
        conn.execute("INSERT OR IGNORE INTO schema_migrations VALUES(2,?)", (datetime.utcnow().isoformat(),))
        conn.executemany("INSERT OR IGNORE INTO topics(code,title,active) VALUES(?,?,1)", DEFAULT_TOPICS.items())
        conn.commit()
        current = 2
    if current < 3 and target >= 3:
        conn.executescript(MIGRATION_V3)
        conn.execute("INSERT OR IGNORE INTO schema_migrations VALUES(3,?)", (datetime.utcnow().isoformat(),))
        conn.commit()
        current = 3
    return current
