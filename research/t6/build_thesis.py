#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.shared import Cm, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "t6" / "build"
GEN = OUT / "generated"
OUT.mkdir(parents=True, exist_ok=True)
GEN.mkdir(parents=True, exist_ok=True)

PARTS = [
    ROOT / "docs/t6/T6_INTRODUCTION.md",
    ROOT / "docs/t6/T6_CHAPTER_1.md",
    ROOT / "docs/t6/T6_CHAPTER_2.md",
    ROOT / "docs/t6/T6_CHAPTER_3.md",
    ROOT / "docs/t6/T6_CONCLUSION.md",
    ROOT / "docs/t6/T6_REFERENCES.md",
]


def dot(name: str, body: str) -> Path:
    src = GEN / f"{name}.dot"
    png = GEN / f"{name}.png"
    src.write_text("digraph G {\nrankdir=LR; graph [bgcolor=white, pad=0.2, nodesep=0.45, ranksep=0.6]; node [shape=box, style=\"rounded\", fontname=\"DejaVu Sans\", fontsize=10, margin=0.12]; edge [fontname=\"DejaVu Sans\", fontsize=9];\n" + body + "\n}\n", encoding="utf-8")
    subprocess.run(["dot", "-Tpng", "-Gdpi=160", str(src), "-o", str(png)], check=True)
    return png


def make_diagrams() -> list[Path]:
    diagrams = []
    diagrams.append(dot("tobe", '''
A[label="Получение"]; B[label="Регистрация + provenance"]; C[label="Валидация / dedup / обезличивание"]; D[label="Классификация\nтональность + аспекты + C1-C4"]; E[label="C3/C4?", shape=diamond]; F[label="Expert verification"]; G[label="Стандартная маршрутизация"]; H[label="Эскалация"]; I[label="Профильная роль"]; J[label="Решение"]; K[label="Ответ клиенту"]; L[label="Внутреннее мероприятие"]; M[label="Контроль"]; N[label="Outcome"]; O[label="Результат подтверждён?", shape=diamond]; P[label="Закрытие + знания"]; Q[label="Аналитика / KPI"];
A->B->C->D->E; E->F[label=" да"]; E->G[label=" нет"]; F->H->J; G->I->J; J->K->M; J->L->M; M->N->O; O->J[label=" нет"]; O->P[label=" да"]; P->Q;
'''))
    diagrams.append(dot("decision_tree", '''
A[label="Новый отзыв"]; B[label="Регистрация"]; C[label="Аспекты + тональность"]; D[label="Critical trigger?", shape=diamond]; E[label="Предварительный C3/C4"]; F[label="Expert verification"]; G[label="Высокий риск подтверждён?", shape=diamond]; H[label="Эскалация RM/LC"]; I[label="Изменить C-level\nс основанием"]; J[label="Нужно профильное действие?", shape=diamond]; K[label="C2/C3 по контексту"]; L[label="C1"]; M[label="Решение"]; N[label="Ответ и/или мероприятие"]; O[label="Контроль"]; P[label="Outcome подтверждён?", shape=diamond]; Q[label="Закрытие"];
A->B->C->D; D->E[label=" да"]; E->F->G; G->H[label=" да"]; G->I[label=" нет"]; D->J[label=" нет"]; J->K[label=" да"]; J->L[label=" нет"]; H->M; I->M; K->M; L->M; M->N->O->P; P->M[label=" нет"]; P->Q[label=" да"];
'''))
    diagrams.append(dot("architecture", '''
A[label="Каналы обратной связи"]; B[label="Получение и регистрация"]; C[label="Качество данных"]; D[label="Классификация и анализ"]; E[label="Решение и маршрутизация"]; F[label="Коммуникация"]; G[label="Мероприятия"]; H[label="Контроль outcome"]; I[label="Аналитика / KPI"]; J[label="Knowledge base / улучшения"];
A->B->C->D->E; E->F->H; E->G->H; H->I->J->D;
'''))
    diagrams.append(dot("logical_model", '''
S[label="SOURCE"]; R[label="REVIEW_CASE"]; C[label="CLASSIFICATION"]; A[label="ASPECT"]; D[label="DECISION"]; RESP[label="RESPONSE"]; ACT[label="ACTION"]; CTRL[label="CONTROL_EVENT"]; O[label="OUTCOME"]; ROLE[label="ROLE"]; AUD[label="AUDIT_EVENT"];
S->R; R->C; C->A[label="M:N"]; R->D; D->RESP; D->ACT; ACT->CTRL; RESP->CTRL; R->O; ROLE->D; ROLE->ACT; R->AUD;
'''))
    diagrams.append(dot("implementation", '''
E0[label="E0 Решение о пилоте"]; E1[label="E1 Подготовка"]; E2[label="E2 Адаптация"]; E3[label="E3 Обучение / dry-run"]; E4[label="E4 BEFORE"]; E5[label="E5 Пилот"]; E6[label="E6 AFTER"]; E7[label="E7 Оценка"]; D[label="Решение", shape=diamond]; E8[label="E8 Масштабирование"]; X[label="Завершение / разбор причин"];
E0->E1->E2->E3->E4->E5->E6->E7->D; D->E8[label=" масштабировать"]; D->E2[label=" корректировать"]; D->X[label=" остановить"];
'''))
    return diagrams


