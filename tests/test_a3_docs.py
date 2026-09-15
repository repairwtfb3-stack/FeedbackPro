from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_a3_source_of_truth_documents_exist():
    required = [
        "A0_BASELINE.md",
        "A1_BASELINE.md",
        "A2_BASELINE.md",
        "A3_DECOMPOSITION.md",
        "REQUIREMENTS_MASTER.md",
        "TRACEABILITY_MASTER.md",
        "THEORY_BASELINE.md",
        "UI_CANON_S01_S10.md",
    ]
    missing = [name for name in required if not (DOCS / name).is_file()]
    assert missing == []


def test_master_requirements_and_traceability_cover_a3_foundation():
    requirements = (DOCS / "REQUIREMENTS_MASTER.md").read_text(encoding="utf-8")
    trace = (DOCS / "TRACEABILITY_MASTER.md").read_text(encoding="utf-8")
    for requirement_id in ("FP-SOT-001", "FP-ARCH-002", "FP-TEST-001", "VKR-G3-003", "VKR-G3-004"):
        assert requirement_id in requirements
        assert requirement_id in trace
    assert "A3.1" in trace and "A3.2" in trace


def test_ui_canon_contains_exact_screen_registry():
    canon = (DOCS / "UI_CANON_S01_S10.md").read_text(encoding="utf-8")
    for i in range(1, 11):
        assert f"S{i:02d}" in canon
    assert "S11" in canon  # explicit prohibition is documented
