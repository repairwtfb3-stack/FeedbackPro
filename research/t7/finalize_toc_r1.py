#!/usr/bin/env python3
from pathlib import Path
import re

from docx import Document
from docx.shared import Cm

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "research/t7/build/WKR_Methodika_EG_T7_R1.docx"

# Verified from the rendered 78-page R1 PDF on 17.09.2026.
PAGE_MAP = {
    "Введение": 3,
    "Глава 1.": 9,
    "1.1.": 9,
    "1.2.": 14,
    "1.3.": 20,
    "Глава 2.": 27,
    "2.1.": 27,
    "2.2.": 32,
    "2.3.": 41,
    "Глава 3.": 48,
    "3.1.": 48,
    "3.2.": 54,
    "3.3.": 61,
    "Заключение": 68,
    "Список использованных источников": 73,
}


def patch_run(run, marker: str, page: int) -> bool:
    text = run.text or ""
    stripped = text.strip()
    if not stripped.startswith(marker):
        return False
    updated, count = re.subn(r"\s+\d+\s*$", f" {page}", text)
    if count:
        run.text = updated
    return count > 0 or re.search(rf"\s{page}\s*$", text) is not None


def main() -> None:
    doc = Document(DOCX)
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)

    inside = False
    seen = set()
    for p in doc.paragraphs:
        stripped = (p.text or "").strip()
        if stripped == "СОДЕРЖАНИЕ":
            inside = True
            continue
        if inside and stripped == "Введение":
            break
        if not inside:
            continue
        for run in p.runs:
            for marker, page in PAGE_MAP.items():
                if patch_run(run, marker, page):
                    seen.add(marker)
                    break

    missing = set(PAGE_MAP) - seen
    if missing:
        raise RuntimeError(f"TOC entries not verified: {sorted(missing)}")

    doc.save(DOCX)
    print("T7.1-R1 TOC finalized against verified 78-page map")


if __name__ == "__main__":
    main()
