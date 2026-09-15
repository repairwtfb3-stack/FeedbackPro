from __future__ import annotations
import csv, hashlib, json, random, shutil, sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Iterable
from .analysis import AnalysisPipeline
from .domain import ANALYSIS_VERSION, ControlStatus, Criticality, Sentiment, normalize_record
from .services import FeedbackService, build_report, read_records
from .storage import Database

def audit(db:Database,event_type:str,entity_type:str,entity_id:str|None=None,payload:dict|None=None,actor:str|None=None)->int:
    cur=db.conn.execute("INSERT INTO audit_events(event_type,entity_type,entity_id,actor,payload_json,created_at) VALUES(?,?,?,?,?,?)",(event_type,entity_type,entity_id,actor,json.dumps(payload or {},ensure_ascii=False,default=str),datetime.utcnow().isoformat()))
    db.conn.commit(); return int(cur.lastrowid)

def audit_history(db:Database,entity_type:str|None=None,entity_id:str|None=None):
    sql="SELECT * FROM audit_events"; args=[]; where=[]
    if entity_type: where.append("entity_type=?"); args.append(entity_type)
    if entity_id is not None: where.append("entity_id=?"); args.append(entity_id)
    if where: sql += " WHERE "+" AND ".join(where)
    sql += " ORDER BY id DESC"; out=[]
    for r in db.conn.execute(sql,args).fetchall():
        d=dict(r); d["payload"]=json.loads(d.pop("payload_json")); out.append(d)
    return out

def preview_import(path:str|Path,limit:int=20):
    p=Path(path); rows=read_records(p); cols=sorted({k for r in rows for k in r}); ok=[]; errors=[]
    for i,row in enumerate(rows,2):
        try: normalize_record(row,source_file=p.name); ok.append(row)
        except Exception as exc: errors.append({"row":i,"error":str(exc)})
    return {"path":str(p),"source_file":p.name,"columns":cols,"total":len(rows),"accepted":len(ok),"rejected":len(errors),"errors":errors,"preview":ok[:limit]}

def import_a3(db:Database,path:str|Path,analyze:bool=True):
    db.migrate(3); p=Path(path); prev=preview_import(p); sha=hashlib.sha256(p.read_bytes()).hexdigest(); started=datetime.utcnow().isoformat()
    cur=db.conn.execute("INSERT INTO import_batches(source_file,file_sha256,total_rows,started_at) VALUES(?,?,?,?)",(p.name,sha,prev["total"],started)); bid=int(cur.lastrowid); db.conn.commit()
    stats=FeedbackService(db).import_file(p,analyze)
    db.conn.execute("UPDATE import_batches SET accepted_rows=?,duplicate_rows=?,rejected_rows=?,completed_at=? WHERE id=?",(stats["inserted"],stats["duplicates"],stats["rejected"],datetime.utcnow().isoformat(),bid)); db.conn.commit()
    audit(db,"import","import_batch",str(bid),{"source_file":p.name,**stats}); return {**prev,**stats,"batch_id":bid}

def export_report(db:Database,path:str|Path):
    p=Path(path); p.write_text(build_report(db.dashboard()),encoding="utf-8"); audit(db,"export_report","report",str(p),{"path":str(p)}); return str(p)

def _review_rows(db:Database,**f):
    where=[]; args=[]
    if f.get("search"):
        q=f"%{f['search'].casefold()}%"; where.append("(LOWER(r.text) LIKE ? OR LOWER(COALESCE(r.author,'')) LIKE ?)"); args += [q,q]
    for col,key in (("r.source","source"),("r.channel","channel"),("a.sentiment","sentiment"),("a.criticality","criticality")):
        if f.get(key): where.append(f"{col}=?"); args.append(f[key])
    if f.get("aspect"): where.append("a.aspects_json LIKE ?"); args.append(f'%"{f["aspect"]}"%')
    if f.get("unverified"): where.append("el.id IS NULL")
    order={"id_asc":"r.id ASC","date_asc":"r.review_date ASC,r.id ASC","date_desc":"r.review_date DESC,r.id DESC"}.get(f.get("sort"),"r.id DESC")
    sql="""SELECT r.*,a.sentiment,a.sentiment_score,a.confidence,a.aspects_json,a.criticality,a.analysis_version,a.explanation,el.id expert_label_id,el.sentiment verified_sentiment,el.aspects_json verified_aspects_json,el.criticality verified_criticality FROM reviews r LEFT JOIN analysis_results a ON a.review_id=r.id LEFT JOIN expert_labels el ON el.review_id=r.id AND el.is_current=1"""
    if where: sql += " WHERE "+" AND ".join(where)
    sql += f" ORDER BY {order} LIMIT ? OFFSET ?"; args += [int(f.get("limit",200)),int(f.get("offset",0))]; out=[]
    for r in db.conn.execute(sql,args).fetchall():
        d=dict(r); d["aspects"]=json.loads(d.pop("aspects_json")) if d.get("aspects_json") else []; d["verified_aspects"]=json.loads(d.pop("verified_aspects_json")) if d.get("verified_aspects_json") else []; out.append(d)
    return out

