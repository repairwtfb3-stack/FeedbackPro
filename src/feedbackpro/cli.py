from __future__ import annotations
import argparse, json
from pathlib import Path
from .core import Database, FeedbackService

def main(argv=None) -> int:
    p=argparse.ArgumentParser(prog="feedbackpro")
    p.add_argument("--db",default="feedbackpro.db")
    sub=p.add_subparsers(dest="cmd",required=True)
    imp=sub.add_parser("import"); imp.add_argument("path")
    sub.add_parser("analyze"); sub.add_parser("dashboard")
    rep=sub.add_parser("report"); rep.add_argument("path")
    sub.add_parser("gate")
    a=p.parse_args(argv)
    if a.cmd=="gate":
        from .gate_a2 import main as gate
        return gate()
    with Database(a.db) as db:
        s=FeedbackService(db); s.initialize()
        if a.cmd=="import": print(json.dumps(s.import_file(a.path),ensure_ascii=False,indent=2))
        elif a.cmd=="analyze": print(s.analyze_all())
        elif a.cmd=="dashboard": print(json.dumps(s.dashboard(),ensure_ascii=False,indent=2))
        elif a.cmd=="report":
            Path(a.path).write_text(s.report(),encoding="utf-8"); print(a.path)
    return 0
if __name__=="__main__": raise SystemExit(main())
