"""E11-15e — Tier-A Chinese-first bundle regression lock.

Bilingualizes 17 user-visible English-only surfaces enumerated by P2
during the E11-15d review (see test_workbench_approval_flow_polish.py
docstring Section 7 + .planning/phases/E11-workbench-engineer-first-ux/
E11-15d-SURFACE-INVENTORY.md):

  Topbar chips (5):       身份/工单/反馈模式/系统 + Manual (advisory) chip
  WOW h3 direction (3):   Causal Chain / Monte Carlo / Reverse Diagnose
  State-of-world (5):     truth-engine SHA / recent e2e / adversarial /
                          open issues / advisory flag
  Trust banner body (3):  scope <em>, advisory <strong>, truth-engine <span>
  Authority banner (1):   Truth Engine — Read Only headline
  Trust dismiss (1):      Hide for session button
  Boot placeholders (3):  pre-hydration "Waiting for ... panel boot."
  Reference packet (1):   Annotate column intro <p>
  Inbox empty (1):        No proposals submitted yet.
  Pending sign-off (1):   Pending Kogami sign-off

Pattern: `<中文> · <English>` everywhere; English suffix is preserved
verbatim so all prior `assert <english> in html` substring locks across
test_workbench_trust_affordance, test_workbench_authority_banner,
test_workbench_role_affordance, test_workbench_column_rename, and
test_workbench_state_of_world_bar continue to pass without contract
churn.

Out of scope (deferred to a future Tier-A or constitutional decision):
  - <option> system values (`Thrust Reverser`, `Landing Gear`, etc.) —
    domain proper nouns coupled to value-attribute IDs and to the
    multi-system adapter dispatch in tests/test_p19_api_multisystem.py.
  - Post-hydration JS boot status strings (`Probe & Trace ready. ...`)
    locked by tests/test_workbench_column_rename.py:170-172 — those are
    a separate JS-side bilingualization with their own lockstep contract.
  - <pre>Intake -> Clarification -> Playback -> Diagnosis -> Knowledge
    </pre> flow diagram — visual phase-arrow, not English copy.
  - Workbench-bundle / approval-center / annotation-toolbar surfaces
    that were already bilingualized in earlier sub-phases.

Test-tier rationale: ≥15 REWRITE strings → Tier-A per the constitution.
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


# ─── 1. Bilingualized strings POSITIVELY locked ──────────────────────


@pytest.mark.parametrize(
    "bilingual",
    [
        # Topbar chip labels (5)
        "<span>身份 · Identity</span>",
        "<span>工单 · Ticket</span>",
        "<span>反馈模式 · Feedback Mode</span>",
        "<span>系统 · System</span>",
        "<strong>手动（仅参考）· Manual (advisory)</strong>",
        # WOW h3 direction flips (3) — Chinese-first per E11-15c convention
        '<h3 id="workbench-wow-a-title">因果链走读 · Causal Chain</h3>',
        '<h3 id="workbench-wow-b-title">1000-trial 可靠性 · Monte Carlo</h3>',
        '<h3 id="workbench-wow-c-title">反向诊断 · Reverse Diagnose</h3>',
        # State-of-world labels (4) + advisory flag (1)
        "真值引擎 SHA · truth-engine SHA",
        "最近 e2e · recent e2e",
        "对抗样本 · adversarial",
        "未关闭问题 · open issues",
        "仅参考 · 非真值引擎实时读数 · advisory · not a live truth-engine reading",
        # Trust banner body (3)
        '这里"手动反馈"的含义 · What "manual feedback" means here:',
        "该模式仅作参考 · That mode is advisory.",
        "真值引擎读数（logic gate L1–L4、controller 派发、审计链）仍然是权威 · Truth engine readings",
        # Trust banner dismiss (1)
        "隐藏（本次会话）· Hide for session",
        # Authority banner headline (1)
        "真值引擎 · 只读 · Truth Engine — Read Only",
        # Pre-hydration boot placeholders (3)
        "等待 probe &amp; trace 面板启动 · Waiting for probe &amp; trace panel boot.",
        "等待 annotate &amp; propose 面板启动 · Waiting for annotate &amp; propose panel boot.",
        "等待 hand off &amp; track 面板启动 · Waiting for hand off &amp; track panel boot.",
        # Reference-packet intro (1)
        "参考资料、澄清说明，以及未来的 text-range 标注会落在这里 · Reference packet, clarification notes",
        # Inbox empty state (1)
        "暂无已提交提案 · No proposals submitted yet.",
        # Pending sign-off (1)
        "等待 Kogami 签字 · Pending Kogami sign-off",
    ],
)
def test_workbench_html_carries_bilingual_e11_15e_string(bilingual: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert bilingual in html, f"missing E11-15e bilingual string: {bilingual}"


# ─── 2. Stale English-only surfaces are gone ─────────────────────────


@pytest.mark.parametrize(
    "stale",
    [
        # Bare topbar chip labels (no Chinese prefix) — must be replaced
        "<span>Identity</span>",
        "<span>Ticket</span>",
        "<span>Feedback Mode</span>",
        "<span>System</span>",
        "<strong>Manual (advisory)</strong>",
        # WOW h3 stale English-first ordering (E11-15c convention)
        '<h3 id="workbench-wow-a-title">Causal Chain · 因果链走读</h3>',
        '<h3 id="workbench-wow-b-title">Monte Carlo · 1000-trial 可靠性</h3>',
        '<h3 id="workbench-wow-c-title">Reverse Diagnose · 反向诊断</h3>',
        # Bare state-of-world labels (no Chinese prefix)
        ">truth-engine SHA<",
        ">recent e2e<",
        ">adversarial<",
        ">open issues<",
        # Bare trust-banner body lines — these are now sentence-internal
        # so we look for the line-leading position they used to hold.
        "<em>What \"manual feedback\" means here:</em>",
        "<strong>That mode is advisory.</strong>",
        # Bare button + headline + boot placeholders
        ">\n          Hide for session\n        <",
        ">\n          Truth Engine — Read Only\n        <",
        ">\n            Waiting for probe &amp; trace panel boot.\n          <",
        ">\n            Waiting for annotate &amp; propose panel boot.\n          <",
        ">\n            Waiting for hand off &amp; track panel boot.\n          <",
        # Bare inbox + pending sign-off
        "<li>No proposals submitted yet.</li>",
        "<strong>Pending Kogami sign-off</strong>",
    ],
)
def test_workbench_html_does_not_carry_stale_english_only(stale: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale not in html, f"stale English-only surface still present: {stale}"


# ─── 3. English suffixes preserved (substring locks unchanged) ───────


@pytest.mark.parametrize(
    "preserved_english_suffix",
    [
        # Anchors required by trust_affordance.py
        "Manual (advisory)",
        "Truth engine readings",
        "Hide for session",
        'What "manual feedback" means here',
        "That mode is advisory.",
        # Anchor required by authority_banner.py
        "Truth Engine — Read Only",
        # Anchor required by role_affordance.py
        "Pending Kogami sign-off",
        # Anchor required by state_of_world_bar.py
        "advisory · not a live truth-engine reading",
        # Anchors required by column_rename.py:118-120 (pre-hydration)
        "Waiting for probe &amp; trace panel boot.",
        "Waiting for annotate &amp; propose panel boot.",
        "Waiting for hand off &amp; track panel boot.",
    ],
)
def test_e11_15e_preserves_english_suffix_locks(preserved_english_suffix: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert preserved_english_suffix in html, (
        f"E11-15e broke English-suffix substring lock: {preserved_english_suffix}"
    )


# ─── 4. Structural anchors preserved ─────────────────────────────────


@pytest.mark.parametrize(
    "anchor",
    [
        'id="workbench-feedback-mode"',
        'id="workbench-trust-banner"',
        'id="workbench-authority-banner"',
        'id="workbench-pending-signoff-affordance"',
        'id="workbench-state-of-world-bar"',
        'id="workbench-wow-starters"',
        'data-trust-banner-dismiss',
        'data-feedback-mode="manual_feedback_override"',
    ],
)
def test_e11_15e_preserves_structural_anchors(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-15e broke structural anchor: {anchor}"


# ─── 5. workbench.js feedback-mode chip stays in lockstep with HTML ──


def test_workbench_js_feedback_mode_label_is_bilingualized() -> None:
    """workbench.js:3788 dynamically rewrites the chip <strong> on mode
    switch. If the JS literal stays English-only, the very first mode
    flip would silently revert the static HTML's bilingual chip back to
    `Manual (advisory)` / `Truth Engine`. Lock both branches."""
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert '"真值引擎 · Truth Engine"' in js, (
        "JS feedback-mode `truth_engine` branch must use bilingual label"
    )
    assert '"手动（仅参考）· Manual (advisory)"' in js, (
        "JS feedback-mode `manual_feedback_override` branch must use bilingual label"
    )
    # Stale English-only literals must not coexist (would imply duplicate
    # write-paths or stale residue).
    assert '"Truth Engine"' not in js, (
        'stale English-only `"Truth Engine"` literal still in workbench.js'
    )
    assert '"Manual (advisory)"' not in js, (
        'stale English-only `"Manual (advisory)"` literal still in workbench.js'
    )


# ─── 6. Live-served route reflects E11-15e end-to-end ────────────────


def test_workbench_route_serves_e11_15e_bundle(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    # Spot-check one string from each surface category.
    assert "身份 · Identity" in html
    assert "因果链走读 · Causal Chain" in html
    assert "真值引擎 SHA · truth-engine SHA" in html
    assert "该模式仅作参考 · That mode is advisory." in html
    assert "隐藏（本次会话）· Hide for session" in html
    assert "真值引擎 · 只读 · Truth Engine — Read Only" in html
    assert "等待 probe &amp; trace 面板启动" in html
    assert "暂无已提交提案 · No proposals submitted yet." in html
    assert "等待 Kogami 签字 · Pending Kogami sign-off" in html


# ─── 7. Truth-engine red line — backend untouched ────────────────────


def test_e11_15e_does_not_touch_truth_engine_backend() -> None:
    """E11-15e only edits static HTML/JS display copy. It must NOT leak
    into controller.py / runner.py / models.py / adapters / demo_server
    (truth-engine red line — see .planning/constitution.md)."""
    repo_root = Path(__file__).resolve().parents[1]
    backend_paths = [
        repo_root / "src" / "well_harness" / "controller.py",
        repo_root / "src" / "well_harness" / "runner.py",
        repo_root / "src" / "well_harness" / "models.py",
        repo_root / "src" / "well_harness" / "demo_server.py",
    ]
    e11_15e_chinese = [
        "身份 · Identity",
        "工单 · Ticket",
        "反馈模式 · Feedback Mode",
        "系统 · System",
        "手动（仅参考）",
        "因果链走读",
        "1000-trial 可靠性",
        "反向诊断 · Reverse Diagnose",
        "真值引擎 SHA",
        "最近 e2e",
        "对抗样本",
        "未关闭问题",
        "仅参考 · 非真值引擎实时读数",
        '这里"手动反馈"的含义',
        "该模式仅作参考",
        "隐藏（本次会话）",
        "真值引擎 · 只读",
        "等待 probe",
        "等待 annotate",
        "等待 hand off",
        "参考资料、澄清说明",
        "暂无已提交提案",
        "等待 Kogami 签字",
    ]
    for backend in backend_paths:
        text = backend.read_text(encoding="utf-8")
        for phrase in e11_15e_chinese:
            assert phrase not in text, (
                f"E11-15e display copy {phrase!r} unexpectedly leaked into "
                f"backend file {backend.name} — truth-engine red-line breach"
            )