def review_search(db:Database,**filters): return _review_rows(db,**filters)

def review_detail(db:Database,rid:int):
    rows=_review_rows(db,limit=100000); d=next((x for x in rows if x["id"]==rid),None)
    if not d: raise KeyError(rid)
    d["expert_history"]=expert_history(db,rid); d["decisions"]=[x for x in db.decision_records() if rid in x["review_ids"]]; d["audit"]=audit_history(db,"review",str(rid)); return d

def batch_reanalyze(db:Database,ids:Iterable[int]):
    pipeline=AnalysisPipeline(); n=0
    for rid in dict.fromkeys(int(x) for x in ids):
        db.save_analysis(pipeline.analyze(db.get_review(rid))); audit(db,"reanalyze","review",str(rid),{"analysis_version":ANALYSIS_VERSION}); n+=1
    return n

def expert_current(db:Database,rid:int):
    r=db.conn.execute("SELECT * FROM expert_labels WHERE review_id=? AND is_current=1",(rid,)).fetchone()
    if not r: return None
    d=dict(r); d["aspects"]=json.loads(d.pop("aspects_json")); return d

def expert_history(db:Database,rid:int):
    out=[]
    for r in db.conn.execute("SELECT * FROM expert_labels WHERE review_id=? ORDER BY revision DESC",(rid,)).fetchall():
        d=dict(r); d["aspects"]=json.loads(d.pop("aspects_json")); out.append(d)
    return out

def expert_verify(db:Database,rid:int,sentiment:str,aspects:Iterable[str],criticality:str,comment:str="",reviewer:str="operator"):
    Sentiment(sentiment); Criticality(criticality); analysis=db.get_analysis(rid)
    if not analysis: raise ValueError("review is not analyzed")
    prev=db.conn.execute("SELECT MAX(revision) m FROM expert_labels WHERE review_id=?",(rid,)).fetchone()["m"] or 0
    db.conn.execute("UPDATE expert_labels SET is_current=0 WHERE review_id=? AND is_current=1",(rid,))
    cur=db.conn.execute("INSERT INTO expert_labels(review_id,sentiment,aspects_json,criticality,comment,reviewer,revision,is_current,created_at) VALUES(?,?,?,?,?,?,?,?,?)",(rid,sentiment,json.dumps(sorted(set(aspects)),ensure_ascii=False),criticality,comment or None,reviewer,int(prev)+1,1,datetime.utcnow().isoformat())); lid=int(cur.lastrowid)
    for field,auto_value,verified_value in (("sentiment",analysis.sentiment.value,sentiment),("aspects",json.dumps(analysis.aspects,ensure_ascii=False),json.dumps(sorted(set(aspects)),ensure_ascii=False)),("criticality",analysis.criticality.value,criticality)):
        db.conn.execute("INSERT INTO analysis_overrides(review_id,expert_label_id,field_name,auto_value,verified_value,created_at) VALUES(?,?,?,?,?,?)",(rid,lid,field,auto_value,verified_value,datetime.utcnow().isoformat()))
    db.conn.commit(); audit(db,"expert_verify","review",str(rid),{"label_id":lid,"revision":int(prev)+1},reviewer); return lid

