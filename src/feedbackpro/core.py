"""Backward-compatible facade for the A1/A2 public API.

A3.2 splits the former monolithic core into focused modules while keeping this
module import-compatible so A2 regression tests and external callers continue
to work unchanged.
"""
from .analysis import (
    ASPECT_RULES,
    CRITICAL_MARKERS,
    HIGH_MARKERS,
    INTENSIFIERS,
    NEGATIONS,
    NEGATIVE,
    POSITIVE,
    AnalysisPipeline,
)
from .domain import (
    ANALYSIS_VERSION,
    AnalysisResult,
    ControlStatus,
    Criticality,
    DecisionStatus,
    Review,
    Sentiment,
    make_fingerprint,
    normalize_record,
    normalize_text,
)
from .migrations import DEFAULT_TOPICS, MIGRATION_V1, MIGRATION_V2, MIGRATION_V3
from .services import ALIASES, FeedbackService, build_report, read_csv, read_records, read_xlsx
from .storage import Database

__all__ = [
    "ANALYSIS_VERSION", "AnalysisPipeline", "AnalysisResult", "ControlStatus",
    "Criticality", "Database", "DecisionStatus", "FeedbackService", "Review",
    "Sentiment", "normalize_record", "normalize_text", "make_fingerprint",
    "read_csv", "read_xlsx", "read_records", "build_report", "MIGRATION_V1",
    "MIGRATION_V2", "MIGRATION_V3", "DEFAULT_TOPICS", "ALIASES", "POSITIVE",
    "NEGATIVE", "INTENSIFIERS", "NEGATIONS", "ASPECT_RULES", "CRITICAL_MARKERS",
    "HIGH_MARKERS",
]
