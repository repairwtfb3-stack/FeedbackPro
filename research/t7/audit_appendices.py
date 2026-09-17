#!/usr/bin/env python3
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "research/t7/build_appendices/pdf/WKR_Methodika_EG_Appendices_A_T.pdf"
REPORT = ROOT / "research/t7/build_appendices/APPENDICES_AUDIT.md"
LETTERS = ["А", "Б", "В", "Г", "Д", "Е", "Ж", "И", "К", "Л", "М", "Н", "П", "Р", "С", "Т"]


def main() -> None:
    reader = PdfReader(PDF)
    pages = len(reader.pages)
    text = "\n".join((p.extract_text() or "") for p in reader.pages)

    missing = [letter for letter in LETTERS if f"ПРИЛОЖЕНИЕ {letter}" not in text]
    if missing:
        raise RuntimeError(f"Missing appendices: {missing}")
    if not 20 <= pages <= 100:
        raise RuntimeError(f"Unexpected appendix page count: {pages}")

    required = [
        "1200", "1192", "RuStore", "01.09.2025", "31.08.2026",
        "P4", "P5", "C3/C4", "99,33", "S01", "S10", "E0", "E8",
        "R1", "R20", "K15", "МАСШТАБИРОВАТЬ", "КОРРЕКТИРОВАТЬ", "ОСТАНОВИТЬ",
    ]
    absent = [x for x in required if x not in text]
    if absent:
        raise RuntimeError(f"Evidence anchors absent from appendix PDF: {absent}")

    prohibited_claims = [
        "Методика ЕГ внедрена в сети «Перекрёсток»",
        "пилот проведён",
        "143 подтверждённых наруш",
        "99,33% решённых проблем",
    ]
    bad = [x for x in prohibited_claims if x.lower() in text.lower()]
    if bad:
        raise RuntimeError(f"Prohibited unsupported claims found: {bad}")

    report = [
        "# T7.1 appendices A–T audit",
        "",
        "Status: **PASS**",
        "",
        f"- PDF pages: **{pages}**;",
        f"- appendices present: **{len(LETTERS)}/{len(LETTERS)}**;",
        "- key T3–T5 evidence anchors: **PASS**;",
        "- unsupported pilot/implementation claims: **none**;",
        "- packet is separate from the 60–80 page main thesis body.",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
