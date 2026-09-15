from __future__ import annotations
import json, sys
from pathlib import Path

def main()->int:
    try:
        from PySide6.QtCore import QObject,Property,QUrl,Signal,Slot
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtQml import QQmlApplicationEngine
    except ImportError as exc:
        raise SystemExit("GUI requires PySide6") from exc
    from .backend import A3Backend
    class Backend(QObject):
        changed=Signal(); messageChanged=Signal()
        def __init__(self): super().__init__(); self.b=A3Backend()
        @Property(str,notify=messageChanged)
        def message(self): return self.b.message
        @Property(str,notify=changed)
        def dashboardJson(self): return json.dumps(self.b.dashboard(),ensure_ascii=False)
        @Property(str,notify=changed)
        def reviewsJson(self): return json.dumps(self.b.search_reviews(),ensure_ascii=False)
        @Property(str,notify=changed)
        def decisionsJson(self): return json.dumps(self.b.db.decision_records(),ensure_ascii=False)
        @Property(str,notify=changed)
        def controlsJson(self): return json.dumps(self.b.db.control_records(),ensure_ascii=False)
        @Property(str,notify=changed)
        def topicsJson(self): return json.dumps(self.b.db.topics(),ensure_ascii=False)
        def emit(self): self.messageChanged.emit(); self.changed.emit()
        @Slot(str,result=str)
        def previewImport(self,path):
            try:
                local=QUrl(path).toLocalFile() if path.startswith("file:") else path; return json.dumps(self.b.preview_import(local),ensure_ascii=False,default=str)
            except Exception as exc: return json.dumps({"error":str(exc)},ensure_ascii=False)
        @Slot(str,result=str)
        def importFile(self,path):
            try:
                local=QUrl(path).toLocalFile() if path.startswith("file:") else path; result=self.b.import_file(local); self.emit(); return json.dumps(result,ensure_ascii=False,default=str)
            except Exception as exc:
                self.b.message=f"Ошибка: {exc}"; self.emit(); return json.dumps({"error":str(exc)},ensure_ascii=False)
        @Slot(str,result=str)
        def exportReport(self,path):
            try:
                local=QUrl(path).toLocalFile() if path.startswith("file:") else path; result=self.b.export_report(local); self.emit(); return result
            except Exception as exc: self.b.message=f"Ошибка: {exc}"; self.emit(); return ""
        @Slot(str,result=str)
        def exportReviews(self,path):
            try:
                local=QUrl(path).toLocalFile() if path.startswith("file:") else path; result=self.b.export_reviews(local); self.emit(); return result
            except Exception as exc: self.b.message=f"Ошибка: {exc}"; self.emit(); return ""
        @Slot(str,result=str)
        def searchReviews(self,filtersJson):
            try: return json.dumps(self.b.search_reviews(json.loads(filtersJson or "{}")),ensure_ascii=False)
            except Exception as exc: return json.dumps({"error":str(exc)},ensure_ascii=False)
        @Slot(int,result=str)
        def reviewDetail(self,rid):
            try: return json.dumps(self.b.review_detail(rid),ensure_ascii=False,default=str)
            except Exception as exc: return json.dumps({"error":str(exc)},ensure_ascii=False)
        @Slot(str,result=int)
        def reanalyze(self,idsJson):
            try: result=self.b.reanalyze(json.loads(idsJson)); self.emit(); return result
            except Exception: self.emit(); return 0
        @Slot(int,str,str,str,str,result=int)
        def verify(self,rid,sentiment,aspectsCsv,criticality,comment):
            try:
                result=self.b.verify(rid,sentiment,[a.strip() for a in aspectsCsv.split(",") if a.strip()],criticality,comment); self.emit(); return result
            except Exception: self.emit(); return 0
        @Slot(int,int,result=str)
        def makeSample(self,size,seed):
            try: return json.dumps(self.b.sample(size,seed),ensure_ascii=False)
            except Exception as exc: return json.dumps({"error":str(exc)},ensure_ascii=False)
        @Slot(str,result=int)
        def qualityRun(self,idsJson):
            try: result=self.b.quality(json.loads(idsJson) if idsJson else None); self.emit(); return result
            except Exception: self.emit(); return 0
        @Slot(str,str,str,str,str,result=int)
        def createDecision(self,title,description,priority,idsJson,due):
            try: result=self.b.create_decision(title,description,priority,json.loads(idsJson),due); self.emit(); return result
            except Exception: self.emit(); return 0
        @Slot(int,str)
        def transitionDecision(self,did,status):
            try: self.b.transition_decision(did,status); self.emit()
            except Exception: self.emit()
        @Slot(int,str,str,str,result=int)
        def setControl(self,did,status,due,outcome):
            try: result=self.b.set_control(did,status,due,outcome); self.emit(); return result
            except Exception: self.emit(); return 0
        @Slot(str,result=bool)
        def backup(self,path):
            try:
                local=QUrl(path).toLocalFile() if path.startswith("file:") else path; self.b.backup(local); self.emit(); return True
            except Exception: self.emit(); return False
        @Slot(result=bool)
        def integrity(self): return self.b.integrity()
        @Slot(str,str,result=str)
        def drilldown(self,kind,value): return json.dumps(self.b.drilldown(kind,value),ensure_ascii=False)
        @Slot(str,str,bool)
        def setTopic(self,code,title,active):
            self.b.db.set_topic(code,title,active); from .a3 import audit; audit(self.b.db,"dictionary_change","topic",code,{"title":title,"active":active}); self.emit()
        @Slot(str,str)
        def setSetting(self,key,value):
            self.b.db.set_setting(key,value); from .a3 import audit; audit(self.b.db,"settings_change","setting",key,{"value":value}); self.emit()
    app=QGuiApplication(sys.argv); engine=QQmlApplicationEngine(); backend=Backend(); engine.rootContext().setContextProperty("backend",backend); engine.load(QUrl.fromLocalFile(str(Path(__file__).with_name("Main.qml"))))
    if not engine.rootObjects(): return 2
    rc=app.exec(); backend.b.close(); return rc

if __name__=="__main__": raise SystemExit(main())
