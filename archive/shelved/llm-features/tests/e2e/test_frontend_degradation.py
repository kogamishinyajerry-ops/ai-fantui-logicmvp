"""E2E Frontend Degradation — DOM + API envelope contract.

Opt-in (@pytest.mark.e2e). Uses requests + BeautifulSoup to observe:
    1. LLM key missing / timeout → structured {error, message} envelope
       that the JS path renders into `.chat-degraded-notice`. The shell
       carries the required DOM anchors (chat-loading-status,
       chat-system-select, etc.) for that notice to land.
    2. API 500/400 on lever-snapshot → the static chat shell is still
       re-servable with canvas <svg> preserved (last-frame-persistence
       contract: JS retains the previous frame because the shell never
       loses the SVG root).
    3. Monte Carlo pathological params (0 / negative / >1e6) → structured
       400 with a renderable error string; no HTML leak, no 5xx.
    4. Archive download (archive-restore) failure on bad manifest_path
       → explicit `{error: "workbench_archive_not_found", ...}` with
       a human-readable message; never a bare 404.

These assertions anchor the frontend's degraded-path behavior without
touching src/. Anchors (DOM IDs + error codes) are what
chat.js keys off to render degraded UI.
"""
from __future__ import annotations

import pytest
import requests
from bs4 import BeautifulSoup


# ─── Stable DOM anchors required for degraded-state rendering ────────────────
# If any of these vanish from chat.html, the JS has nowhere to place the
# degraded notice → effective white-screen even if JS is healthy.
REQUIRED_DOM_IDS = {
    "chat-system-select",
    "system-shell-status",
    "canvas-global-controls",
    "zoom-container",
    "chain-topology-thrust-reverser",
    "chat-input",
    "chat-send-btn",
    "chat-loading-status",   # aria-live region that JS writes degraded copy into
    "chat-drawer",
}


def _get_shell(base_url: str) -> BeautifulSoup:
    resp = requests.get(base_url + "/", timeout=5)
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("Content-Type", "")
    return BeautifulSoup(resp.text, "html.parser")


