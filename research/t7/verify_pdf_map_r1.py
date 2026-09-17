#!/usr/bin/env python3
from pathlib import Path
import re

from docx import Document
from pypdf import PdfReader

from finalize_toc_r1 import ENTRIES, body_page_map

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "research/t7/build/WKR_Methodika_EG_T7_R1.docx"
PDF = ROOT / "research/t7/build/pdf/WKR_Methodika_EG_T7_R1.pdf"
MAP_FILE = ROOT / "research/t7/build/R1_PAGE_MAP.txt"


def load_expected() -> dict[str, int]:
    result = {}
    for line in MAP_FILE.read_text(encoding="utf-8").splitlines():
        prefix, page = line.rsplit("\t", 1)
        result[prefix] = int(page)
    return result


def toc_map_from_docx() -> dict[str, int]:
    doc = Document(DOCX)
    inside = False
    result: dict[str, int] = {}
    prefixes = [prefix for prefix, _ in ENTRIES]
    for p in doc.paragraphs:
        text = (p.text or "").strip()
        if text == "СОДЕРЖАНИЕ":
            inside = True
            continue
        if inside and text == "Введение":
            break
        if not inside:
            continue
        for run in p.runs:
            run_text = (run.text or "").strip()
            for prefix in prefixes:
                if run_text.startswith(prefix):
                    m = re.search(r"(\d+)\s*$", run_text)
                    if m:
                        result[prefix] = int(m.group(1))
                    break
    return result


def main() -> None:
    expected = load_expected()
    actual = body_page_map(PDF)
    toc = toc_map_from_docx()
    pages = len(PdfReader(PDF).pages)

    if not 60 <= pages <= 80:
        raise RuntimeError(f"A4 page count outside 60–80: {pages}")
    if actual != expected:
        raise RuntimeError(f"body page map changed after TOC patch: actual={actual}, expected={expected}")
    if toc != expected:
        raise RuntimeError(f"DOCX TOC does not match rendered body map: toc={toc}, expected={expected}")

    print(f"T7.1-R1 A4 page count PASS: {pages}")
    print("T7.1-R1 rendered body map = DOCX contents map: PASS")
    for prefix, _ in ENTRIES:
        print(f"{prefix} -> {actual[prefix]}")


if __name__ == "__main__":
    main()
