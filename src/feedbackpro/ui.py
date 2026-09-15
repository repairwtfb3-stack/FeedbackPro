from __future__ import annotations
import json, sys
from datetime import date
from pathlib import Path
from .core import ControlStatus, Database, FeedbackService

def main() -> int:
    try:
        from PySide6.QtCore import QObject, Property, QUrl, Signal, Slot
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtQml import QQmlApplicationEngine
    except ImportError as exc:
        raise SystemExit("GUI requires PySide6") from exc
    class Backend(QObject):
        changed=Signal(); messageChanged=Signal()
        def __init__(self):
            super().__init__(); self.db=Database("feedbackpro.db"); self.s=FeedbackService(self.db); self.s.initialize(); self._message="Готово"
        @Property(str,notify=messageChanged)
        def message(self): return self._message
        @Property(str,notify=changed)
        def dashboardJson(self): return json.dumps(self.db.dashboard(),ensure_ascii=False)
        @Property(str,notify=changed)
        def reviewsJson(self): return json.dumps(self.db.review_records(),ensure_ascii=False)
        @Property(str,notify=changed)
        def decisionsJson(self): return json.dumps(self.db.decision_records(),ensure_ascii=False)
        @Property(str,notify=changed)
        def controlsJson(self): return json.dumps(self.db.control_records(),ensure_ascii=False)
        @Property(str,notify=changed)
        def topicsJson(self): return json.dumps(self.db.topics(),ensure_ascii=False)
        def msg(self,text): self._message=text; self.messageChanged.emit(); self.changed.emit()
        @Slot()
        def analyzeAll(self):
            try: self.msg("Проанализировано: "+str(self.s.analyze_all()))
            except Exception as e: self.msg("Ошибка: "+str(e))
        @Slot(str,str,str,int,str)
        def createDecision(self,title,description,priority,review_id,due):
            try: self.msg("Решение #"+str(self.s.create_decision(title,description,priority,review_id,date.fromisoformat(due) if due else None)))
            except Exception as e: self.msg("Ошибка: "+str(e))
        @Slot(int,str,str,str)
        def setControl(self,decision_id,status,due,outcome):
            try: self.s.set_control(decision_id,ControlStatus(status),date.fromisoformat(due) if due else None,outcome or None); self.msg("Контроль сохранён")
            except Exception as e: self.msg("Ошибка: "+str(e))
        @Slot(str,str,bool)
        def setTopic(self,code,title,active):
            try: self.db.set_topic(code,title,active); self.msg("Тема сохранена")
            except Exception as e: self.msg("Ошибка: "+str(e))
        @Slot(str,str)
        def setSetting(self,key,value):
            try: self.db.set_setting(key,value); self.msg("Настройка сохранена")
            except Exception as e: self.msg("Ошибка: "+str(e))
    app=QGuiApplication(sys.argv); engine=QQmlApplicationEngine(); backend=Backend(); engine.rootContext().setContextProperty("backend",backend); engine.load(QUrl.fromLocalFile(str(Path(__file__).with_name("Main.qml"))))
    if not engine.rootObjects(): return 2
    return app.exec()

if __name__=="__main__": raise SystemExit(main())
