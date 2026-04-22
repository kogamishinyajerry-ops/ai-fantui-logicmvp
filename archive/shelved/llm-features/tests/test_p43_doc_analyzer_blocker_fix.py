"""P43-01 · Step B regression tests.

Locks the four Counter-F contract bugs in run_pipeline_from_intake():
- Bug A: assessment.get("blockers") silently bypassed the blocker guard
  (emitted key is "blocking_reasons" at document_intake.py:940).
- Bug B1: bundle.playback_report.scenarios (no such attribute on
  ScenarioPlaybackReport — singular report, not a collection).
- Bug B2: bundle.fault_diagnosis_report.fault_modes (no such attribute
  on FaultDiagnosisReport — singular diagnosis).

Frontend consumer contract at static/ai-doc-analyzer.js:527-528
(result.status === "blocked" / result.blockers) — pinned by test 4.

Bug D (clarify-{i} stable-ID drift) is R6 report-only scope → P43-03.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from well_harness.ai_doc_analyzer import run_pipeline_from_intake


FIXTURES_ROOT = Path(__file__).parent / "fixtures" / "p43_spike"
HAPPY_FIXTURE = FIXTURES_ROOT / "real_pdf_happy_path" / "intake_minimal_ready.json"
BLOCKED_FIXTURE = FIXTURES_ROOT / "synthetic_blocker" / "intake_missing_source_docs.json"

SOURCE_FILE = Path(__file__).parent.parent / "src" / "well_harness" / "ai_doc_analyzer.py"
FRONTEND_FILE = Path(__file__).parent.parent / "src" / "well_harness" / "static" / "ai-doc-analyzer.js"


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# Test 1 — Bug A: blocker guard triggers on missing source_documents
# ---------------------------------------------------------------------------

def test_p43_blocker_guard_triggers_on_missing_source_documents():
    """Blocked packet returns status=blocked shape; Bug A regression."""
    intake = _load(BLOCKED_FIXTURE)
    result = run_pipeline_from_intake(intake)

    assert result.get("status") == "blocked", (
        f"blocker guard must fire; got status={result.get('status')!r}. "
        "Regression of Bug A (assessment.get('blockers') vs emitted 'blocking_reasons')."
    )
    assert isinstance(result.get("blockers"), list) and result["blockers"], (
        "blockers key must be non-empty list (frontend contract)."
    )
    assert "at least one source document is required." in result["blockers"]
    assert result.get("message") == (
        "存在阻塞问题，无法构建诊断 bundle。请先解决以下问题。"
    ), "blocker message must match frontend literal."
    # Blocked path must NOT expose bundle/system_snapshot.
    assert "bundle" not in result
    assert "system_snapshot" not in result


# ---------------------------------------------------------------------------
# Test 2 — Happy path: B1 + B2 AttributeErrors do not fire; shape complete
# ---------------------------------------------------------------------------

def test_p43_happy_path_returns_full_contract_shape():
    """Ready packet returns assessment + bundle + system_snapshot; Bugs B1 + B2 regression."""
    intake = _load(HAPPY_FIXTURE)
    # Must not raise AttributeError on bundle.playback_report.scenarios (B1)
    # or bundle.fault_diagnosis_report.fault_modes (B2).
    result = run_pipeline_from_intake(intake)

    assert "status" not in result, "ready path must not emit status key."
    assert set(result.keys()) == {"assessment", "bundle", "system_snapshot"}, (
        f"ready return must have exact top-level keys; got {sorted(result.keys())}."
    )

    bundle = result["bundle"]
    assert bundle is not None, "ready packet must build a bundle."
    assert bundle["ready_for_spec_build"] is True
    # Single ScenarioPlaybackReport per bundle → scenario_count is 0 or 1.
    assert bundle["scenario_count"] in (0, 1), (
        f"scenario_count must be int 0/1 (one report per bundle); got {bundle['scenario_count']!r}."
    )
    assert bundle["fault_mode_count"] in (0, 1), (
        f"fault_mode_count must be int 0/1; got {bundle['fault_mode_count']!r}."
    )

    snap = result["system_snapshot"]
    assert snap["ready_for_spec_build"] is True
    assert snap["component_count"] == 3
    assert snap["logic_node_count"] == 1
    assert snap["acceptance_scenario_count"] == 1
    assert snap["fault_mode_count"] == 1


# ---------------------------------------------------------------------------
# Test 3 — Regression grep: no stale 'blockers' reader or list-count access
# ---------------------------------------------------------------------------

def test_p43_no_stale_contract_readers_in_source():
    """Source file has no stale contract readers (defend against re-introduction).

    Specifically catches:
      - assessment.get("blockers") / assessment["blockers"] (Bug A)
      - bundle.playback_report.scenarios (Bug B1)
      - bundle.fault_diagnosis_report.fault_modes (Bug B2)
    """
    source = SOURCE_FILE.read_text(encoding="utf-8")

    assert not re.search(r'assessment\.get\(\s*["\']blockers["\']\s*\)', source), (
        "Bug A regression: assessment.get('blockers') found — must read 'blocking_reasons'."
    )
    assert not re.search(r'assessment\[\s*["\']blockers["\']\s*\]', source), (
        "Bug A regression: assessment['blockers'] indexing found — must read 'blocking_reasons'."
    )
    assert "playback_report.scenarios" not in source, (
        "Bug B1 regression: bundle.playback_report.scenarios — ScenarioPlaybackReport has no .scenarios attr."
    )
    assert "fault_diagnosis_report.fault_modes" not in source, (
        "Bug B2 regression: bundle.fault_diagnosis_report.fault_modes — FaultDiagnosisReport has no .fault_modes attr."
    )


# ---------------------------------------------------------------------------
# Test 4 — Frontend consumer audit: emit key 'blockers' + status 'blocked' literal
# ---------------------------------------------------------------------------

def test_p43_frontend_consumer_contract_alignment():
    """ai-doc-analyzer.js consumes result.blockers + status === 'blocked' literally.

    Backend EMIT key "blockers" (preserved after READ-side Bug A fix) and literal
    status == "blocked" must stay aligned with frontend reader contract.
    """
    frontend = FRONTEND_FILE.read_text(encoding="utf-8")

    assert re.search(r'result\.status\s*===\s*["\']blocked["\']', frontend), (
        "Frontend must read result.status === 'blocked' — backend emit key alignment."
    )
    assert re.search(r'result\.blockers', frontend), (
        "Frontend must read result.blockers — backend EMIT key 'blockers' preserved."
    )
