from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any, Mapping

ANALYSIS_VERSION = "a2-rules-1.0"


class Sentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Criticality(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionStatus(StrEnum):
    CREATED = "created"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"


class ControlStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"


@dataclass(frozen=True, slots=True)
class Review:
    id: int | None
    source: str
    channel: str
    review_date: date | None
    author: str | None
    rating: float | None
    text: str
    normalized_text: str
    fingerprint: str
    external_id: str | None = None
    source_file: str | None = None
    imported_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    review_id: int | None
    sentiment: Sentiment
    sentiment_score: float
    confidence: float
    aspects: tuple[str, ...]
    criticality: Criticality
    explanation: str
    analysis_version: str
    analyzed_at: datetime = field(default_factory=datetime.utcnow)


_SPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    return _SPACE_RE.sub(" ", (value or "").strip())


def parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Unsupported review date: {raw}")


def parse_rating(value: Any) -> float | None:
    if value in (None, ""):
        return None
    rating = float(str(value).replace(",", "."))
    if not 0 <= rating <= 5:
        raise ValueError("rating must be between 0 and 5")
    return rating


def make_fingerprint(source: str, external_id: str | None, review_date: date | None, text: str) -> str:
    raw = (
        f"id|{source.casefold()}|{external_id.strip().casefold()}"
        if external_id
        else f"text|{source.casefold()}|{review_date or ''}|{text.casefold()}"
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize_record(record: Mapping[str, Any], *, source_file: str | None = None) -> Review:
    source = normalize_text(str(record.get("source") or "unknown"))
    channel = normalize_text(str(record.get("channel") or source))
    text = normalize_text(str(record.get("text") or ""))
    if not text:
        raise ValueError("review text is required")
    review_date = parse_date(record.get("date") or record.get("review_date"))
    ext = record.get("external_id") or record.get("id")
    external_id = normalize_text(str(ext)) if ext not in (None, "") else None
    author_raw = record.get("author")
    author = normalize_text(str(author_raw)) if author_raw not in (None, "") else None
    rating = parse_rating(record.get("rating"))
    return Review(
        id=None,
        source=source,
        channel=channel,
        review_date=review_date,
        author=author,
        rating=rating,
        text=text,
        normalized_text=text,
        fingerprint=make_fingerprint(source, external_id, review_date, text),
        external_id=external_id,
        source_file=source_file,
    )


_parse_date = parse_date
_parse_rating = parse_rating
