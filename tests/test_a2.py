from feedbackpro.core import AnalysisPipeline, ControlStatus, Criticality, Database, FeedbackService, Sentiment, normalize_record
from feedbackpro.gate_a2 import run_gate

def test_normalization_analysis():
    r=normalize_record({"source":"site","date":"01.09.2026","rating":1,"text":"Дважды списали деньги, поддержка не отвечает"})
    a=AnalysisPipeline().analyze(r)
    assert a.sentiment is Sentiment.NEGATIVE
    assert "support" in a.aspects
    assert a.criticality in {Criticality.HIGH,Criticality.CRITICAL}

def test_e2e(tmp_path):
    db=Database(tmp_path/"fp.db"); s=FeedbackService(db); assert s.initialize()==2
    stats=s.import_rows([
        {"id":"1","source":"site","rating":5,"text":"Отличный товар и быстрая доставка"},
        {"id":"2","source":"site","rating":1,"text":"Брак, дважды списали деньги, поддержка не отвечает"},
        {"id":"2","source":"site","rating":1,"text":"дубль"},
        {"id":"3","source":"site","text":""},
    ])
    assert stats=={"inserted":2,"duplicates":1,"rejected":1,"analyzed":3}
    reviews=db.list_reviews(); did=s.create_decision("Проверить","Возврат средств","critical",reviews[1].id)
    s.set_control(did,ControlStatus.IN_PROGRESS,outcome="В работе")
    d=s.dashboard(); assert d["total_reviews"]==2 and d["decision_count"]==1 and d["negative_reviews"]>=1
    assert "BEFORE/AFTER" in s.report(); db.close()
    reopened=Database(tmp_path/"fp.db"); reopened.migrate(); assert reopened.dashboard()["total_reviews"]==2; reopened.close()

def test_gate():
    results=run_gate()
    assert len(results)==20
    assert [x for x in results if not x[1]]==[]
