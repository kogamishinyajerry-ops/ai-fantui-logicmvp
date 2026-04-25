from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_workbench_loads_annotation_overlay_and_four_tools():
    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")

    assert '<script src="/annotation_overlay.js"' in html
    assert 'id="workbench-annotation-toolbar"' in html
    for tool in ["point", "area", "link", "text-range"]:
        assert f'data-annotation-tool="{tool}"' in html


def test_workbench_exposes_three_annotation_surfaces():
    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")

    assert 'id="workbench-control-panel"' in html
    assert 'data-annotation-surface="control"' in html
    assert 'id="workbench-document-panel"' in html
    assert 'data-annotation-surface="document"' in html
    assert 'id="workbench-circuit-panel"' in html
    assert 'data-annotation-surface="circuit"' in html


def test_annotation_overlay_js_exports_bootstrap_and_draft_contracts():
    script = (PROJECT_ROOT / "src/well_harness/static/annotation_overlay.js").read_text(encoding="utf-8")

    assert "WorkbenchAnnotationOverlay" in script
    assert "createAnnotationDraft" in script
    assert "installAnnotationOverlay" in script
    for tool in ["point", "area", "link", "text-range"]:
        assert tool in script
