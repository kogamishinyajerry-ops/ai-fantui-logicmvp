"""P49-02a — state machine extension lockdown.

Verifies the new GOVERNANCE_HOLD state + transitions are wired
correctly, the existing transitions still work, and bad event
names from GOVERNANCE_HOLD are rejected.
"""

from __future__ import annotations

import pytest

from well_harness.skill_executor.errors import InvalidExecutionTransitionError
from well_harness.skill_executor.states import (
    ALLOWED_TRANSITIONS,
    ExecutionState,
    next_state,
)


# ─── 1. New transitions allowed ───────────────────────────────────


def test_planning_to_governance_hold_allowed():
    assert next_state(
        ExecutionState.PLANNING, "governance_required",
    ) == ExecutionState.GOVERNANCE_HOLD


def test_governance_hold_to_asking_allowed():
    assert next_state(
        ExecutionState.GOVERNANCE_HOLD, "governance_approved",
    ) == ExecutionState.ASKING


def test_governance_hold_to_aborted_via_reject():
    assert next_state(
        ExecutionState.GOVERNANCE_HOLD, "governance_rejected",
    ) == ExecutionState.ABORTED


def test_governance_hold_to_aborted_via_user_abort():
    """Cancel + timeout both come out as user_abort so the
    abort_reason field carries the distinction."""
    assert next_state(
        ExecutionState.GOVERNANCE_HOLD, "user_abort",
    ) == ExecutionState.ABORTED


# ─── 2. Existing transitions still wired ──────────────────────────


def test_planning_to_asking_still_works():
    """The default planner-to-asking path is unchanged for runs
    that don't trip governance."""
    assert next_state(
        ExecutionState.PLANNING, "plan_ready",
    ) == ExecutionState.ASKING


def test_planning_other_events_still_work():
    assert next_state(
        ExecutionState.PLANNING, "planner_error",
    ) == ExecutionState.FAILED
    assert next_state(
        ExecutionState.PLANNING, "user_abort",
    ) == ExecutionState.ABORTED


# ─── 3. Bad event names from GOVERNANCE_HOLD rejected ─────────────


def test_governance_hold_rejects_unknown_event():
    """A typo in event names must surface as
    InvalidExecutionTransitionError, not silently route somewhere
    unsafe."""
    with pytest.raises(InvalidExecutionTransitionError):
        next_state(ExecutionState.GOVERNANCE_HOLD, "edits_applied")


def test_governance_hold_cannot_skip_to_editing_directly():
    """Even with a 'user_approved' event (which works in ASKING),
    GOVERNANCE_HOLD requires the right key. Otherwise a callsite
    bug could bypass the gate."""
    with pytest.raises(InvalidExecutionTransitionError):
        next_state(ExecutionState.GOVERNANCE_HOLD, "user_approved")


# ─── 4. State value is JSON-stable ────────────────────────────────


def test_governance_hold_str_value():
    """Audit JSONs serialize ExecutionState by .value; lock down
    the wire string so old audit files won't drift."""
    assert ExecutionState.GOVERNANCE_HOLD.value == "GOVERNANCE_HOLD"


def test_governance_hold_not_terminal():
    """Mid-flight state, not terminal. Audit code uses is_terminal
    to stop persisting; making GOVERNANCE_HOLD terminal would
    freeze the run."""
    from well_harness.skill_executor.states import is_terminal
    assert is_terminal(ExecutionState.GOVERNANCE_HOLD) is False


# ─── 5. Transitions table includes new edges ──────────────────────


def test_transitions_table_includes_new_edges():
    """Lock down the state-machine declaration so a refactor that
    deletes an entry doesn't silently disable the gate."""
    assert (
        (ExecutionState.PLANNING, "governance_required")
        in ALLOWED_TRANSITIONS
    )
    assert (
        (ExecutionState.GOVERNANCE_HOLD, "governance_approved")
        in ALLOWED_TRANSITIONS
    )
    assert (
        (ExecutionState.GOVERNANCE_HOLD, "governance_rejected")
        in ALLOWED_TRANSITIONS
    )
    assert (
        (ExecutionState.GOVERNANCE_HOLD, "user_abort")
        in ALLOWED_TRANSITIONS
    )
