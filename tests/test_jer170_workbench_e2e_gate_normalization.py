from __future__ import annotations

from pathlib import Path


E2E_SMOKE_PATH = Path("tests/e2e/test_workbench_js_boot_smoke.py")


def test_workbench_e2e_smoke_uses_explicit_readiness_helpers() -> None:
    text = E2E_SMOKE_PATH.read_text(encoding="utf-8")

    assert "def _goto_shell_workbench" in text
    assert "def _goto_bundle_workbench" in text
    assert "wait_for_selector(\"#workbench-identity\", state=\"attached\")" in text
    assert "wait_for_selector(\"#workbench-packet-json\", state=\"attached\")" in text
    assert "typeof window.setWorkbenchIdentity === 'function'" in text
    assert "document.querySelector('#workbench-tool-approve-title')" in text


def test_workbench_e2e_smoke_no_longer_waits_for_global_network_idle() -> None:
    text = E2E_SMOKE_PATH.read_text(encoding="utf-8")

    forbidden_wait = 'wait_until="' + 'networkidle"'
    assert forbidden_wait not in text
