"""E11-15c — Chinese-first direction consistency + h1/eyebrow dedup.

Two NIT closures from E11-15b (P3 Demo Presenter):

NIT #1 — h1 + eyebrow duplication
    `<p class="eyebrow">控制逻辑工作台</p>` immediately followed by
    `<h1>控制逻辑工作台 · Control Logic Workbench</h1>` reads redundantly.
    E11-15c flips the eyebrow to `工程师工作区` (a sub-category) so
    eyebrow + h1 read as category + title.

NIT #2 — direction asymmetry
    Column-trio h2s were English-first (`Probe & Trace · 探针与追踪`)
    while the rest of the page is Chinese-first. E11-15c flips them
    to `<中文> · <English>` for full-page direction consistency.

Net change is 4 [REWRITE] lines in workbench.html. Existing test files
test_workbench_column_rename and test_workbench_chinese_eyebrow_sweep
were updated in lockstep with the new strings.
"""

from __future__ import annotations

import http.client
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request("GET", path)
    response = connection.getresponse()
    return response.status, response.read().decode("utf-8")


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. NIT #2: column h2s are now Chinese-first ─────────────────────


@pytest.mark.parametrize(
    "chinese_first_h2",
    [
        "<h2>探针与追踪 · Probe &amp; Trace</h2>",
        "<h2>标注与提案 · Annotate &amp; Propose</h2>",
        "<h2>移交与跟踪 · Hand off &amp; Track</h2>",
    ],
)
def test_column_h2_is_chinese_first(chinese_first_h2: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert chinese_first_h2 in html, f"missing Chinese-first column h2: {chinese_first_h2}"


@pytest.mark.parametrize(
    "stale_english_first_h2",
    [
        "<h2>Probe &amp; Trace · 探针与追踪</h2>",
        "<h2>Annotate &amp; Propose · 标注与提案</h2>",
        "<h2>Hand off &amp; Track · 移交与跟踪</h2>",
    ],
)
def test_stale_english_first_column_h2_removed(stale_english_first_h2: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale_english_first_h2 not in html, (
        f"stale English-first column h2 still present: {stale_english_first_h2}"
    )


# ─── 2. NIT #1: page eyebrow + h1 are no longer duplicates ───────────


def test_page_eyebrow_is_engineer_workspace_not_h1_duplicate() -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert '<p class="eyebrow">工程师工作区</p>' in html
    assert '<p class="eyebrow">控制逻辑工作台</p>' not in html


def test_h1_still_carries_full_bilingual_title() -> None:
    """E11-15b's h1 bilingualization must survive E11-15c — only the
    sibling eyebrow changes; the h1 stays as the page-title source of
    truth."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert "<h1>控制逻辑工作台 · Control Logic Workbench</h1>" in html


def test_eyebrow_and_h1_are_not_chinese_duplicates() -> None:
    """Closure of P3's NIT #1: extracting the eyebrow's Chinese and the
    h1's Chinese, they must not match."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    eyebrow_inner = (
        html.split('<div class="workbench-collab-brand">')[1]
        .split('<p class="eyebrow">')[1]
        .split("</p>")[0]
    )
    h1_inner = html.split("<h1>")[1].split("</h1>")[0]
    h1_chinese = h1_inner.split(" · ")[0]
    assert eyebrow_inner != h1_chinese, (
        f"eyebrow ({eyebrow_inner!r}) duplicates h1 Chinese ({h1_chinese!r}) — "
        "P3 NIT #1 not closed"
    )


# ─── 3. English suffixes preserved (no regression on substring locks) ─


@pytest.mark.parametrize(
    "preserved_english_suffix",
    [
        "Probe &amp; Trace</h2>",
        "Annotate &amp; Propose</h2>",
        "Hand off &amp; Track</h2>",
        "Control Logic Workbench</h1>",
    ],
)
def test_e11_15c_preserves_english_suffix(preserved_english_suffix: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert preserved_english_suffix in html, (
        f"E11-15c broke English suffix invariant: {preserved_english_suffix}"
    )


# ─── 4. Live-served route reflects E11-15c ───────────────────────────


def test_workbench_route_reflects_direction_flip(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    assert "探针与追踪 · Probe" in html
    assert "标注与提案 · Annotate" in html
    assert "移交与跟踪 · Hand off" in html
    assert "工程师工作区" in html


# ─── 5. Truth-engine red line ────────────────────────────────────────


def test_e11_15c_only_touches_static_html_and_tests() -> None:
    """The fix is HTML + test-only. Demo server, controller, runner,
    models, adapters, JS, and CSS must NOT carry any of the 4 new
    strings.

    P4 IMPORTANT closure (E11-15c review): every backend / JS / CSS /
    adapters file is scanned against EVERY new string, not just a
    subset.
    """
    repo_root = Path(__file__).resolve().parents[1]
    well_harness_root = repo_root / "src" / "well_harness"

    new_strings = [
        "工程师工作区",
        "探针与追踪 · Probe",
        "标注与提案 · Annotate",
        "移交与跟踪 · Hand off",
    ]

    scan_targets: list[Path] = [
        well_harness_root / "demo_server.py",
        well_harness_root / "controller.py",
        well_harness_root / "runner.py",
        well_harness_root / "models.py",
        well_harness_root / "static" / "workbench.js",
        well_harness_root / "static" / "workbench.css",
    ]
    adapters_dir = well_harness_root / "adapters"
    if adapters_dir.is_dir():
        scan_targets.extend(p for p in adapters_dir.rglob("*.py"))

    for target in scan_targets:
        if not target.exists():
            continue
        content = target.read_text(encoding="utf-8")
        for new_string in new_strings:
            assert new_string not in content, (
                f"E11-15c string {new_string!r} unexpectedly leaked into "
                f"{target.relative_to(repo_root)}"
            )
