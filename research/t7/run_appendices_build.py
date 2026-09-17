#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.shared import Pt
from docx.table import Table
from docx.text.paragraph import Paragraph

import build_appendices as ba


def _escape_newlines_inside_quotes(text: str) -> str:
    """Convert literal line breaks inside Graphviz quoted labels to \\n."""
    out: list[str] = []
    in_quote = False
    escaped = False
    for ch in text:
        if ch == '"' and not escaped:
            in_quote = not in_quote
            out.append(ch)
            escaped = False
            continue
        if ch == '\n' and in_quote:
            out.append('\\n')
            escaped = False
            continue
        out.append(ch)
        if ch == '\\' and not escaped:
            escaped = True
        else:
            escaped = False
    return ''.join(out)


def _normalize_inline_node_attrs(text: str) -> str:
    """Rewrite invalid `A[label=..] -> B[label=..]` syntax into valid DOT."""
    node_pat = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(\[[^\]]*\])")
    declared: set[str] = set()
    out: list[str] = []
    for raw_stmt in text.split(';'):
        stmt = raw_stmt.strip()
        if not stmt:
            continue
        if '->' not in stmt:
            out.append(stmt + ';')
            continue
        declarations: list[str] = []
        def repl(match: re.Match[str]) -> str:
            node_id = match.group(1)
            attrs = match.group(2)
            if node_id not in declared:
                declarations.append(f"{node_id}{attrs};")
                declared.add(node_id)
            return node_id
        edge_stmt = node_pat.sub(repl, stmt)
        out.extend(declarations)
        out.append(edge_stmt + ';')
    return '\n'.join(out)


def safe_dot_png(name: str, dot_body: str) -> Path:
    dot_path = ba.GEN / f"{name}.dot"
    png_path = ba.GEN / f"{name}.png"
    body = _escape_newlines_inside_quotes(dot_body)
    body = _normalize_inline_node_attrs(body)
    dot_path.write_text(
        "digraph G {\n"
        "graph [bgcolor=white, pad=0.2, nodesep=0.35, ranksep=0.5];\n"
        "node [shape=box, style=\"rounded\", fontname=\"DejaVu Sans\", fontsize=10];\n"
        "edge [fontname=\"DejaVu Sans\", fontsize=9];\n"
        + body + "\n}\n",
        encoding="utf-8",
    )
    subprocess.run(["dot", "-Tpng", "-Gdpi=180", str(dot_path), "-o", str(png_path)], check=True)
    return png_path


def _body_items(doc: Document):
    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield "p", Paragraph(child, doc)
        elif isinstance(child, CT_Tbl):
            yield "t", Table(child, doc)


def _table_head(table: Table) -> list[str]:
    if not table.rows:
        return []
    return [(c.text or "").strip() for c in table.rows[0].cells]


def _set_table_font(table: Table, size: float) -> None:
    for row in table.rows:
        tr_pr = row._tr.get_or_add_trPr()
        cant_split = tr_pr.find(qn("w:cantSplit"))
        if cant_split is None:
            cant_split = OxmlElement("w:cantSplit")
            tr_pr.append(cant_split)
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                for r in p.runs:
                    r.font.size = Pt(size)


def _insert_page_break_before_table(table: Table) -> None:
    p = OxmlElement("w:p")
    r = OxmlElement("w:r")
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    r.append(br)
    p.append(r)
    table._tbl.addprevious(p)


def _move_note_before_previous_table(doc: Document, prefix: str) -> None:
    items = list(_body_items(doc))
    for idx, (kind, obj) in enumerate(items):
        if kind != "p" or not (obj.text or "").strip().startswith(prefix):
            continue
        for j in range(idx - 1, -1, -1):
            prev_kind, prev_obj = items[j]
            if prev_kind == "t":
                prev_obj._tbl.addprevious(obj._p)
                return
        raise RuntimeError(f"Previous table not found for appendix note: {prefix}")
    raise RuntimeError(f"Appendix note not found: {prefix}")


