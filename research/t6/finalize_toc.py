#!/usr/bin/env python3
from pathlib import Path
import re
from docx import Document

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "research/t6/build/WKR_Methodika_EG_T6.docx"

PAGE_MAP = {
    "Введение": 3,
    "Глава 1.": 11,
    "1.1.": 11,
    "1.2.": 16,
    "1.3.": 22,
    "Глава 2.": 29,
    "2.1.": 29,
    "2.2.": 34,
    "2.3.": 42,
    "Глава 3.": 48,
    "3.1.": 48,
    "3.2.": 53,
    "3.3.": 59,
    "Заключение": 67,
    "Список использованных источников": 75,
}


def replace_trailing_page(text: str, page: int) -> str:
    return re.sub(r"\s+\d+\s*$", f" {page}", text)


def main() -> None:
    doc = Document(DOCX)
    inside = False
    changed = 0
    seen = set()
    for p in doc.paragraphs:
        text = (p.text or "").strip()
        if text == "СОДЕРЖАНИЕ":
            inside = True
            continue
        if inside and text == "Введение" and not re.search(r"\d+\s*$", text):
            # Actual chapter heading reached; stop after TOC section.
            inside = False
        if not inside or not text:
            continue
        for prefix, page in PAGE_MAP.items():
            if text.startswith(prefix):
                new_text = replace_trailing_page(text, page)
                if new_text != text:
                    # Contents lines are plain runs; replacing text is safe here.
                    p.text = new_text
                    changed += 1
                seen.add(prefix)
                break
    missing = set(PAGE_MAP) - seen
    if missing:
        raise RuntimeError(f"TOC entries not found: {sorted(missing)}")
    doc.save(DOCX)
    print(f"TOC finalized: {len(seen)} entries, {changed} page values changed")


if __name__ == "__main__":
    main()
