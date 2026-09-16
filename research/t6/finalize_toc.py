#!/usr/bin/env python3
from pathlib import Path
import re
from docx import Document

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "research/t6/build/WKR_Methodika_EG_T6.docx"

# Only these entries differ from the verified 80-page render produced by the
# canonical builder. Other TOC entries already match and may wrap across DOCX
# paragraphs, so they are deliberately left untouched.
PATCHES = {
    "3.3.": 59,
    "Заключение": 67,
    "Список использованных источников": 75,
}


def replace_trailing_page(text: str, page: int) -> str:
    updated, count = re.subn(r"\s+\d+\s*$", f" {page}", text)
    return updated if count else text


def main() -> None:
    doc = Document(DOCX)
    inside = False
    seen = set()
    changed = 0

    for p in doc.paragraphs:
        text = (p.text or "").strip()
        if text == "СОДЕРЖАНИЕ":
            inside = True
            continue
        if inside and text == "Введение" and not re.search(r"\d+\s*$", text):
            break
        if not inside or not text:
            continue

        for prefix, page in PATCHES.items():
            if text.startswith(prefix):
                new_text = replace_trailing_page(text, page)
                if new_text != text:
                    p.text = new_text
                    changed += 1
                seen.add(prefix)
                break

    missing = set(PATCHES) - seen
    if missing:
        raise RuntimeError(f"Required TOC patches not found: {sorted(missing)}")

    doc.save(DOCX)
    print(f"TOC finalized: {len(seen)} verified entries, {changed} values changed")


if __name__ == "__main__":
    main()
