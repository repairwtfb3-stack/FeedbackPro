#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
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
        + body
        + "\n}\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["dot", "-Tpng", "-Gdpi=180", str(dot_path), "-o", str(png_path)],
        check=True,
    )
    return png_path


def _body_items(doc: Document):
    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield "p", Paragraph(child, doc)
        elif isinstance(child, CT_Tbl):
            yield "t", Table(child, doc)


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


def _shrink_figure_before_caption(doc: Document, caption_prefix: str, factor: float = 0.82) -> None:
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
    # These notes were previously orphaned on nearly empty pages after long tables.
    # Moving them before the corresponding table preserves content and improves pagination.
    _move_note_before_previous_table(doc, "C3/C4 являются уровнями предварительного скрининга")
    _move_note_before_previous_table(doc, "P4 и P5 сохраняют статус NOT ASSESSABLE INTERNALLY")
    _move_note_before_previous_table(doc, "R — выполняет; A — несёт итоговую ответственность")
    # Keep the decision-tree caption with its figure by slightly reducing only this figure.
    _shrink_figure_before_caption(doc, "Рисунок И.1 — Логика проверки и эскалации", factor=0.82)
    doc.save(path)


ba.dot_png = safe_dot_png
ba.build()
polish_appendix_docx(ba.DOCX)