# ═══════════════════════════════════════════════════════════════════════════
# Path 1: LLM timeout / key missing → .chat-degraded-notice landing contract
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
def test_frontend_llm_failure_returns_structured_envelope_for_degraded_notice(
    no_minimax_key_server,
):
    """LLM path fails → body carries {error, message} that JS renders into
    the `.chat-degraded-notice` DOM node. Break the envelope shape and the
    frontend's degraded render path silently regresses.
    """
    resp = requests.post(
        no_minimax_key_server + "/api/chat/reason",
        json={"question": "why is logic3 active?", "snapshot": {}},
        timeout=10,
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body.get("error") == "minimax_api_key_missing"
    assert isinstance(body.get("message"), str) and body["message"].strip()
    # Must not leak framework internals into a user-facing notice
    for v in body.values():
        if isinstance(v, str):
            assert "Traceback" not in v
            assert '<html' not in v.lower()


@pytest.mark.e2e
def test_frontend_shell_carries_chat_degraded_notice_landing_anchors(demo_server):
    """The static shell must carry the DOM anchors JS needs to attach the
    .chat-degraded-notice node (chat-loading-status aria-live region +
    chat-drawer host + system-shell-status chip).
    """
    soup = _get_shell(demo_server)
    present_ids = {tag.get("id") for tag in soup.find_all(attrs={"id": True})}
    missing = REQUIRED_DOM_IDS - present_ids
    assert not missing, f"chat.html missing degraded-notice landing anchors: {missing}"
    # aria-live region specifically — JS writes LLM-timeout copy here
    loading = soup.find(id="chat-loading-status")
    assert loading is not None
    assert loading.get("aria-live") == "polite", (
        "chat-loading-status must remain an aria-live region for degraded copy"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Path 2: API 500/400 → Canvas keeps last frame (shell + SVG survive)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
def test_frontend_canvas_svg_preserved_in_shell_for_last_frame_persistence(demo_server):
    """Canvas keeps-last-frame requires the <svg class="chain-svg"> to exist
    in the static shell; if it vanishes, the last-frame state has nowhere
    to persist when an API error arrives.
    """
    soup = _get_shell(demo_server)
    svg = soup.find("svg", class_="chain-svg")
    assert svg is not None, "chat.html static shell missing <svg class='chain-svg'>"
    # Canvas node group structure must be present so the previous frame's
    # node-state classes stay rendered when a subsequent snapshot 500s.
    # Canvas-rendered node groups drive last-frame persistence. The thrust-reverser
    # SVG ships a non-trivial number; tie the floor to a value known to exist so
    # that a markup regression (drastic removal) fails this test.
    node_groups = soup.find_all("g", class_="chain-node-group")
    assert len(node_groups) >= 10, (
        f"chain-svg has {len(node_groups)} node groups, "
        f"expected >=10 for last-frame persistence"
    )


@pytest.mark.e2e
def test_frontend_shell_reservable_after_backend_reject_no_white_screen(demo_server):
    """Trigger a structured reject on lever-snapshot, then re-GET the shell.
    If a prior error poisoned the handler, this reveals it — whiteness
    would show as shell < 5KB or missing content-type.
    """
    reject = requests.post(
        demo_server + "/api/lever-snapshot",
        json={"tra_deg": "not-a-number"},
        timeout=5,
    )
    assert reject.status_code in (400, 422)
    resp = requests.get(demo_server + "/", timeout=5)
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("Content-Type", "")
    assert len(resp.text) > 5000, "shell suspiciously small → white-screen regression"


# ═══════════════════════════════════════════════════════════════════════════
# Path 3: Monte Carlo pathological params → structured 400 + renderable UI text
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.parametrize("bad_trials", [0, -1, 1_500_000])
def test_frontend_monte_carlo_bad_n_trials_returns_renderable_response(
    demo_server, bad_trials
):
    """0 / negative / >1e6 must never 5xx. Either clamp (200 + clamped value)
    or structured 400 — both are renderable by the frontend without white-screen.
    The frontend UI notice class keys off a string body.error when 400.
    """
    resp = requests.post(
        demo_server + "/api/monte-carlo/run",
        json={"system_id": "thrust-reverser", "n_trials": bad_trials, "seed": 1},
        timeout=10,
    )
    assert resp.status_code in (200, 400), (
        f"MC with n_trials={bad_trials} returned {resp.status_code} (must be 200 clamped or 400)"
    )
    body = resp.json()
    if resp.status_code == 200:
        # Clamp contract: value falls back into [1, 10000]
        assert 1 <= body["n_trials"] <= 10000
    else:
        # Structured-error contract the frontend renders
        assert isinstance(body.get("error"), str) and body["error"].strip()


@pytest.mark.e2e
def test_frontend_monte_carlo_bad_type_returns_structured_400_not_html(demo_server):
    """Type error must not fall through to an HTML 5xx page — JS fetch would
    fail to JSON-parse and render confusing copy.
    """
    resp = requests.post(
        demo_server + "/api/monte-carlo/run",
        json={"system_id": "thrust-reverser", "n_trials": "nope", "seed": 1},
        timeout=10,
    )
    assert resp.status_code == 400
    assert "application/json" in resp.headers.get("Content-Type", "")
    body = resp.json()
    assert isinstance(body.get("error"), str) and body["error"].strip()


# ═══════════════════════════════════════════════════════════════════════════
# Path 4: Archive download failure → explicit error, not bare 404
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
def test_frontend_archive_download_missing_manifest_returns_explicit_error(demo_server):
    """Archive restore with a non-existent manifest must return a structured
    error with a human-readable message, not a bare 404 or HTML page.
    Frontend archive panel renders body.message as a toast.
    """
    resp = requests.post(
        demo_server + "/api/workbench/archive-restore",
        json={"manifest_path": "/tmp/definitely-does-not-exist-xyz/archive_manifest.json"},
        timeout=10,
    )
    assert resp.status_code == 400, (
        f"archive-restore with missing file returned {resp.status_code} — "
        f"expected structured 400"
    )
    assert "application/json" in resp.headers.get("Content-Type", "")
    body = resp.json()
    assert body.get("error") == "workbench_archive_not_found", (
        f"archive-restore missing-file error code changed: {body.get('error')!r}"
    )
    assert isinstance(body.get("message"), str) and body["message"].strip(), (
        "archive-restore error must carry a renderable message (UI toast source)"
    )


@pytest.mark.e2e
def test_frontend_archive_download_missing_field_returns_explicit_error(demo_server):
    """Missing manifest_path field → structured field-level error the UI
    can translate into a form-validation notice.
    """
    resp = requests.post(
        demo_server + "/api/workbench/archive-restore",
        json={},
        timeout=10,
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body.get("error") == "invalid_workbench_request"
    assert body.get("field") == "manifest_path"
    assert isinstance(body.get("message"), str) and body["message"].strip()


# ═══════════════════════════════════════════════════════════════════════════
# Cross-cutting: 404 on unknown API must be JSON (JS fetch-parse contract)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
def test_frontend_unknown_api_returns_json_404_not_html_page(demo_server):
    resp = requests.get(demo_server + "/api/does-not-exist", timeout=5)
    assert resp.status_code == 404
    assert "application/json" in resp.headers.get("Content-Type", ""), (
        f"404 served as {resp.headers.get('Content-Type')!r} — would break JS fetch"
    )
    body = resp.json()
    assert body.get("error") == "not_found"
