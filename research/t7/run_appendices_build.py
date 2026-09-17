#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

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
    """Rewrite invalid `A[label=..] -> B[label=..]` syntax into valid DOT.

    build_appendices.py intentionally stores compact human-readable graph bodies.
    Graphviz requires node declarations to be separate from an edge chain, so
    this adapter extracts node attributes and then emits the edge statement.
    """
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


ba.dot_png = safe_dot_png
ba.build()
