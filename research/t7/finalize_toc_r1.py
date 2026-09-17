#!/usr/bin/env python3
from pathlib import Path
import re

from docx import Document
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "research/t7/build/WKR_Methodika_EG_T7_R1.docx"
PROVISIONAL_PDF = ROOT / "research/t7/build/pdf_provisional/WKR_Methodika_EG_T7_R1.pdf"
MAP_FILE = ROOT / "research/t7/build/R1_PAGE_MAP.txt"

ENTRIES = [
    ("Введение", "Введение"),
    ("Глава 1.", "Глава 1. Теоретические основы организации работы с отзывами клиентов в системе PR-коммуникаций"),
    ("1.1.", "1.1. Клиентский отзыв как форма обратной связи и PR-коммуникации в цифровой среде"),
    ("1.2.", "1.2. Клиентский опыт, цифровая репутация и управленческое значение отзывов"),
    ("1.3.", "1.3. Подходы к классификации и анализу клиентских отзывов"),
    ("Глава 2.", "Глава 2. Анализ публичного контура клиентских отзывов торговой сети «Перекрёсток»"),
    ("2.1.", "2.1. Характеристика объекта исследования, информационных каналов и методики формирования корпуса"),
    ("2.2.", "2.2. Результаты контент-анализа и количественной группировки клиентских отзывов"),
    ("2.3.", "2.3. Выявленные проблемы и требования к совершенствованию процесса работы с отзывами"),
    ("Глава 3.", "Глава 3. Разработка организационно-методической программы «Методика ЕГ» и плана её внедрения"),
    ("3.1.", "3.1. Обоснование концепции и целевая процессная модель TO-BE"),
    ("3.2.", "3.2. Классификатор, роли, регламент, архитектура и проектные представления «Методики ЕГ»"),
    ("3.3.", "3.3. KPI, план внедрения, риски и методика будущей оценки эффективности"),
    ("Заключение", "Заключение"),
    ("Список использованных источников", "Список использованных источников"),
]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def body_page_map(pdf: Path) -> dict[str, int]:
    reader = PdfReader(pdf)
    texts = [norm(page.extract_text() or "") for page in reader.pages]
    result: dict[str, int] = {}
    for prefix, full in ENTRIES:
        found = None
        for i, text in enumerate(texts[2:], start=3):
            if full in text:
                found = i
                break
        if found is None:
            raise RuntimeError(f"Body heading not found in provisional PDF: {full}")
        result[prefix] = found
    return result


def patch_run(run, prefix: str, page: int) -> bool:
    text = run.text or ""
    if not text.strip().startswith(prefix):
        return False
    updated, count = re.subn(r"\s+\d+\s*$", f" {page}", text)
    if count:
        run.text = updated
        return True
    return re.search(rf"\s{page}\s*$", text) is not None


def main() -> None:
    if not PROVISIONAL_PDF.exists():
        raise RuntimeError(f"Provisional A4 PDF not found: {PROVISIONAL_PDF}")
    page_map = body_page_map(PROVISIONAL_PDF)

    doc = Document(DOCX)
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
            for prefix, _full in ENTRIES:
                if patch_run(run, prefix, page_map[prefix]):
                    seen.add(prefix)
                    break

    missing = set(page_map) - seen
    if missing:
        raise RuntimeError(f"TOC entries not patched: {sorted(missing)}")

    doc.save(DOCX)
    MAP_FILE.write_text(
        "\n".join(f"{prefix}\t{page_map[prefix]}" for prefix, _ in ENTRIES) + "\n",
        encoding="utf-8",
    )
    print("T7.1-R1 TOC finalized from provisional A4 render")
    for prefix, _ in ENTRIES:
        print(f"{prefix} -> {page_map[prefix]}")


if __name__ == "__main__":
    main()
