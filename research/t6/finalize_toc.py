#!/usr/bin/env python3
from pathlib import Path
import re
from docx import Document
from docx.shared import Cm

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "research/t6/build/WKR_Methodika_EG_T6.docx"


def patch_run(run, old_page: int, new_page: int, marker: str) -> bool:
    text = run.text or ""
    if marker not in text:
        return False
    updated, count = re.subn(rf"\s+{old_page}\s*$", f" {new_page}", text)
    if count:
        run.text = updated
        return True
    return re.search(rf"\s{new_page}\s*$", text) is not None


def main() -> None:
    doc = Document(DOCX)

    # Pandoc defaults to US Letter. T6 is verified and delivered on A4,
    # therefore page size is fixed explicitly before the verification render.
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)

    inside = False
    found_33 = found_conclusion = found_refs = False

    for p in doc.paragraphs:
        stripped = (p.text or "").strip()
        if stripped == "СОДЕРЖАНИЕ":
            inside = True
            continue
        if inside and stripped == "Введение":
            break
        if not inside:
            continue

        # Preserve existing 11 pt TOC run formatting and line breaks.
        # These values are an interim page map; the final T6 pass replaces
        # them with the verified A4 map after section-length normalization.
        for run in p.runs:
            found_33 = patch_run(run, 61, 59, "3.3. KPI, план внедрения") or found_33
            found_conclusion = patch_run(run, 68, 67, "Заключение") or found_conclusion
            found_refs = patch_run(run, 76, 75, "Список использованных источников") or found_refs

    missing = []
    if not found_33:
        missing.append("3.3 -> 59")
    if not found_conclusion:
        missing.append("Заключение -> 67")
    if not found_refs:
        missing.append("Источники -> 75")
    if missing:
        raise RuntimeError(f"Required TOC patches not verified: {missing}")

    doc.save(DOCX)
    print("DOCX finalized on A4; interim TOC page patches preserved")


if __name__ == "__main__":
    main()
