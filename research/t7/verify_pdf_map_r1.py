#!/usr/bin/env python3
from pathlib import Path
import re

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "research/t7/build/pdf/WKR_Methodika_EG_T7_R1.pdf"

EXPECTED = {
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


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def first_page(texts: list[str], marker: str) -> int | None:
    for i, text in enumerate(texts, start=1):
        if i == 2:  # contents page
            continue
        if marker in text:
            return i
    return None


def main() -> None:
    reader = PdfReader(PDF)
    texts = [norm(page.extract_text() or "") for page in reader.pages]
    if len(texts) != 78:
        raise RuntimeError(f"R1 page count changed: {len(texts)} != 78")

    actual = {}
    for marker in EXPECTED:
        page = first_page(texts, marker)
        actual[marker] = page
        if page != EXPECTED[marker]:
            raise RuntimeError(f"page map mismatch for {marker!r}: {page} != {EXPECTED[marker]}")

    print("T7.1-R1 rendered page map PASS")
    for marker, page in actual.items():
        print(f"{marker} -> {page}")


if __name__ == "__main__":
    main()
