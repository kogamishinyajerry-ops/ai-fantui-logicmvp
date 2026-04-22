"""P43-01 · Step D — Playwright readAsText browser behavior proof (S4).

Opt-in e2e test. Not part of default pytest lane.

Run via: pytest -m e2e tests/test_p43_readAsText_browser_behavior.py -v

Proves the hypothesis that `FileReader.readAsText(file)` at
`src/well_harness/static/ai-doc-analyzer.js:224` silently produces garbage
for pdf/docx binaries: the read "succeeds" (onload fires, no onerror) but
the resulting text is the UTF-8-misinterpreted raw bytes — including the
literal PDF magic header `%PDF-` — which `_documentText` then carries
forward into analysis. The analyzer has no content-type guard between
this step and LLM submission.

Conclusion registered in CONTRACT-PROOF-REPORT.md §2 (S4) and in R6 for
P43-03 fix per plan Q12=B+a (server-side pypdf / python-docx extraction).

Self-contained server boot (does not depend on tests/e2e/conftest.py)
because plan §2c whitelist places this test at tests/ flat, not tests/e2e/.
"""

from __future__ import annotations

import http.client
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = REPO_ROOT / "uploads" / "20260417-C919反推控制逻辑需求文档.pdf"
PORT = 8797  # distinct from tests/e2e/conftest.py (8799) to avoid collision
READY_TIMEOUT_S = 10.0


pytestmark = pytest.mark.e2e


# ---------------------------------------------------------------------------
# Minimal self-contained demo_server boot
# ---------------------------------------------------------------------------

def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) != 0


def _wait_ready(port: int, deadline_s: float) -> bool:
    probe = json.dumps({
        "tra_deg": 0, "radio_altitude_ft": 100, "engine_running": True,
        "aircraft_on_ground": True, "reverser_inhibited": False,
        "eec_enable": True, "n1k": 0.5, "feedback_mode": "auto_scrubber",
        "deploy_position_percent": 0,
    }).encode()
    start = time.monotonic()
    while time.monotonic() - start < deadline_s:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1.0)
            conn.request(
                "POST", "/api/lever-snapshot", body=probe,
                headers={"Content-Type": "application/json"},
            )
            resp = conn.getresponse()
            resp.read()
            conn.close()
            if resp.status == 200:
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            pass
        time.sleep(0.15)
    return False


@pytest.fixture(scope="module")
def demo_server_p43():
    if not _port_free(PORT):
        pytest.fail(f"Port {PORT} already in use")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src") + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    proc = subprocess.Popen(
        [sys.executable, "-m", "well_harness.demo_server", "--port", str(PORT)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        if not _wait_ready(PORT, READY_TIMEOUT_S):
            pytest.fail(f"demo_server not ready on :{PORT} within {READY_TIMEOUT_S}s")
        yield f"http://127.0.0.1:{PORT}"
    finally:
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                pass
            try:
                proc.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    pass
                proc.wait(timeout=2.0)


@pytest.fixture(scope="module")
def playwright_chromium():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("playwright not installed")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            browser.close()


# ---------------------------------------------------------------------------
# Test — S4 evidence dump
# ---------------------------------------------------------------------------

def test_p43_readAsText_pdf_silently_produces_garbage(demo_server_p43, playwright_chromium):
    """pdf upload via ai-doc-analyzer.html → FileReader.readAsText → garbage text.

    Expected observation (broken path):
      - `%PDF-` header literal visible in the preview textarea.
      - No onerror dispatched (upload error element stays empty).
      - `_analyzeBtn.disabled === false` — analyzer is willing to proceed
        with garbage text (this is the missing content-type guard).
      - Character count nonzero (reader did produce a string).
    """
    assert PDF_PATH.exists(), f"fixture pdf missing: {PDF_PATH}"

    page = playwright_chromium.new_page()
    try:
        page.goto(f"{demo_server_p43}/ai-doc-analyzer.html", wait_until="load", timeout=10_000)

        file_input = page.locator("#ai-doc-file-input")
        file_input.set_input_files(str(PDF_PATH))

        page.wait_for_function(
            "() => document.getElementById('ai-doc-preview').value.length > 0",
            timeout=5_000,
        )

        preview_text = page.eval_on_selector("#ai-doc-preview", "el => el.value")
        analyze_disabled = page.eval_on_selector(
            "#ai-doc-analyze-btn", "el => el.disabled"
        )
        upload_error_text = page.eval_on_selector(
            "#ai-doc-upload-error", "el => el.textContent || ''"
        )
    finally:
        page.close()

    # --- Evidence assertions ---------------------------------------------
    assert len(preview_text) > 0, "FileReader produced no text at all (unexpected)."

    assert preview_text.startswith("%PDF-"), (
        "pdf header `%PDF-` missing from readAsText output — upstream behavior "
        "may have changed; P43-03 server-side extraction plan assumptions must "
        "be re-verified. First 40 chars: " + repr(preview_text[:40])
    )

    assert analyze_disabled is False, (
        "analyze button should have stayed ENABLED despite garbage input "
        "(this IS the bug — demonstrates the missing content-type guard)."
    )

    assert upload_error_text.strip() == "", (
        "FileReader.readAsText did not dispatch onerror — the broken flow is "
        "silent. Current error text: " + repr(upload_error_text)
    )

    # --- Shape dump registered in report §2 (S4) -------------------------
    # Ground-truth artifact referenced by CONTRACT-PROOF-REPORT.md §2 S4.
    evidence = {
        "preview_starts_with": preview_text[:8],
        "preview_length": len(preview_text),
        "analyze_btn_disabled": analyze_disabled,
        "upload_error_present": bool(upload_error_text.strip()),
    }
    print(f"\n[P43-01 S4 evidence] {evidence}")
