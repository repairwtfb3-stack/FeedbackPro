#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor
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

TOC = [
    ("Введение", 3),
    ("Глава 1. Теоретические основы организации работы с отзывами клиентов в системе PR-коммуникаций", 11),
    ("1.1. Клиентский отзыв как форма обратной связи и PR-коммуникации в цифровой среде", 11),
    ("1.2. Клиентский опыт, цифровая репутация и управленческое значение отзывов", 16),
    ("1.3. Подходы к классификации и анализу клиентских отзывов", 22),
    ("Глава 2. Анализ публичного контура клиентских отзывов торговой сети «Перекрёсток»", 29),
    ("2.1. Характеристика объекта исследования, информационных каналов и методики формирования корпуса", 29),
    ("2.2. Результаты контент-анализа и количественной группировки клиентских отзывов", 34),
    ("2.3. Выявленные проблемы и требования к совершенствованию процесса работы с отзывами", 42),
    ("Глава 3. Разработка организационно-методической программы «Методика ЕГ» и плана её внедрения", 48),
    ("3.1. Обоснование концепции и целевая процессная модель TO-BE", 48),
    ("3.2. Классификатор, роли, регламент, архитектура и проектные представления «Методики ЕГ»", 53),
    ("3.3. KPI, план внедрения, риски и методика будущей оценки эффективности", 61),
    ("Заключение", 68),
    ("Список использованных источников", 76),
]


def dot(name: str, body: str, *, rankdir: str = "TB", nodesep: float = 0.30, ranksep: float = 0.42) -> Path:
    src = GEN / f"{name}.dot"
    png = GEN / f"{name}.png"
    src.write_text(
        "digraph G {\n"
        f"rankdir={rankdir}; "
        f"graph [bgcolor=white,pad=0.12,nodesep={nodesep},ranksep={ranksep},splines=polyline]; "
        'node [shape=box,style="rounded",fontname="DejaVu Sans",fontsize=13,margin="0.16,0.10"]; '
        'edge [fontname="DejaVu Sans",fontsize=11,arrowsize=0.75];\n'
        + body
        + "\n}\n",
        encoding="utf-8",
    )
    subprocess.run(["dot", "-Tpng", "-Gdpi=180", str(src), "-o", str(png)], check=True)
    return png