def build_markdown(diagrams: list[Path]) -> Path:
    title = '''# ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА\n\n**Тема:** «создание программы по работе с отзывами клиентов анализ, моделирование, внедрение»\n\n**Рабочее название авторской разработки:** «Методика ЕГ»\n\n*Рабочая сборка T6. Реквизиты образовательной организации, обучающегося и руководителя заполняются по утверждённому титульному шаблону на этапе T7.*\n\n\\newpage\n\n'''
    text = title
    d_idx = 0
    for p in PARTS:
        s = p.read_text(encoding="utf-8-sig")
        # Make repository-relative image paths valid from root build context.
        s = s.replace("../../research/", "research/")
        # Replace Mermaid source with deterministic rendered diagrams.
        def repl(_m):
            nonlocal d_idx
            if d_idx >= len(diagrams):
                return ""
            img = diagrams[d_idx]
            d_idx += 1
            captions = [
                "Целевая процессная модель TO-BE «Методики ЕГ»",
                "Дерево решений и эскалации",
                "Функциональная архитектура «Методики ЕГ»",
                "Логическая модель информационных сущностей",
                "Этапы внедрения E0-E8",
            ]
            return f"\n![{captions[d_idx-1]}]({img.relative_to(ROOT).as_posix()})\n"
        s = re.sub(r"```mermaid\s*.*?```", repl, s, flags=re.S)
        text += s.rstrip() + "\n\n"
    combined = OUT / "T6_COMBINED.md"
    combined.write_text(text, encoding="utf-8")
    return combined


def set_run_font(run, name="Times New Roman", size=Pt(14)):
    run.font.name = name
    run.font.size = size
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.rFonts
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        rFonts.set(qn(f"w:{attr}"), name)


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = " PAGE "
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    set_run_font(run, size=Pt(12))


def postprocess(docx_path: Path):
    doc = Document(docx_path)
    for sec in doc.sections:
        sec.top_margin = Cm(2.0)
        sec.bottom_margin = Cm(2.0)
        sec.left_margin = Cm(3.0)
        sec.right_margin = Cm(1.5)
        sec.header_distance = Cm(1.0)
        sec.footer_distance = Cm(1.0)
        # Page number in footer.
        if not sec.footer.paragraphs:
            sec.footer.add_paragraph()
        fp = sec.footer.paragraphs[0]
        if not fp.text:
            add_page_number(fp)

    # Base styles.
    for stylename in ["Normal", "Body Text", "First Paragraph"]:
        if stylename in doc.styles:
            st = doc.styles[stylename]
            st.font.name = "Times New Roman"
            st.font.size = Pt(14)
            st.paragraph_format.line_spacing = 1.5
            st.paragraph_format.space_after = Pt(0)
            st.paragraph_format.first_line_indent = Cm(1.25)
    for stylename, size in [("Title", 16), ("Heading 1", 14), ("Heading 2", 14), ("Heading 3", 14)]:
        if stylename in doc.styles:
            st = doc.styles[stylename]
            st.font.name = "Times New Roman"
            st.font.size = Pt(size)
            st.font.bold = True
            st.paragraph_format.first_line_indent = Cm(0)
            st.paragraph_format.space_before = Pt(12)
            st.paragraph_format.space_after = Pt(6)
            st.paragraph_format.keep_with_next = True

    for p in doc.paragraphs:
        txt = p.text.strip()
        style = p.style.name if p.style else ""
        is_heading = style.startswith("Heading") or style == "Title"
        is_caption = txt.startswith("Рисунок ") or txt.startswith("Таблица ") or txt.startswith("Источник:")
        if is_heading:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if style in ("Heading 1", "Title") else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            if style == "Heading 1" and txt not in ("ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА",):
                p.paragraph_format.page_break_before = True
        elif txt:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if txt.startswith("!") else WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.first_line_indent = Cm(0) if is_caption else Cm(1.25)
        for r in p.runs:
            set_run_font(r, size=Pt(14) if not is_caption else Pt(12))

    # Tables: fit academically and avoid oversized font.
    for table in doc.tables:
        table.style = "Table Grid"
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.first_line_indent = Cm(0)
                    p.paragraph_format.line_spacing = 1.0
                    p.paragraph_format.space_after = Pt(0)
                    for r in p.runs:
                        set_run_font(r, size=Pt(10))
        # Repeat header row.
        if table.rows:
            trPr = table.rows[0]._tr.get_or_add_trPr()
            tblHeader = OxmlElement("w:tblHeader")
            tblHeader.set(qn("w:val"), "true")
            trPr.append(tblHeader)

    # Images centered.
    for p in doc.paragraphs:
        if p._p.xpath('.//w:drawing'):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Cm(0)

    # Document properties.
    doc.core_properties.title = "ВКР — Методика ЕГ — T6"
    doc.core_properties.subject = "Создание программы по работе с отзывами клиентов анализ, моделирование, внедрение"
    doc.core_properties.author = ""
    doc.core_properties.keywords = "ВКР; отзывы клиентов; PR; Методика ЕГ"

    doc.save(docx_path)


def main():
    diagrams = make_diagrams()
    md = build_markdown(diagrams)
    raw = OUT / "WKR_Methodika_EG_T6_raw.docx"
    final = OUT / "WKR_Methodika_EG_T6.docx"
    cmd = [
        "pandoc", str(md),
        "--from=markdown+raw_tex",
        "--to=docx",
        "--toc",
        "--toc-depth=2",
        "--resource-path", str(ROOT),
        "-o", str(raw),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)
    raw.replace(final)
    postprocess(final)
    print(final)

if __name__ == "__main__":
    main()
