from __future__ import annotations

import tempfile
from pathlib import Path

from .core import AnalysisPipeline, ControlStatus, Criticality, Database, FeedbackService, Sentiment, normalize_record, read_csv, read_xlsx

TRACEABILITY = {f"A2.{i}" for i in range(1, 12)}
SCREENS = [f"S{i:02d}" for i in range(1, 11)]

def run_gate() -> list[tuple[str, bool, str]]:
    out: list[tuple[str, bool, str]] = []
    check = lambda gid, ok, note: out.append((gid, bool(ok), note))
    with tempfile.TemporaryDirectory(prefix="feedbackpro-a2-") as td:
        root = Path(td); db_path = root / "gate.db"; db = Database(db_path)
        check("G-A2-01", db.migrate(1) == 1, "migration v1")
        check("G-A2-02", db.migrate(2) == 2 and db.current_version() == 2, "migration v1→v2")
        service = FeedbackService(db)
        csv_path = root / "reviews.csv"
        csv_path.write_text("id;дата;оценка;источник;канал;отзыв\n1;2026-09-01;5;site;web;Отличный сервис и быстрая доставка\n2;2026-09-02;1;site;web;Дважды списали деньги, поддержка не отвечает\n", encoding="utf-8")
        rows = read_csv(csv_path); imported = service.import_file(csv_path)
        check("G-A2-03", len(rows) == 2 and imported["inserted"] == 2, "CSV import")
        try:
            from openpyxl import Workbook
            wb = Workbook(); ws = wb.active
            ws.append(["id", "дата", "оценка", "источник", "отзыв"])
            ws.append(["x1", "2026-09-04", 4, "xlsx", "Хороший товар"])
            xlsx = root / "reviews.xlsx"; wb.save(xlsx); wb.close()
            xrows = read_xlsx(xlsx); xlsx_ok = len(xrows) == 1 and xrows[0]["text"] == "Хороший товар"
        except Exception:
            xlsx_ok = False
        check("G-A2-04", xlsx_ok, "XLSX import")
        again = service.import_file(csv_path)
        check("G-A2-05", again["duplicates"] == 2 and len(db.list_reviews()) == 2, "dedup")
        first, second = db.list_reviews(); a1, a2 = db.get_analysis(first.id), db.get_analysis(second.id)
        check("G-A2-06", a1 is not None and a2 is not None and a1.sentiment is Sentiment.POSITIVE and a2.sentiment is Sentiment.NEGATIVE, "sentiment")
        check("G-A2-07", a1 is not None and "delivery" in a1.aspects and a2 is not None and "support" in a2.aspects, "aspects")
        check("G-A2-08", a2 is not None and a2.criticality in {Criticality.HIGH, Criticality.CRITICAL}, "criticality")
        check("G-A2-09", AnalysisPipeline().analyze(first).analysis_version != "", "single analysis")
        check("G-A2-10", service.analyze_all() == 2, "batch analysis")
        db.close(); db = Database(db_path); db.migrate()
        check("G-A2-11", len(db.list_reviews()) == 2 and db.get_analysis(second.id) is not None, "persistence/reopen")
        service = FeedbackService(db)
        decision_id = service.create_decision("Проверить списание", "Проверить платёж и подготовить ответ", "critical", second.id)
        decisions = db.decision_records()
        check("G-A2-12", decision_id > 0 and decisions[0]["review_ids"] == [second.id], "review→decision")
        control_id = service.set_control(decision_id, ControlStatus.IN_PROGRESS, outcome="Проверка начата")
        check("G-A2-13", control_id > 0 and db.control_records()[0]["status"] == "in_progress", "decision→control")
        stats = db.dashboard()
        check("G-A2-14", stats["total_reviews"] == 2 and stats["decision_count"] == 1, "KPI recomputation")
        qml = Path(__file__).with_name("Main.qml"); qml_text = qml.read_text(encoding="utf-8") if qml.exists() else ""
        check("G-A2-15", all(screen in qml_text for screen in SCREENS), "S01–S10 manifest")
        check("G-A2-16", "Аналитический отчёт" in service.report() and "Всего отзывов" in service.report(), "report generation")
        offline = AnalysisPipeline().analyze(normalize_record({"source": "offline", "text": "Хороший товар"}))
        check("G-A2-17", offline.sentiment is Sentiment.POSITIVE, "offline deterministic analysis")
        clean = Database(root / "clean.db"); clean_ok = clean.migrate() == 2 and clean.dashboard()["total_reviews"] == 0; clean.close()
        check("G-A2-18", clean_ok, "clean database")
        check("G-A2-19", db.dashboard()["analyzed_reviews"] == 2 and db.dashboard()["critical_reviews"] >= 1, "populated database")
        trace = Path(__file__).resolve().parents[2] / "docs" / "A2_BASELINE.md"; trace_text = trace.read_text(encoding="utf-8") if trace.exists() else ""
        check("G-A2-20", all(item in trace_text for item in TRACEABILITY), "traceability A2.1–A2.11")
        db.close()
    return out

def main() -> int:
    results = run_gate()
    for gid, ok, note in results: print(f"{gid}: {'PASS' if ok else 'FAIL'} — {note}")
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\nGate A2: {passed}/{len(results)} PASS")
    if passed == 20:
        print("A2 WORK_VERIFIED = YES"); return 0
    print("A2 WORK_VERIFIED = NO"); return 1

if __name__ == "__main__": raise SystemExit(main())