def export_reviews(db:Database,path:str|Path,rows:list[dict]|None=None):
    p=Path(path); rows=rows if rows is not None else _review_rows(db,limit=100000); fields=["id","source","channel","review_date","author","rating","text","sentiment","criticality","aspects","verified_sentiment","verified_criticality","verified_aspects"]
    if p.suffix.lower()==".csv":
        with p.open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader()
            for r in rows: w.writerow({**r,"aspects":",".join(r.get("aspects") or []),"verified_aspects":",".join(r.get("verified_aspects") or [])})
    elif p.suffix.lower()==".xlsx":
        from openpyxl import Workbook
        wb=Workbook(); ws=wb.active; ws.title="Отзывы"; ws.append(fields)
        for r in rows: ws.append([",".join(r.get(k) or []) if k in {"aspects","verified_aspects"} else r.get(k) for k in fields])
        wb.save(p); wb.close()
    else: raise ValueError("export format must be .csv or .xlsx")
    audit(db,"export_reviews","reviews",str(p),{"rows":len(rows)}); return str(p)

def sample_manifest(db:Database,size:int=300,seed:int=20260915):
    ids=[r.id for r in db.list_reviews() if r.id is not None]
    if len(ids)<size: raise ValueError(f"corpus has {len(ids)} reviews; {size} required; synthetic padding is forbidden")
    return {"size":size,"seed":seed,"algorithm":"python.random.Random.sample/v1","review_ids":sorted(random.Random(seed).sample(ids,size))}

def _class_metrics(true:list[str],pred:list[str],labels:list[str]):
    cm={a:{b:0 for b in labels} for a in labels}
    for t,p in zip(true,pred): cm[t][p]+=1
    per={}
    for lab in labels:
        tp=cm[lab][lab]; fp=sum(cm[x][lab] for x in labels if x!=lab); fn=sum(cm[lab][x] for x in labels if x!=lab); precision=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0; f1=2*precision*recall/(precision+recall) if precision+recall else 0; per[lab]={"precision":precision,"recall":recall,"f1":f1}
    return {"accuracy":sum(cm[x][x] for x in labels)/len(true),"macro_f1":sum(per[x]["f1"] for x in labels)/len(labels),"confusion_matrix":cm,"per_class":per}

def quality_metrics(db:Database,ids:Iterable[int]|None=None):
    allowed=set(ids) if ids is not None else None; st=[]; sp=[]; ct=[]; cp=[]; true_aspects=[]; pred_aspects=[]; used=[]
    for r in db.list_reviews():
        if allowed is not None and r.id not in allowed: continue
        e=expert_current(db,r.id); a=db.get_analysis(r.id)
        if e and a:
            used.append(r.id); st.append(e["sentiment"]); sp.append(a.sentiment.value); ct.append(e["criticality"]); cp.append(a.criticality.value); true_aspects.append(set(e["aspects"])); pred_aspects.append(set(a.aspects))
    if not used: raise ValueError("expert labels required")
    sentiment=_class_metrics(st,sp,["positive","neutral","negative"]); criticality=_class_metrics(ct,cp,["low","medium","high","critical"]); order={x:i for i,x in enumerate(["low","medium","high","critical"])}; criticality["ordinal_mae"]=sum(abs(order[x]-order[y]) for x,y in zip(ct,cp))/len(ct)
    labels=sorted(set().union(*true_aspects,*pred_aspects)); tp=fp=fn=0; f1s=[]
    for lab in labels:
        ltp=sum(lab in t and lab in p for t,p in zip(true_aspects,pred_aspects)); lfp=sum(lab not in t and lab in p for t,p in zip(true_aspects,pred_aspects)); lfn=sum(lab in t and lab not in p for t,p in zip(true_aspects,pred_aspects)); tp+=ltp; fp+=lfp; fn+=lfn; precision=ltp/(ltp+lfp) if ltp+lfp else 0; recall=ltp/(ltp+lfn) if ltp+lfn else 0; f1s.append(2*precision*recall/(precision+recall) if precision+recall else 0)
    precision=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0; aspects={"micro_precision":precision,"micro_recall":recall,"micro_f1":2*precision*recall/(precision+recall) if precision+recall else 0,"macro_f1":sum(f1s)/len(f1s) if f1s else 0,"exact_match_ratio":sum(t==p for t,p in zip(true_aspects,pred_aspects))/len(true_aspects)}
    return {"review_ids":used,"sample_size":len(used),"sentiment":sentiment,"aspects":aspects,"criticality":criticality}

