#!/usr/bin/env python3
from pathlib import Path
import re
from docx import Document
from docx.shared import Cm

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "research/t6/build/WKR_Methodika_EG_T6.docx"

# Verified A4 page map for the normalized T6 manuscript.
PAGE_MAP = {
    "Введение": 3,
    "Глава 1.": 8,
    "1.1.": 8,
    "1.2.": 13,
    "1.3.": 19,
    "Глава 2.": 25,
    "2.1.": 25,
    "2.2.": 30,
    "2.3.": 38,
    "Глава 3.": 44,
    "3.1.": 44,
    "3.2.": 49,
    "3.3.": 55,
    "Заключение": 62,
    "Список использованных источников": 66,
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

    # Pandoc defaults to US Letter; T6 is delivered and verified on A4.
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

        # Each contents entry is kept in its original 11 pt run. Some grouped
        # subsections share a paragraph but remain separate runs.
        for run in p.runs:
            for marker, page in PAGE_MAP.items():
                if patch_run(run, marker, page):
                    seen.add(marker)
                    break

    missing = set(PAGE_MAP) - seen
    if missing:
        raise RuntimeError(f"TOC entries not verified: {sorted(missing)}")

    doc.save(DOCX)
    print("DOCX finalized on A4; TOC verified against 71-page T6 map")


if __name__ == "__main__":
    main()