def _shrink_figure_before_caption(doc: Document, caption_prefix: str, factor: float) -> None:
    items = list(_body_items(doc))
    for idx, (kind, obj) in enumerate(items):
        if kind != "p" or not (obj.text or "").strip().startswith(caption_prefix):
            continue
        obj.paragraph_format.keep_together = True
        for j in range(idx - 1, -1, -1):
            prev_kind, prev_obj = items[j]
            if prev_kind != "p":
                continue
            drawings = prev_obj._p.xpath('.//w:drawing')
            if not drawings:
                if (prev_obj.text or "").strip():
                    break
                continue
            prev_obj.paragraph_format.keep_with_next = True
            for extent in prev_obj._p.xpath('.//wp:extent'):
                for attr in ('cx', 'cy'):
                    extent.set(attr, str(int(int(extent.get(attr)) * factor)))
            for extent in prev_obj._p.xpath('.//a:ext'):
                for attr in ('cx', 'cy'):
                    extent.set(attr, str(int(int(extent.get(attr)) * factor)))
            return
        raise RuntimeError(f"Figure paragraph not found for caption: {caption_prefix}")
    raise RuntimeError(f"Caption not found: {caption_prefix}")


def polish_appendix_docx(path: Path) -> None:
    doc = Document(path)

    # Keep explanatory notes with the material they qualify.
    _move_note_before_previous_table(doc, "C3/C4 являются уровнями предварительного скрининга")
    _move_note_before_previous_table(doc, "P4 и P5 сохраняют статус NOT ASSESSABLE INTERNALLY")
    _move_note_before_previous_table(doc, "R — выполняет; A — несёт итоговую ответственность")

    # Make the two tall process figures fit together with their captions.
    _shrink_figure_before_caption(doc, "Рисунок Е.1 — Целевой жизненный цикл работы с отзывом", factor=0.60)
    _shrink_figure_before_caption(doc, "Рисунок И.1 — Логика проверки и эскалации", factor=0.64)

    # Targeted table pagination: values are unchanged, only typography/page starts change.
    for kind, obj in list(_body_items(doc)):
        if kind != "t":
            continue
        head = _table_head(obj)
        first = head[0] if head else ""
        second = head[1] if len(head) > 1 else ""

        # Appendix B criticality table: move as one compact block to the next page.
        if first == "Уровень" and second == "Смысл" and len(obj.rows) == 5:
            _set_table_font(obj, 9)
            _insert_page_break_before_table(obj)

        # Appendix V factual tables: slightly tighter typography prevents 1-2 row spillovers.
        elif first in {"source_name", "rating_num", "sentiment_proxy", "aspect", "criticality", "month"}:
            _set_table_font(obj, 8)

        # Appendix D P1-P8 matrix: keep the full 8-row evidence matrix on one landscape page.
        elif first == "id" and second == "problem_hypothesis":
            _set_table_font(obj, 6)

        # Appendix Zh process RACI: avoid a single orphan continuation row.
        elif first == "Этап" and len(head) == 9:
            _set_table_font(obj, 7)

        # Appendix L: start S05 cleanly on the next page so the 3-row mini-table is not split.
        elif first.startswith("S05 —"):
            _insert_page_break_before_table(obj)

        # Appendix T: compact both decision/preregistration tables enough to keep the closing note nearby.
        elif first == "Блок" and second == "Условие":
            _set_table_font(obj, 9)
        elif first == "Поле предварительной регистрации":
            _set_table_font(obj, 8)

    # Keep the closing Appendix T warning before the preregistration table instead of stranding it.
    _move_note_before_previous_table(doc, "Пункты результатов пилота и AFTER не заполняются")

    doc.save(path)


ba.dot_png = safe_dot_png
ba.build()
polish_appendix_docx(ba.DOCX)
