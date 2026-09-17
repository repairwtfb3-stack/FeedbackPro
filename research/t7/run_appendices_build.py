#!/usr/bin/env python3
from __future__ import annotations

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


def safe_dot_png(name: str, dot_body: str) -> Path:
    dot_path = ba.GEN / f"{name}.dot"
    png_path = ba.GEN / f"{name}.png"
    body = _escape_newlines_inside_quotes(dot_body)
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
