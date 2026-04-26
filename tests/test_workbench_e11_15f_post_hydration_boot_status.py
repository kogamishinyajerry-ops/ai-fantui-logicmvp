"""E11-15f — bilingualize the 3 post-hydration boot-status strings in
workbench.js (the strings users actually see for most of the session;
the pre-hydration `Waiting for ...` flash that E11-15e closed is shown
only briefly before JS hydration replaces it).

Pattern: `<中文> · <English>`. English suffix preserved verbatim so the
existing locks at `tests/test_workbench_column_rename.py:170-172`
continue to pass without contract churn.

Out of scope: the 3 deferred surfaces still listed in
`E11-15e-SURFACE-INVENTORY.md` Section 3 (`<option>` system values,
`<pre>` flow diagram, eyebrow column tags).
"""

from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"


@pytest.mark.parametrize(
    "bilingual",
    [
        "探针与追踪面板就绪，场景动作已编入下一捆 · Probe & Trace ready. Scenario actions are staged for the next bundle.",
        "标注与提案面板就绪，text-range 标注已编入下一捆 · Annotate & Propose ready. Text-range annotation is staged for the next bundle.",
        "移交与跟踪面板就绪，覆盖层标注已编入下一捆 · Hand off & Track ready. Overlay annotation is staged for the next bundle.",
    ],
)
def test_workbench_js_post_hydration_boot_status_is_bilingualized(bilingual: str) -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert bilingual in js, f"missing E11-15f bilingual boot status: {bilingual}"


@pytest.mark.parametrize(
    "stale",
    [
        # Bare English-only literals (no Chinese prefix) must be gone.
        '"Probe & Trace ready. Scenario actions are staged for the next bundle.";',
        '"Annotate & Propose ready. Text-range annotation is staged for the next bundle.";',
        '"Hand off & Track ready. Overlay annotation is staged for the next bundle.";',
    ],
)
def test_workbench_js_post_hydration_no_bare_english(stale: str) -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert stale not in js, f"E11-15f stale English-only literal still in workbench.js: {stale}"


@pytest.mark.parametrize(
    "preserved_english_suffix",
    [
        # column_rename:170-172 substring locks must keep passing.
        "Probe & Trace ready. Scenario actions are staged for the next bundle.",
        "Annotate & Propose ready. Text-range annotation is staged for the next bundle.",
        "Hand off & Track ready. Overlay annotation is staged for the next bundle.",
    ],
)
def test_e11_15f_preserves_english_suffix(preserved_english_suffix: str) -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert preserved_english_suffix in js, (
        f"E11-15f broke English-suffix substring lock: {preserved_english_suffix}"
    )


def test_e11_15f_does_not_touch_truth_engine_backend() -> None:
    """E11-15f only edits a static JS literal. Backend (controller.py /
    runner.py / models.py / demo_server.py / adapters/**) must stay
    untouched per truth-engine red line."""
    repo_root = Path(__file__).resolve().parents[1]
    well_harness_dir = repo_root / "src" / "well_harness"
    backend_paths: list[Path] = [
        well_harness_dir / "controller.py",
        well_harness_dir / "runner.py",
        well_harness_dir / "models.py",
        well_harness_dir / "demo_server.py",
    ]
    adapters_dir = well_harness_dir / "adapters"
    if adapters_dir.is_dir():
        backend_paths.extend(
            p for p in adapters_dir.rglob("*.py") if "__pycache__" not in p.parts
        )
    e11_15f_chinese = [
        "探针与追踪面板就绪",
        "标注与提案面板就绪",
        "移交与跟踪面板就绪",
        "场景动作已编入下一捆",
        "text-range 标注已编入下一捆",
        "覆盖层标注已编入下一捆",
    ]
    for backend in backend_paths:
        text = backend.read_text(encoding="utf-8")
        for phrase in e11_15f_chinese:
            assert phrase not in text, (
                f"E11-15f display copy {phrase!r} unexpectedly leaked into "
                f"{backend.relative_to(repo_root)} — truth-engine red-line breach"
            )
