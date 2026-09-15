from feedbackpro.core import AnalysisPipeline, Database, FeedbackService, Sentiment, normalize_record
from feedbackpro.queries import schema_snapshot


def test_migration_v2_to_v3_preserves_a2_data(tmp_path):
    db = Database(tmp_path / "upgrade.db")
    service = FeedbackService(db)
    assert service.initialize() == 2
    stats = service.import_rows([{"id": "r1", "source": "site", "rating": 5, "text": "Отличный товар"}])
    assert stats["inserted"] == 1
    review_id = db.list_reviews()[0].id
    assert db.get_analysis(review_id).sentiment is Sentiment.POSITIVE

    assert db.migrate(3) == 3
    assert db.current_version() == 3
    assert len(db.list_reviews()) == 1
    assert db.get_analysis(review_id).sentiment is Sentiment.POSITIVE

    snap = schema_snapshot(db.conn)
    expected = {"expert_labels", "analysis_overrides", "audit_events", "import_batches", "quality_runs", "quality_run_metrics"}
    assert expected.issubset(set(snap["tables"]))
    assert [x["version"] for x in snap["migrations"]] == [1, 2, 3]
    db.close()


def test_clean_v3_and_idempotency(tmp_path):
    db = Database(tmp_path / "clean-v3.db")
    assert db.migrate(3) == 3
    assert db.migrate(3) == 3
    assert db.dashboard()["total_reviews"] == 0
    db.close()


def test_a2_compatibility_surface_stays_intact(tmp_path):
    db = Database(tmp_path / "compat.db")
    service = FeedbackService(db)
    assert service.initialize() == 2
    assert db.current_version() == 2
    review = normalize_record({"source": "offline", "text": "Хороший товар"})
    assert AnalysisPipeline().analyze(review).sentiment is Sentiment.POSITIVE
    db.close()