def persist_quality(db:Database,ids:Iterable[int]|None=None):
    metrics=quality_metrics(db,ids); manifest=metrics.pop("review_ids"); metrics.pop("sample_size",None)
    cur=db.conn.execute("INSERT INTO quality_runs(analysis_version,sample_manifest_json,sample_size,labeled_count,created_at) VALUES(?,?,?,?,?)",(ANALYSIS_VERSION,json.dumps(manifest),len(manifest),len(manifest),datetime.utcnow().isoformat())); qid=int(cur.lastrowid)
    for group,values in metrics.items():
        if not isinstance(values,dict): continue
        for name,value in values.items():
            if isinstance(value,(int,float)): db.conn.execute("INSERT INTO quality_run_metrics VALUES(?,?,?,?)",(qid,group,name,float(value)))
    db.conn.commit(); audit(db,"quality_run","quality",str(qid),{"sample_size":len(manifest)}); return qid

def quality_run(db:Database,qid:int):
    r=db.conn.execute("SELECT * FROM quality_runs WHERE id=?",(qid,)).fetchone()
    if not r: return None
    d=dict(r); d["metrics"]={f"{x['metric_group']}.{x['metric_name']}":x["metric_value"] for x in db.conn.execute("SELECT * FROM quality_run_metrics WHERE quality_run_id=?",(qid,)).fetchall()}; return d

def analytics(db:Database):
    d=db.dashboard(); q=db.conn.execute; d["by_source"]={r["source"]:r["c"] for r in q("SELECT source,COUNT(*) c FROM reviews GROUP BY source").fetchall()}; d["by_channel"]={r["channel"]:r["c"] for r in q("SELECT channel,COUNT(*) c FROM reviews GROUP BY channel").fetchall()}; d["trend"]=[dict(r) for r in q("SELECT review_date date,COUNT(*) count FROM reviews WHERE review_date IS NOT NULL GROUP BY review_date ORDER BY review_date").fetchall()]; d["overdue_controls"]=q("SELECT COUNT(*) c FROM control_items WHERE due_date IS NOT NULL AND due_date<date('now') AND status!='verified'").fetchone()["c"]; return d

def drilldown(db:Database,kind:str,value:str):
    if kind not in {"sentiment","criticality","source","channel","aspect"}: raise ValueError("unsupported drilldown")
    return _review_rows(db,**{kind:value})

DECISION_ALLOWED={"created":{"planned"},"planned":{"in_progress"},"in_progress":{"completed"},"completed":{"verified"},"verified":set()}; CONTROL_ALLOWED={"planned":{"in_progress"},"in_progress":{"completed"},"completed":{"verified"},"verified":set()}

def create_decision(db:Database,title:str,description:str,priority:str,review_ids:Iterable[int],due:date|None=None):
    ids=list(review_ids); did=db.create_decision(title,description,priority,ids,due); audit(db,"decision_create","decision",str(did),{"review_ids":ids}); return did

def transition_decision(db:Database,did:int,new:str):
    row=next((x for x in db.decision_records() if x["id"]==did),None)
    if not row: raise KeyError(did)
    if new not in DECISION_ALLOWED[row["status"]]: raise ValueError("invalid decision transition")
    db.conn.execute("UPDATE decisions SET status=? WHERE id=?",(new,did)); db.conn.commit(); audit(db,"decision_transition","decision",str(did),{"from":row["status"],"to":new})

def set_control(db:Database,did:int,new:str,due:date|None=None,outcome:str|None=None):
    row=next((x for x in db.control_records() if x["decision_id"]==did),None)
    if row:
        if new!=row["status"] and new not in CONTROL_ALLOWED[row["status"]]: raise ValueError("invalid control transition")
    elif new!="planned": raise ValueError("control must start planned")
    cid=db.set_control(did,ControlStatus(new),due,outcome); audit(db,"control_change","control",str(cid),{"decision_id":did,"status":new}); return cid

def backup(db:Database,path:str|Path):
    dest=sqlite3.connect(path); db.conn.backup(dest); dest.close(); audit(db,"backup","database",str(path),{}); return str(path)

def restore(source:str|Path,target:str|Path):
    src=Database(source)
    try:
        if src.conn.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or src.current_version() not in (1,2,3): raise ValueError("invalid backup")
    finally: src.close()
    shutil.copy2(source,target); return str(target)

def integrity(db:Database): return db.conn.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