def make_diagrams() -> list[Path]:
    return [
        dot(
            "tobe",
            '''
A[label="Получение отзыва"]; B[label="Регистрация + provenance"]; C[label="Валидация / dedup / обезличивание"]; D[label="Классификация\\nтональность + аспекты + C1-C4"]; E[label="C3/C4 или critical trigger?",shape=diamond];
F[label="Экспертная проверка"]; G[label="Стандартная маршрутизация"]; H[label="Эскалация"]; I[label="Назначение профильной роли"]; J[label="Решение"]; K[label="Ответ клиенту"]; L[label="Внутреннее мероприятие"]; M[label="Контроль"]; N[label="Оценка outcome"]; O[label="Результат подтверждён?",shape=diamond]; P[label="Закрытие + знания"]; Q[label="Аналитика / KPI"];
A->B->C->D->E; E->F[label="да"]; E->G[label="нет"]; {rank=same;F;G;} F->H; G->I; {rank=same;H;I;} H->J; I->J; J->K; J->L; {rank=same;K;L;} K->M; L->M; M->N->O; O->J[label="нет"]; O->P[label="да"]; P->Q;
''',
            rankdir="TB", nodesep=0.28, ranksep=0.34,
        ),
        dot(
            "decision_tree",
            '''
A[label="Новый отзыв"]; B[label="Регистрация"]; C[label="Аспекты + тональность"]; D[label="Critical trigger?",shape=diamond]; E[label="Предварительный C3/C4"]; F[label="Expert verification"]; G[label="Высокий риск подтверждён?",shape=diamond]; H[label="Эскалация RM / Legal"]; I[label="Изменить C-level\\nс основанием"]; J[label="Нужно профильное действие?",shape=diamond]; K[label="C2/C3 по контексту"]; L[label="C1"]; M[label="Решение"]; N[label="Ответ и/или мероприятие"]; O[label="Контроль"]; P[label="Outcome подтверждён?",shape=diamond]; Q[label="Закрытие"];
A->B->C->D; D->E[label="да"]; E->F->G; G->H[label="да"]; G->I[label="нет"]; D->J[label="нет"]; J->K[label="да"]; J->L[label="нет"]; {rank=same;H;I;K;L;} H->M; I->M; K->M; L->M; M->N->O->P; P->M[label="нет"]; P->Q[label="да"];
''',
            rankdir="TB", nodesep=0.22, ranksep=0.34,
        ),
        dot(
            "architecture",
            '''
A[label="Каналы обратной связи"]; B[label="Получение и регистрация"]; C[label="Качество данных\\nprovenance / dedup / privacy"]; D[label="Классификация и анализ"]; E[label="Решение и маршрутизация"]; F[label="Коммуникация\\nRESPONSE"]; G[label="Внутренние мероприятия\\nACTION"]; H[label="Контроль результата\\nOUTCOME"]; I[label="Аналитика / KPI"]; J[label="Knowledge base / улучшения"];
A->B->C->D->E; E->F; E->G; {rank=same;F;G;} F->H; G->H; H->I->J; J->D[label="обновление правил"];
''',
            rankdir="TB", nodesep=0.35, ranksep=0.42,
        ),
        dot(
            "logical_model",
            '''
S[label="SOURCE"]; R[label="REVIEW_CASE"]; C[label="CLASSIFICATION"]; A[label="ASPECT"]; D[label="DECISION"]; RESP[label="RESPONSE"]; ACT[label="ACTION"]; CTRL[label="CONTROL_EVENT"]; O[label="OUTCOME"]; ROLE[label="ROLE"]; AUD[label="AUDIT_EVENT"];
S->R; R->C; C->A[label="M:N"]; R->D; D->RESP; D->ACT; {rank=same;RESP;ACT;} RESP->CTRL; ACT->CTRL; CTRL->O; R->O; ROLE->D; ROLE->ACT; R->AUD;
''',
            rankdir="TB", nodesep=0.32, ranksep=0.38,
        ),
        dot(
            "implementation",
            '''
E0[label="E0. Решение о пилоте"]; E1[label="E1. Подготовка"]; E2[label="E2. Адаптация методики"]; E3[label="E3. Обучение / dry-run"]; E4[label="E4. BEFORE baseline"]; E5[label="E5. Пилот"]; E6[label="E6. AFTER measurement"]; E7[label="E7. Оценка"]; D[label="Decision gate",shape=diamond]; E8[label="E8. Масштабирование"]; C[label="Корректировка\\nновая версия + новый пилот"]; X[label="Остановить / разбор причин"];
E0->E1->E2->E3->E4->E5->E6->E7->D; D->E8[label="масштабировать"]; D->C[label="корректировать"]; D->X[label="остановить"]; {rank=same;E8;C;X;} C->E2[label="новый цикл"];
''',
            rankdir="TB", nodesep=0.30, ranksep=0.36,
        ),
    ]


def toc_markdown() -> str:
    lines = ["# СОДЕРЖАНИЕ", ""]
    for title, page in TOC:
        level = 0 if title.startswith(("Введение", "Глава", "Заключение", "Список")) else 1
        prefix = "    " if level else ""
        dots = "." * max(6, 74 - min(len(title), 64))
        lines.append(f"{prefix}{title} {dots} {page}")
        lines.append("")
    return "\n".join(lines) + "\n"


def build_markdown(diagrams: list[Path]) -> Path:
    text = '''# ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА\n\n**Тема:** «создание программы по работе с отзывами клиентов анализ, моделирование, внедрение»\n\n**Рабочее название авторской разработки:** «Методика ЕГ»\n\n*Рабочая сборка T6. Реквизиты образовательной организации, обучающегося и руководителя заполняются по утверждённому титульному шаблону на этапе T7.*\n\n'''
    text += toc_markdown() + "\n"
    captions = [
        "Рисунок 3.1 — Целевая процессная модель TO-BE «Методики ЕГ»",
        "Рисунок 3.2 — Дерево решений и эскалации",
        "Рисунок 3.3 — Функциональная архитектура «Методики ЕГ»",
        "Рисунок 3.4 — Логическая модель информационных сущностей",
        "Рисунок 3.5 — Этапы внедрения E0-E8",
    ]
    widths = [12.4, 13.2, 13.4, 13.6, 13.2]
    d_idx = 0
    for path in PARTS:
        s = path.read_text(encoding="utf-8-sig").replace("../../research/", "research/")

        def repl(_m):
            nonlocal d_idx
            if d_idx >= len(diagrams):
                return ""
            img = diagrams[d_idx].relative_to(ROOT).as_posix()
            cap = captions[d_idx]
            width = widths[d_idx]
            d_idx += 1
            return f'\n![{cap}]({img}){{ width={width}cm }}\n'

        s = re.sub(r"```mermaid\s*.*?```", repl, s, flags=re.S)
        text += s.rstrip() + "\n\n"
    combined = OUT / "T6_COMBINED.md"
    combined.write_text(text, encoding="utf-8")
    return combined


