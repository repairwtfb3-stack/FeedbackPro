#!/usr/bin/env python3
from pathlib import Path
import re
from docx import Document

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "research/t6/build/WKR_Methodika_EG_T6.docx"


def main() -> None:
    doc = Document(DOCX)
    inside = False
    found_33 = found_conclusion = found_refs = False

    for p in doc.paragraphs:
        text = p.text or ""
        stripped = text.strip()
        if stripped == "СОДЕРЖАНИЕ":
            inside = True
            continue
        if inside and stripped == "Введение":
            break
        if not inside or not text:
            continue

        new_text = text
        # Pandoc groups 3.1/3.2/3.3 into one DOCX paragraph separated by line
        # breaks, so patch the 3.3 line inside the paragraph rather than relying
        # on paragraph prefix matching.
        if "3.3. KPI, план внедрения" in new_text:
            new_text, n = re.subn(
                r"(3\.3\. KPI, план внедрения, риски и методика будущей оценки эффективности\s+\.{3,}\s*)61(\s*$)",
                r"\g<1>59\2",
                new_text,
                flags=re.S,
            )
            found_33 = n > 0 or "3.3. KPI, план внедрения" in new_text and re.search(r"3\.3\..*?59\s*$", new_text, re.S) is not None

        if stripped.startswith("Заключение"):
            new_text, n = re.subn(r"\s+68\s*$", " 67", new_text)
            found_conclusion = n > 0 or re.search(r"\s67\s*$", new_text) is not None

        if stripped.startswith("Список использованных источников"):
            new_text, n = re.subn(r"\s+76\s*$", " 75", new_text)
            found_refs = n > 0 or re.search(r"\s75\s*$", new_text) is not None

        if new_text != text:
            p.text = new_text

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
    print("TOC finalized: 3.3=59; Заключение=67; Источники=75")


if __name__ == "__main__":
    main()
