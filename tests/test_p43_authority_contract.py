"""P43 Authority Contract Tests — R1-R6 mechanical compliance.

All tests are string-grep style: they inspect source files, not runtime behaviour.

Tests marked @pytest.mark.xfail are for rules whose implementation is pending
in later P43 sub-phases. They will be unmarked as each phase lands.

R1  (P43-02 · Step 3a/B)   — backend never writes draft_design_state   [PASS now]
R2  (P43-08)                — final_approve never reads draft            [xfail: handler missing]
R3  (P43-03/04)             — frozenSpec via assignFrozenSpec+deepFreeze [xfail: not yet]
R4  (P43-05/06)             — generator reads frozen only                [xfail: not yet]
R5  (P43-07)                — validateDraftAgainstFrozen singleton        [xfail: not yet]
R6a (P43-08)                — final_approve removes draft key             [xfail: handler missing]
R6b (P43-02 · Step 3a/B)   — archive bundle excludes draft               [PASS now]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
_WJS  = _REPO / "src" / "well_harness" / "static" / "workbench.js"
_WPY  = _REPO / "src" / "well_harness" / "workbench_bundle.py"
_DSV  = _REPO / "src" / "well_harness" / "demo_server.py"


# ──────────────────────────────────────────────
# fixtures
# ──────────────────────────────────────────────

@pytest.fixture(scope="module")
def wjs() -> str:
    assert _WJS.exists(), f"workbench.js missing: {_WJS}"
    return _WJS.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def wpy() -> str:
    assert _WPY.exists(), f"workbench_bundle.py missing: {_WPY}"
    return _WPY.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def dsv() -> str:
    assert _DSV.exists(), f"demo_server.py missing: {_DSV}"
    return _DSV.read_text(encoding="utf-8")


def _grep(text: str, pattern: str) -> list[int]:
    return [i + 1 for i, line in enumerate(text.splitlines()) if re.search(pattern, line)]


def _find_block(text: str, start_re: str, max_lines: int = 80) -> str:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(start_re, line):
            return "\n".join(lines[i : i + max_lines])
    return ""


# ──────────────────────────────────────────────
# R1 — backend never writes draft_design_state
# (PASS now — implementation-agnostic absence check)
# ──────────────────────────────────────────────

class TestR1BackendNoDraftWrite:
    def test_r1_demo_server_no_draft_key(self, dsv: str):
        """demo_server.py must never write draft_design_state."""
        hits = _grep(dsv, r"draft_design_state|draftDesignState")
        assert hits == [], (
            f"R1 VIOLATION: demo_server.py references draft key at lines {hits}. "
            "Backend must never write draft_design_state."
        )

    def test_r1_workbench_bundle_no_draft_emit(self, wpy: str):
        """workbench_bundle.py must never emit draft_design_state to clients."""
        # Bundle may contain the string as a comment / guard; we check for
        # any write/serialize pattern (not mere mention in comments).
        write_hits = _grep(wpy, r"['\"]draft_design_state['\"]|['\"]draftDesignState['\"]")
        assert write_hits == [], (
            f"R1 VIOLATION: workbench_bundle.py serialises draft key at lines {write_hits}."
        )


# ──────────────────────────────────────────────
# R2 — final_approve handler never reads draft
# (xfail: final_approve handler not yet implemented — P43-08)
# ──────────────────────────────────────────────

class TestR2FinalApproveNoDraftRead:
    @pytest.mark.xfail(
        strict=False,
        reason="P43-08: final_approve handler not yet implemented in workbench.js",
    )
    def test_r2_final_approve_handler_exists(self, wjs: str):
        """final_approve handler must exist before we can verify R2."""
        block = _find_block(wjs, r"function\s+handleFinalApprove|handleFinalApprove\s*=\s*(?:async\s+)?function")
        assert block != "", "final_approve handler not found in workbench.js"

    @pytest.mark.xfail(
        strict=False,
        reason="P43-08: final_approve handler not yet implemented",
    )
    def test_r2_handler_no_draft_getitem(self, wjs: str):
        """final_approve block must not call getItem on draft key."""
        block = _find_block(wjs, r"function\s+handleFinalApprove|handleFinalApprove\s*=\s*(?:async\s+)?function")
        assert block, "final_approve handler not found — skipping R2 read check"
        read_hits = [p for p in [r"getItem.*draft", r"draft_design_state", r"draftDesignState"]
                     if re.search(p, block)]
        assert read_hits == [], (
            f"R2 VIOLATION: final_approve block reads draft via patterns: {read_hits}"
        )


# ──────────────────────────────────────────────
# R3 — frozenSpec only via assignFrozenSpec+deepFreeze
# (xfail: assignFrozenSpec/deepFreeze not yet in workbench.js — P43-03/04)
# ──────────────────────────────────────────────

class TestR3FrozenSpecControlledWriter:
    @pytest.mark.xfail(
        strict=False,
        reason="P43-03: assignFrozenSpec not yet implemented in workbench.js",
    )
    def test_r3_assign_frozen_spec_declared(self, wjs: str):
        """assignFrozenSpec function must be declared in workbench.js."""
        found = bool(re.search(r"function assignFrozenSpec|assignFrozenSpec\s*=", wjs))
        assert found, "assignFrozenSpec declaration missing from workbench.js"

    @pytest.mark.xfail(
        strict=False,
        reason="P43-03: deepFreeze not yet implemented in workbench.js",
    )
    def test_r3_deepfreeze_declared(self, wjs: str):
        """deepFreeze function must be declared in workbench.js."""
        found = bool(re.search(r"function deepFreeze|const deepFreeze\s*=|var deepFreeze\s*=", wjs))
        assert found, "deepFreeze declaration missing from workbench.js"

    @pytest.mark.xfail(
        strict=False,
        reason="P43-03: frozenSpec not yet introduced; bare-write check vacuously passes but marked xfail for parity",
    )
    def test_r3_no_bare_frozenspec_assignment(self, wjs: str):
        """No bare `frozenSpec = ...` outside assignFrozenSpec body."""
        # Collect assignments but exclude variable declarations (let/const/var frozenSpec = ...)
        _wjs_lines = wjs.splitlines()
        candidate_lines = [
            ln for ln in _grep(wjs, r"frozenSpec\s*=(?!=)")
            if not re.search(r"\b(?:let|const|var)\s+frozenSpec\b", _wjs_lines[ln - 1])
        ]
        # Remove lines inside assignFrozenSpec body (heuristic: within 15 lines of declaration)
        decl_line = next(
            (i + 1 for i, l in enumerate(wjs.splitlines())
             if re.search(r"function assignFrozenSpec|assignFrozenSpec\s*=", l)),
            None,
        )
        if decl_line is None:
            # assignFrozenSpec doesn't exist yet → any frozenSpec= is a violation
            assert candidate_lines == [], (
                f"R3 VIOLATION: bare frozenSpec= at lines {candidate_lines} "
                "(assignFrozenSpec not yet declared)"
            )
            return
        allowed = set(range(decl_line, decl_line + 20))
        bad = [ln for ln in candidate_lines if ln not in allowed]
        assert bad == [], f"R3 VIOLATION: bare frozenSpec= outside assignFrozenSpec at lines {bad}"

    @pytest.mark.xfail(
        strict=False,
        reason="P43-03: frozenSpec not yet introduced; alias-mutate check vacuously passes",
    )
    def test_r3_no_alias_mutate_patterns(self, wjs: str):
        """Forbidden alias-mutate patterns must not appear."""
        forbidden = [
            r"frozenSpec\.merge\(",
            r"frozenSpec\.assign\(",
            r"Object\.assign\(frozenSpec",
            r"\{\.\.\.frozenSpec,\s*\.\.\.draft",
        ]
        found = [p for p in forbidden if re.search(p, wjs)]
        assert found == [], f"R3 VIOLATION: alias-mutate patterns found: {found}"

    @pytest.mark.xfail(
        strict=False,
        reason="P43-03: assignFrozenSpec not yet implemented; origin check pending",
    )
    def test_r3_no_draft_origin(self, wjs: str):
        """All assignFrozenSpec call-sites must use origin ∈ {'freeze-event','archive-restore'}."""
        # Check lines that call assignFrozenSpec but are NOT function declarations or comments
        call_lines = [
            line.strip() for line in wjs.splitlines()
            if "assignFrozenSpec(" in line
            and not re.search(r"\bfunction\b", line)
            and not line.strip().startswith("//")
        ]
        assert call_lines, "assignFrozenSpec call sites not found — cannot check origin"
        bad = [l for l in call_lines if not re.search(r"freeze-event|archive-restore", l)]
        assert bad == [], (
            f"R3 VIOLATION: assignFrozenSpec call sites without valid origin:\n" +
            "\n".join(f"  {l}" for l in bad)
        )

    @pytest.mark.xfail(
        strict=False,
        reason="P43-03: deepFreeze not yet implemented; runtime enforcement pending",
    )
    def test_r3_deepfreeze_called_in_assign(self, wjs: str):
        """assignFrozenSpec body must call deepFreeze(newSpec)."""
        block = _find_block(wjs, r"function assignFrozenSpec|assignFrozenSpec\s*=")
        assert block, "assignFrozenSpec not found"
        assert re.search(r"deepFreeze\(", block), (
            "R3 VIOLATION: assignFrozenSpec does not call deepFreeze()"
        )


# ──────────────────────────────────────────────
# R4 — generator reads frozenSpec only, never draft
# (xfail: generator not yet implemented — P43-05/06)
# ──────────────────────────────────────────────

class TestR4GeneratorFrozenOnly:
    @pytest.mark.xfail(
        strict=False,
        reason="P43-05: generator function not yet implemented in workbench.js",
    )
    def test_r4_generator_exists(self, wjs: str):
        """Generator function must be present before R4 can be verified."""
        block = _find_block(wjs, r"start_gen|generatePanel|runGeneration|handleStartGen")
        assert block != "", "Generator function not found in workbench.js"

    @pytest.mark.xfail(
        strict=False,
        reason="P43-05: generator not yet implemented",
    )
    def test_r4_generator_no_draft_read(self, wjs: str):
        """Generator block must not read draft_design_state."""
        block = _find_block(wjs, r"start_gen|generatePanel|runGeneration|handleStartGen")
        assert block, "Generator not found — R4 check skipped"
        bad = [p for p in [r"draft_design_state", r"draftDesignState"] if re.search(p, block)]
        assert bad == [], f"R4 VIOLATION: generator reads draft via: {bad}"


# ──────────────────────────────────────────────
# R5 — validateDraftAgainstFrozen singleton in workbench.js
# (xfail: not yet implemented — P43-07)
# ──────────────────────────────────────────────

class TestR5ValidatorSingleton:
    @pytest.mark.xfail(
        strict=False,
        reason="P43-07: validateDraftAgainstFrozen not yet implemented",
    )
    def test_r5_singleton_declared(self, wjs: str):
        """validateDraftAgainstFrozen must be declared exactly once in workbench.js."""
        decl_count = len(re.findall(
            r"function validateDraftAgainstFrozen|validateDraftAgainstFrozen\s*=",
            wjs,
        ))
        assert decl_count >= 1, "validateDraftAgainstFrozen missing from workbench.js"
        assert decl_count == 1, (
            f"R5 VIOLATION: validateDraftAgainstFrozen declared {decl_count} times — must be singleton"
        )


# ──────────────────────────────────────────────
# R6 — final_approve deletes draft; archive excludes draft
# R6a: final_approve handler (xfail — P43-08)
# R6b: archive exclusion (PASS now — absence check)
# ──────────────────────────────────────────────

class TestR6LifecycleBoundary:
    @pytest.mark.xfail(
        strict=False,
        reason="P43-08: final_approve handler not yet implemented",
    )
    def test_r6_final_approve_removes_draft(self, wjs: str):
        """final_approve block must delete draft via removeItem or clearDraftDesignState()."""
        block = _find_block(wjs, r"function\s+handleFinalApprove|handleFinalApprove\s*=\s*(?:async\s+)?function")
        assert block, "final_approve handler not found"
        pattern = (
            r"(?:localStorage\.removeItem\([^)]*(?:draft_design_state|draftDesignState)[^)]*\)"
            r"|clearDraftDesignState\(\))"
        )
        assert re.search(pattern, block), (
            "R6 VIOLATION: final_approve block does not delete draft "
            "(expected clearDraftDesignState() or localStorage.removeItem(draft_design_state))"
        )

    def test_r6_archive_bundle_excludes_draft(self, wpy: str):
        """workbench_bundle.py archive must not contain any draft key references."""
        hits = _grep(wpy, r"['\"]draft_design_state['\"]|['\"]draftDesignState['\"]")
        assert hits == [], (
            f"R6 VIOLATION: workbench_bundle.py serialises draft key at lines {hits}. "
            "Archive bundle must never contain draft_design_state."
        )

    def test_r6_bundle_no_draft_substring(self, wpy: str):
        """workbench_bundle.py must contain no draft_design_state string anywhere."""
        # Broader check: even comments should not reference the key as a value
        hits = _grep(wpy, r"draft_design_state|draftDesignState")
        assert hits == [], (
            f"R6 NOTE: workbench_bundle.py mentions draft key at lines {hits}. "
            "Verify these are not serialisation paths."
        )


# ──────────────────────────────────────────────
# Observability: check_authority_contract.py tool
# ──────────────────────────────────────────────

class TestAuthorityContractTool:
    def test_tool_exists_and_is_runnable(self):
        """tools/check_authority_contract.py must exist and be importable."""
        tool = _REPO / "tools" / "check_authority_contract.py"
        assert tool.exists(), "tools/check_authority_contract.py missing"
        # Verify it's valid Python
        import importlib.util
        spec = importlib.util.spec_from_file_location("check_authority_contract", tool)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        assert hasattr(mod, "run"), "check_authority_contract.py must expose run()"
        assert hasattr(mod, "_CHECKERS"), "check_authority_contract.py must expose _CHECKERS"

    def test_tool_covers_all_six_rules(self):
        """check_authority_contract.py must cover R1 through R6."""
        tool = _REPO / "tools" / "check_authority_contract.py"
        content = tool.read_text(encoding="utf-8")
        for rule in ["R1", "R2", "R3", "R4", "R5", "R6"]:
            assert f'"{rule}"' in content or f"'{rule}'" in content or f"check_{rule.lower()}" in content, (
                f"check_authority_contract.py does not cover {rule}"
            )

    def test_tool_r1_returns_pass(self):
        """R1 check must return PASS against current codebase (no backend draft writes)."""
        sys.path.insert(0, str(_REPO / "tools"))
        import check_authority_contract as m
        sys.path.pop(0)
        js  = _WJS.read_text()
        wpy = _WPY.read_text()
        dsv = _DSV.read_text()
        result = m.check_r1(js, dsv)
        assert result["status"] == "PASS", (
            f"R1 unexpectedly non-PASS: {result['detail']}"
        )

    def test_tool_r6b_returns_pass(self):
        """R6 archive check must return PASS (archive already excludes draft)."""
        sys.path.insert(0, str(_REPO / "tools"))
        import check_authority_contract as m
        sys.path.pop(0)
        js  = _WJS.read_text()
        wpy = _WPY.read_text()
        result = m.check_r6(js, wpy)
        # R6 may be PASS or MISSING (handler not there) but NOT FAIL
        assert result["status"] != "FAIL", (
            f"R6 archive FAIL — bundle contains draft references: {result['detail']}"
        )
