from pathlib import Path
import json
import tomllib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def test_a4_release_version_and_package_contract():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    from feedbackpro.version import VERSION, build_metadata, version_label

    assert pyproject["project"]["version"] == VERSION == "0.4.0rc1"
    assert "release" in pyproject["project"]["optional-dependencies"]
    assert "build_meta.json" in pyproject["tool"]["setuptools"]["package-data"]["feedbackpro"]
    assert build_metadata()["version"] == VERSION
    assert VERSION in version_label()


def test_a4_windows_packaging_files_are_structurally_valid():
    required = [
        "packaging/feedbackpro.spec",
        "packaging/windows/feedbackpro_entry.py",
        "packaging/windows/app.manifest",
        "packaging/windows/build.ps1",
        "packaging/windows/smoke.ps1",
        "scripts/build_windows.ps1",
        "scripts/hash_release.ps1",
        ".github/workflows/windows-release.yml",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), rel

    ET.parse(ROOT / "packaging/windows/app.manifest")
    spec = (ROOT / "packaging/feedbackpro.spec").read_text(encoding="utf-8")
    assert "feedbackpro_entry.py" in spec
    assert "Main.qml" in spec
    assert 'rglob("*.qml")' in spec
    assert "app.manifest" in spec


def test_a4_windows_workflow_preserves_regression_and_artifact_evidence():
    workflow = (ROOT / ".github/workflows/windows-release.yml").read_text(encoding="utf-8")
    for token in [
        "windows-latest",
        "pytest",
        "feedbackpro-gate-a2",
        "feedbackpro-gate-a3",
        "scripts/build_windows.ps1",
        "packaging/windows/smoke.ps1",
        "actions/upload-artifact@v4",
        "release/**",
    ]:
        assert token in workflow

    build = (ROOT / "packaging/windows/build.ps1").read_text(encoding="utf-8")
    for token in ["PyInstaller", "FeedbackPro.exe", "release-manifest.json", "RC_SHA256", "pilot-rc"]:
        assert token in build
    smoke = (ROOT / "packaging/windows/smoke.ps1").read_text(encoding="utf-8")
    assert "SHA-256 mismatch" in smoke
    assert "PACKAGE_SMOKE=PASS" in smoke


def test_a4_release_does_not_claim_pilot_results():
    doc = (ROOT / "docs/A4_R1_R2_IMPLEMENTATION.md").read_text(encoding="utf-8")
    assert "BEFORE/AFTER" in doc
    assert "не являются" in doc
    meta = json.loads((ROOT / "src/feedbackpro/build_meta.json").read_text(encoding="utf-8"))
    assert meta["channel"] == "development"
