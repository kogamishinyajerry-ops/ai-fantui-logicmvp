from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_workbench_loads_annotation_overlay_and_four_tools():
    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")

    assert '<script src="/annotation_overlay.js"' in html
    assert 'id="workbench-annotation-toolbar"' in html
    for tool in ["point", "area", "link", "text-range"]:
        assert f'data-annotation-tool="{tool}"' in html


def test_workbench_exposes_circuit_hero_annotation_surface():
    """P44-01 (replaces three-annotation-surfaces lock): the workbench is
    now centered on a single circuit-hero region that IS the annotation
    surface. The previous 3-column control/document/circuit shell was
    removed because it was empty placeholder scaffolding."""
    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")

    assert 'id="workbench-circuit-hero"' in html
    assert 'data-annotation-surface="circuit"' in html
    # Old per-column annotation surfaces must NOT appear (regression guard).
    assert 'data-annotation-surface="control"' not in html
    assert 'data-annotation-surface="document"' not in html
    assert 'id="workbench-control-panel"' not in html
    assert 'id="workbench-document-panel"' not in html
    assert 'id="workbench-circuit-panel"' not in html


def test_annotation_overlay_js_exports_bootstrap_and_draft_contracts():
    script = (PROJECT_ROOT / "src/well_harness/static/annotation_overlay.js").read_text(encoding="utf-8")

    assert "WorkbenchAnnotationOverlay" in script
    assert "createAnnotationDraft" in script
    assert "installAnnotationOverlay" in script
    for tool in ["point", "area", "link", "text-range"]:
        assert tool in script
