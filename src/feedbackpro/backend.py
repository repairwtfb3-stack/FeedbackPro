from __future__ import annotations
from datetime import date
from pathlib import Path
from . import a3
from .storage import Database
from .services import FeedbackService

class A3Backend:
    def __init__(self,db_path:str|Path="feedbackpro.db"):
        self.db=Database(db_path); FeedbackService(self.db).initialize_a3(); self.message="Готово"; self.error=""; self.busy=False
    def close(self): self.db.close()
    def dashboard(self): return a3.analytics(self.db)
    def preview_import(self,path:str): return a3.preview_import(path)
    def import_file(self,path:str):
        r=a3.import_a3(self.db,path); self.message=f"Импорт: {r['inserted']} новых, {r['duplicates']} дублей, {r['rejected']} ошибок"; return r
    def export_report(self,path:str): return a3.export_report(self.db,path)
    def export_reviews(self,path:str): return a3.export_reviews(self.db,path)
    def search_reviews(self,filters=None): return a3.review_search(self.db,**(filters or {}))
    def review_detail(self,rid:int): return a3.review_detail(self.db,rid)
    def reanalyze(self,ids): return a3.batch_reanalyze(self.db,ids)
    def verify(self,rid:int,sentiment:str,aspects:list[str],criticality:str,comment:str="",reviewer:str="operator"): return a3.expert_verify(self.db,rid,sentiment,aspects,criticality,comment,reviewer)
    def sample(self,size=300,seed=20260915): return a3.sample_manifest(self.db,size,seed)
    def quality(self,ids=None): return a3.persist_quality(self.db,ids)
    def create_decision(self,title,description,priority,review_ids,due=""): return a3.create_decision(self.db,title,description,priority,review_ids,date.fromisoformat(due) if due else None)
    def transition_decision(self,did,status): return a3.transition_decision(self.db,did,status)
    def set_control(self,did,status,due="",outcome=""): return a3.set_control(self.db,did,status,date.fromisoformat(due) if due else None,outcome or None)
    def backup(self,path): return a3.backup(self.db,path)
    def integrity(self): return a3.integrity(self.db)
    def drilldown(self,kind,value): return a3.drilldown(self.db,kind,value)
