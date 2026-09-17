#!/usr/bin/env python3
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "research/t7/build_appendices/WKR_Methodika_EG_Appendices_A_T.docx"


def main() -> None:
    doc = Document(DOCX)
    changed = 0
    for paragraph in doc.paragraphs:
        if (paragraph.text or "").strip().startswith("Таблица "):
            paragraph.paragraph_format.keep_with_next = True
            changed += 1
    if changed == 0:
        raise RuntimeError("No table captions found")
    doc.save(DOCX)
    print(f"table captions finalized: {changed}")


if __name__ == "__main__":
    main()
