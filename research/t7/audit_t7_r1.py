#!/usr/bin/env python3
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from terminology_r1 import FORBIDDEN_AFTER_R1, TARGET_NAMES, normalize_text

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "t6"
OUT = ROOT / "research" / "t7" / "build"
OUT.mkdir(parents=True, exist_ok=True)

ALL_PARTS = [
    "T6_INTRODUCTION.md",
    "T6_CHAPTER_1.md",
    "T6_CHAPTER_2.md",
    "T6_CHAPTER_3.md",
    "T6_CONCLUSION.md",
]

CITATION_RE = re.compile(r"\[([0-9][0-9;\s,\-–]*)\]")
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")


def citation_tokens(text: str) -> list[str]:
    return CITATION_RE.findall(text)


def expand_citations(text: str) -> set[int]:
    result: set[int] = set()
    for group in citation_tokens(text):
        for part in re.split(r"[;,]", group):
            part = part.strip()
            if not part:
                continue
            m = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part)
            if m:
                a, b = map(int, m.groups())
                result.update(range(min(a, b), max(a, b) + 1))
            elif part.isdigit():
                result.add(int(part))
    return result


def main() -> None:
    transformed: dict[str, str] = {}
    rows: list[str] = []
    failures: list[str] = []

    for name in ALL_PARTS:
        src = (DOCS / name).read_text(encoding="utf-8-sig")
        dst = normalize_text(src) if name in TARGET_NAMES else src
        transformed[name] = dst

        citations_equal = Counter(citation_tokens(src)) == Counter(citation_tokens(dst))
        numbers_equal = NUMBER_RE.findall(src) == NUMBER_RE.findall(dst)
        if not citations_equal:
            failures.append(f"{name}: citation tokens changed")
        if not numbers_equal:
            failures.append(f"{name}: numeric token sequence changed")

        rows.append(
            f"| {name} | {'PASS' if citations_equal else 'FAIL'} | "
            f"{'PASS' if numbers_equal else 'FAIL'} |"
        )

    combined = "\n".join(transformed.values())
    used = expand_citations(combined)
    expected = set(range(1, 41))
    if used != expected:
        failures.append(f"citation set changed: expected 1..40, got {sorted(used)}")

    non_recent = {27, 32, 33, 34, 35, 36, 37}
    recent_used = used - non_recent
    recent_ratio = (len(recent_used) / len(used) * 100) if used else 0.0
    if len(used) < 35:
        failures.append(f"CITED threshold failed: {len(used)} < 35")
    if recent_ratio < 80.0:
        failures.append(f"RECENT threshold failed: {recent_ratio:.2f}% < 80%")

    residual: list[str] = []
    for term in FORBIDDEN_AFTER_R1:
        if term.lower() in combined.lower():
            residual.append(term)
    if residual:
        failures.append("forbidden editorial terms remain: " + ", ".join(residual))

    anchors = {
        "1200": "корпус 1200",
        "1192": "Yandex Maps / public responses 1192",
        "99,33": "99,33% public response",
        "143": "C3/C4 screening baseline 143",
        "35": "high-criticality cross-rating baseline 35",
        "01.09.2025": "period start",
        "31.08.2026": "period end",
        "P4": "P4 limitation",
        "P5": "P5 limitation",
        "S01": "S01–S10 architecture",
        "E0": "E0–E8 implementation",
    }
    missing_anchors = [label for token, label in anchors.items() if token not in combined]
    if missing_anchors:
        failures.append("evidence anchors missing: " + ", ".join(missing_anchors))

    report = [
        "# T7.1-R1 citation/evidence audit",
        "",
        "R1 is an editorial transformation of the closed T6 baseline. The audit checks that wording changes do not alter citation placement or numeric evidence.",
        "",
        "## Invariance by source part",
        "",
        "| Part | Citation tokens | Numeric tokens |",
        "|---|---|---|",
        *rows,
        "",
        "## Citation coverage",
        "",
        f"- cited source IDs: **{len(used)}/40**;",
        f"- expected source set 1–40 preserved: **{'PASS' if used == expected else 'FAIL'}**;",
        f"- modern 2022–2026 sources: **{len(recent_used)}/{len(used)} = {recent_ratio:.1f}%**;",
        f"- threshold `CITED >= 35`: **{'PASS' if len(used) >= 35 else 'FAIL'}**;",
        f"- threshold `RECENT >= 80%`: **{'PASS' if recent_ratio >= 80 else 'FAIL'}**.",
        "",
        "## Evidence invariance",
        "",
        "- numeric token sequence for every edited part must be byte-order equivalent at token level;",
        "- key anchors 1200 / 1192 / 99,33 / 143 / 35 / study period / P4-P5 / S01 / E0 are required;",
        f"- anchor check: **{'PASS' if not missing_anchors else 'FAIL'}**.",
        "",
        "## Editorial term audit",
        "",
        f"- forbidden residual terms: **{', '.join(residual) if residual else 'none'}**;",
        f"- result: **{'PASS' if not residual else 'FAIL'}**.",
        "",
        "## Final",
        "",
        f"**T7.1-R1 AUDIT = {'PASS' if not failures else 'FAIL'}**",
    ]
    if failures:
        report.extend(["", "Failures:"] + [f"- {x}" for x in failures])

    out = OUT / "T7_R1_AUDIT.md"
    out.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(out.read_text(encoding="utf-8"))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
