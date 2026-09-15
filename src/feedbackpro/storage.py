from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Iterator

from .domain import AnalysisResult, ControlStatus, Criticality, DecisionStatus, Review, Sentiment
from .migrations import current_version as migration_current_version, migrate as run_migrations


class Database:
    def __init__(self, path: str | Path = "feedbackpro.db") -> None:
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            self.conn.execute("BEGIN")
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def current_version(self) -> int:
        return migration_current_version(self.conn)

    def migrate(self, target: int = 2) -> int:
        return run_migrations(self.conn, target)

    def add_review(self, review: Review) -> tuple[Review, bool]:
        try:
            cur = self.conn.execute(
                """INSERT INTO reviews(source,channel,review_date,author,rating,text,normalized_text,fingerprint,external_id,source_file,imported_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    review.source,
                    review.channel,
                    review.review_date.isoformat() if review.review_date else None,
                    review.author,
                    review.rating,
                    review.text,
                    review.normalized_text,
                    review.fingerprint,
                    review.external_id,
                    review.source_file,
                    review.imported_at.isoformat(),
                ),
            )
            self.conn.commit()
            return replace(review, id=int(cur.lastrowid)), True
        except sqlite3.IntegrityError:
            self.conn.rollback()
            row = self.conn.execute("SELECT * FROM reviews WHERE fingerprint=?", (review.fingerprint,)).fetchone()
            return self._review(row), False

    def _review(self, row: sqlite3.Row) -> Review:
        return Review(
            id=row["id"],
            source=row["source"],
            channel=row["channel"],
            review_date=date.fromisoformat(row["review_date"]) if row["review_date"] else None,
            author=row["author"],
            rating=row["rating"],
            text=row["text"],
            normalized_text=row["normalized_text"],
            fingerprint=row["fingerprint"],
            external_id=row["external_id"],
            source_file=row["source_file"],
            imported_at=datetime.fromisoformat(row["imported_at"]),
        )

    def list_reviews(self) -> list[Review]:
        return [self._review(r) for r in self.conn.execute("SELECT * FROM reviews ORDER BY id").fetchall()]

    def get_review(self, review_id: int) -> Review:
        row = self.conn.execute("SELECT * FROM reviews WHERE id=?", (review_id,)).fetchone()
        if row is None:
            raise KeyError(review_id)
        return self._review(row)

    def save_analysis(self, result: AnalysisResult) -> None:
        if result.review_id is None:
            raise ValueError("persist review before analysis")
        self.conn.execute(
            """INSERT INTO analysis_results VALUES(?,?,?,?,?,?,?,?,?)
            ON CONFLICT(review_id) DO UPDATE SET
              sentiment=excluded.sentiment,
              sentiment_score=excluded.sentiment_score,
              confidence=excluded.confidence,
              aspects_json=excluded.aspects_json,
              criticality=excluded.criticality,
              explanation=excluded.explanation,
              analysis_version=excluded.analysis_version,
              analyzed_at=excluded.analyzed_at""",
            (
                result.review_id,
                result.sentiment.value,
                result.sentiment_score,
                result.confidence,
                json.dumps(result.aspects, ensure_ascii=False),
                result.criticality.value,
                result.explanation,
                result.analysis_version,
                result.analyzed_at.isoformat(),
            ),
        )
        self.conn.commit()

    def get_analysis(self, review_id: int) -> AnalysisResult | None:
        r = self.conn.execute("SELECT * FROM analysis_results WHERE review_id=?", (review_id,)).fetchone()
        if r is None:
            return None
        return AnalysisResult(
            review_id=r["review_id"],
            sentiment=Sentiment(r["sentiment"]),
            sentiment_score=r["sentiment_score"],
            confidence=r["confidence"],
            aspects=tuple(json.loads(r["aspects_json"])),
            criticality=Criticality(r["criticality"]),
            explanation=r["explanation"],
            analysis_version=r["analysis_version"],
            analyzed_at=datetime.fromisoformat(r["analyzed_at"]),
        )

    def review_records(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT r.*,a.sentiment,a.sentiment_score,a.confidence,a.aspects_json,a.criticality,a.analysis_version
            FROM reviews r LEFT JOIN analysis_results a ON a.review_id=r.id ORDER BY r.id DESC"""
        ).fetchall()
        return [
            {
                "id": r["id"], "source": r["source"], "channel": r["channel"],
                "review_date": r["review_date"], "author": r["author"], "rating": r["rating"],
                "text": r["text"], "sentiment": r["sentiment"], "sentiment_score": r["sentiment_score"],
                "confidence": r["confidence"], "aspects": json.loads(r["aspects_json"]) if r["aspects_json"] else [],
                "criticality": r["criticality"], "analysis_version": r["analysis_version"],
            }
            for r in rows
        ]

    def create_decision(self, title: str, description: str, priority: str, review_ids: Iterable[int], due_date: date | None = None) -> int:
        ids = tuple(dict.fromkeys(int(x) for x in review_ids))
        if not ids:
            raise ValueError("decision must reference review")
        with self.transaction() as cx:
            for rid in ids:
                if cx.execute("SELECT 1 FROM reviews WHERE id=?", (rid,)).fetchone() is None:
                    raise KeyError(rid)
            cur = cx.execute(
                "INSERT INTO decisions(title,description,priority,status,due_date,created_at) VALUES(?,?,?,?,?,?)",
                (title.strip(), description.strip(), priority.strip() or "medium", DecisionStatus.CREATED.value, due_date.isoformat() if due_date else None, datetime.utcnow().isoformat()),
            )
            did = int(cur.lastrowid)
            cx.executemany("INSERT INTO decision_reviews VALUES(?,?)", [(did, rid) for rid in ids])
        return did

    def decision_records(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT d.*,GROUP_CONCAT(dr.review_id) review_ids,c.status control_status,c.outcome control_outcome
            FROM decisions d LEFT JOIN decision_reviews dr ON dr.decision_id=d.id
            LEFT JOIN control_items c ON c.decision_id=d.id GROUP BY d.id ORDER BY d.id DESC"""
        ).fetchall()
        return [
            {
                "id": r["id"], "title": r["title"], "description": r["description"], "priority": r["priority"],
                "status": r["status"], "due_date": r["due_date"],
                "review_ids": [int(x) for x in (r["review_ids"] or "").split(",") if x],
                "control_status": r["control_status"], "control_outcome": r["control_outcome"],
            }
            for r in rows
        ]

    def set_control(self, decision_id: int, status: ControlStatus, due_date: date | None = None, outcome: str | None = None) -> int:
        if self.conn.execute("SELECT 1 FROM decisions WHERE id=?", (decision_id,)).fetchone() is None:
            raise KeyError(decision_id)
        verified = datetime.utcnow().isoformat() if status is ControlStatus.VERIFIED else None
        self.conn.execute(
            """INSERT INTO control_items(decision_id,status,due_date,outcome,verified_at) VALUES(?,?,?,?,?)
            ON CONFLICT(decision_id) DO UPDATE SET status=excluded.status,due_date=excluded.due_date,outcome=excluded.outcome,verified_at=excluded.verified_at""",
            (decision_id, status.value, due_date.isoformat() if due_date else None, outcome, verified),
        )
        self.conn.commit()
        return int(self.conn.execute("SELECT id FROM control_items WHERE decision_id=?", (decision_id,)).fetchone()["id"])

    def control_records(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute("SELECT c.*,d.title decision_title FROM control_items c JOIN decisions d ON d.id=c.decision_id ORDER BY c.id DESC").fetchall()]

    def topics(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM topics ORDER BY title").fetchall()]

    def set_topic(self, code: str, title: str, active: bool) -> None:
        self.conn.execute(
            """INSERT INTO topics(code,title,active) VALUES(?,?,?) ON CONFLICT(code) DO UPDATE SET title=excluded.title,active=excluded.active""",
            (code.strip(), title.strip(), int(active)),
        )
        self.conn.commit()

    def set_setting(self, key: str, value: str) -> None:
        self.conn.execute(
            """INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
            (key.strip(), value),
        )
        self.conn.commit()

    def dashboard(self) -> dict[str, Any]:
        q = self.conn.execute
        sentiments = {r["sentiment"]: r["c"] for r in q("SELECT sentiment,COUNT(*) c FROM analysis_results GROUP BY sentiment").fetchall()}
        aspects: dict[str, int] = {}
        for r in q("SELECT aspects_json FROM analysis_results").fetchall():
            for a in json.loads(r["aspects_json"]):
                aspects[a] = aspects.get(a, 0) + 1
        return {
            "total_reviews": q("SELECT COUNT(*) c FROM reviews").fetchone()["c"],
            "analyzed_reviews": q("SELECT COUNT(*) c FROM analysis_results").fetchone()["c"],
            "negative_reviews": q("SELECT COUNT(*) c FROM analysis_results WHERE sentiment='negative'").fetchone()["c"],
            "critical_reviews": q("SELECT COUNT(*) c FROM analysis_results WHERE criticality='critical'").fetchone()["c"],
            "decision_count": q("SELECT COUNT(*) c FROM decisions").fetchone()["c"],
            "open_controls": q("SELECT COUNT(*) c FROM control_items WHERE status!='verified'").fetchone()["c"],
            "sentiments": sentiments,
            "aspects": dict(sorted(aspects.items(), key=lambda x: (-x[1], x[0]))),
        }