def set_run_font(run, size=Pt(14), bold=None):
    run.font.name = "Times New Roman"
    run.font.size = size
    run.font.color.rgb = RGBColor(0, 0, 0)
    if bold is not None:
        run.bold = bold
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{attr}"), "Times New Roman")


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = " PAGE "
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, end])
    set_run_font(run, Pt(12))


def add_table_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = borders.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}")
            borders.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")


def postprocess(docx_path: Path):
    doc = Document(docx_path)
    for sec in doc.sections:
        sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(2.0)
        sec.left_margin, sec.right_margin = Cm(3.0), Cm(1.5)
        sec.header_distance, sec.footer_distance = Cm(1.0), Cm(1.0)
        sec.different_first_page_header_footer = True
        first_fp = sec.first_page_footer.paragraphs[0] if sec.first_page_footer.paragraphs else sec.first_page_footer.add_paragraph()
        first_fp.clear()
        fp = sec.footer.paragraphs[0] if sec.footer.paragraphs else sec.footer.add_paragraph()
        if not fp.text:
            add_page_number(fp)

    for stylename in ["Normal", "Body Text", "First Paragraph"]:
        if stylename in doc.styles:
            st = doc.styles[stylename]
            st.font.name, st.font.size = "Times New Roman", Pt(14)
            st.font.color.rgb = RGBColor(0, 0, 0)
            st.paragraph_format.line_spacing = 1.5
            st.paragraph_format.space_after = Pt(0)
            st.paragraph_format.first_line_indent = Cm(1.25)
    for stylename, size in [("Title", 16), ("Heading 1", 14), ("Heading 2", 14), ("Heading 3", 14)]:
        if stylename in doc.styles:
            st = doc.styles[stylename]
            st.font.name, st.font.size, st.font.bold = "Times New Roman", Pt(size), True
            st.font.color.rgb = RGBColor(0, 0, 0)
            st.paragraph_format.first_line_indent = Cm(0)
            st.paragraph_format.space_before, st.paragraph_format.space_after = Pt(12), Pt(6)
            st.paragraph_format.keep_with_next = True

    in_contents = False
    for p in doc.paragraphs:
        txt = p.text.strip()
        style = p.style.name if p.style else ""
        heading = style.startswith("Heading") or style == "Title"
        caption = txt.startswith(("Рисунок ", "Таблица ", "Источник:"))

        if txt == "СОДЕРЖАНИЕ":
            in_contents = True
            p.paragraph_format.page_break_before = True
        elif txt == "Введение":
            in_contents = False

        if heading:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if style in ("Heading 1", "Title") else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            if style == "Heading 1" and txt not in ("ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА", "СОДЕРЖАНИЕ"):
                p.paragraph_format.page_break_before = True
        elif txt:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.first_line_indent = Cm(0) if caption else Cm(1.25)

        if in_contents and txt and txt != "СОДЕРЖАНИЕ":
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(1)

        if p._p.xpath('.//w:drawing'):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)

        for r in p.runs:
            if txt == "СОДЕРЖАНИЕ":
                set_run_font(r, Pt(14), bold=True)
            elif in_contents:
                set_run_font(r, Pt(11))
            else:
                set_run_font(r, Pt(12) if caption else Pt(14))

    for table in doc.tables:
        add_table_borders(table)
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.first_line_indent = Cm(0)
                    p.paragraph_format.line_spacing = 1.0
                    p.paragraph_format.space_after = Pt(0)
                    for r in p.runs:
                        set_run_font(r, Pt(10))
        if table.rows:
            tr_pr = table.rows[0]._tr.get_or_add_trPr()
            header = OxmlElement("w:tblHeader"); header.set(qn("w:val"), "true"); tr_pr.append(header)

    doc.core_properties.title = "ВКР — Методика ЕГ — T6"
    doc.core_properties.subject = "Создание программы по работе с отзывами клиентов анализ, моделирование, внедрение"
    doc.core_properties.author = ""
    doc.core_properties.keywords = "ВКР; отзывы клиентов; PR; Методика ЕГ"
    doc.save(docx_path)


def main():
    md = build_markdown(make_diagrams())
    final = OUT / "WKR_Methodika_EG_T6.docx"
    subprocess.run(
        [
            "pandoc", str(md),
            "--from=markdown+link_attributes",
            "--to=docx",
            "--resource-path", str(ROOT),
            "-o", str(final),
        ],
        cwd=ROOT,
        check=True,
    )
    postprocess(final)
    print(final)


if __name__ == "__main__":
    main()
