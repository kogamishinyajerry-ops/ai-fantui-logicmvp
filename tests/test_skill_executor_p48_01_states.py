"""P48-01 — skill executor state machine.

Locks down: 8 states, fixed transition table, 3 terminal states. The
audit log records every state transition; an audit can never claim a
forbidden transition because the writer enforces the table.
"""

from __future__ import annotations

import pytest

from well_harness.skill_executor.errors import InvalidExecutionTransitionError
from well_harness.skill_executor.states import (
    ALLOWED_TRANSITIONS,
    TERMINAL_STATES,
    ExecutionState,
    is_terminal,
    next_state,
)


# ─── 1. State enum ─────────────────────────────────────────────────────


def test_state_enum_has_eleven_states():
    """7 non-terminal (INIT/PLANNING/GOVERNANCE_HOLD/ASKING/EDITING/
    TESTING/PR_OPEN) + 4 terminal (LANDED/DRY_RUN_COMPLETE/ABORTED/
    FAILED) = 11. GOVERNANCE_HOLD added in P49-02a;
    DRY_RUN_COMPLETE added in P49-04. Locking the count so a future
    PR can't quietly drop a state and rely on no caller tripping
    the diff."""
    assert len(list(ExecutionState)) == 11


@pytest.mark.parametrize(
    "expected",
    [
        "INIT",
        "PLANNING",
        "GOVERNANCE_HOLD",
        "ASKING",
        "EDITING",
        "TESTING",
        "PR_OPEN",
        "LANDED",
        "DRY_RUN_COMPLETE",
        "ABORTED",
        "FAILED",
    ],
)
def test_state_enum_contains(expected):
    """If we drop one of these we lose audit replay coverage for
    that lifecycle stage."""
    assert ExecutionState(expected).value == expected


def test_state_enum_serializes_to_string():
    """JSON serialization relies on the enum being a str subclass."""
    assert isinstance(ExecutionState.INIT.value, str)


# ─── 2. Terminal states ────────────────────────────────────────────────


def test_four_terminal_states():
    assert TERMINAL_STATES == frozenset(
        {
            ExecutionState.LANDED,
            ExecutionState.DRY_RUN_COMPLETE,
            ExecutionState.ABORTED,
            ExecutionState.FAILED,
        }
    )


@pytest.mark.parametrize(
    "state, expected",
    [
        (ExecutionState.INIT, False),
        (ExecutionState.PLANNING, False),
        (ExecutionState.ASKING, False),
        (ExecutionState.EDITING, False),
        (ExecutionState.TESTING, False),
        (ExecutionState.PR_OPEN, False),
        (ExecutionState.LANDED, True),
        (ExecutionState.DRY_RUN_COMPLETE, True),
        (ExecutionState.ABORTED, True),
        (ExecutionState.FAILED, True),
    ],
)
def test_is_terminal(state, expected):
    assert is_terminal(state) is expected


def test_terminal_states_have_no_outgoing_transitions():
    """LANDED/ABORTED/FAILED are sinks — once there, you can't
    transition out. Audit replayer relies on this to know when to
    stop reading events."""
    for state in TERMINAL_STATES:
        outgoing = [
            event for (s, event) in ALLOWED_TRANSITIONS.keys() if s == state
        ]
        assert outgoing == [], (
            f"{state.value} has outgoing transitions {outgoing!r}; "
            f"terminal states must be sinks"
        )


# ─── 3. Transitions: happy-path ────────────────────────────────────────


def test_init_starts_planning():
    assert next_state(ExecutionState.INIT, "start_planning") == ExecutionState.PLANNING


def test_planning_to_asking():
    assert next_state(ExecutionState.PLANNING, "plan_ready") == ExecutionState.ASKING


def test_asking_to_editing():
    assert next_state(ExecutionState.ASKING, "user_approved") == ExecutionState.EDITING


def test_editing_to_testing():
    assert next_state(ExecutionState.EDITING, "edits_applied") == ExecutionState.TESTING


def test_testing_to_pr_open():
    assert next_state(ExecutionState.TESTING, "tests_pass") == ExecutionState.PR_OPEN


def test_pr_open_to_landed():
    assert next_state(ExecutionState.PR_OPEN, "merge_recorded") == ExecutionState.LANDED


def test_full_happy_path_walk():
    """Walk through INIT → … → LANDED to make sure the table
    composes."""
    state = ExecutionState.INIT
    for event, expected in [
        ("start_planning", ExecutionState.PLANNING),
        ("plan_ready", ExecutionState.ASKING),
        ("user_approved", ExecutionState.EDITING),
        ("edits_applied", ExecutionState.TESTING),
        ("tests_pass", ExecutionState.PR_OPEN),
        ("merge_recorded", ExecutionState.LANDED),
    ]:
        state = next_state(state, event)
        assert state == expected
    assert is_terminal(state)


# ─── 4. Transitions: failure / abort branches ──────────────────────────


def test_planning_failure_to_failed():
    assert next_state(ExecutionState.PLANNING, "planner_error") == ExecutionState.FAILED


def test_asking_rejection_to_aborted():
    assert (
        next_state(ExecutionState.ASKING, "user_rejected") == ExecutionState.ABORTED
    )


def test_editing_error_to_failed():
    assert next_state(ExecutionState.EDITING, "edit_error") == ExecutionState.FAILED


def test_testing_regression_to_aborted():
    assert (
        next_state(ExecutionState.TESTING, "tests_regress") == ExecutionState.ABORTED
    )


def test_testing_runner_error_to_failed():
    assert (
        next_state(ExecutionState.TESTING, "test_runner_error")
        == ExecutionState.FAILED
    )


def test_pr_closed_unmerged_to_aborted():
    assert (
        next_state(ExecutionState.PR_OPEN, "pr_closed_unmerged")
        == ExecutionState.ABORTED
    )


def test_user_abort_from_each_non_terminal_state():
    """user_abort is the universal escape hatch — it must work from
    every non-terminal state."""
    for state in [
        ExecutionState.PLANNING,
        ExecutionState.ASKING,
        ExecutionState.EDITING,
        ExecutionState.TESTING,
        ExecutionState.PR_OPEN,
    ]:
        assert next_state(state, "user_abort") == ExecutionState.ABORTED


def test_user_abort_not_allowed_from_init():
    """INIT means we haven't even started planning — there's
    nothing to abort. The skill should refuse to start, not
    transition to ABORTED."""
    with pytest.raises(InvalidExecutionTransitionError):
        next_state(ExecutionState.INIT, "user_abort")


# ─── 5. Transitions: rejection of forbidden moves ──────────────────────


@pytest.mark.parametrize(
    "current, event",
    [
        (ExecutionState.INIT, "plan_ready"),  # skipping PLANNING
        (ExecutionState.INIT, "user_approved"),  # skipping ASKING
        (ExecutionState.PLANNING, "user_approved"),  # skipping ASKING
        (ExecutionState.ASKING, "edits_applied"),  # bypassing approve
        (ExecutionState.EDITING, "tests_pass"),  # skipping TESTING
        (ExecutionState.TESTING, "merge_recorded"),  # skipping PR_OPEN
        (ExecutionState.LANDED, "user_abort"),  # terminal
        (ExecutionState.ABORTED, "user_approved"),  # terminal
        (ExecutionState.FAILED, "start_planning"),  # terminal
    ],
)
def test_forbidden_transitions_raise(current, event):
    with pytest.raises(InvalidExecutionTransitionError) as exc:
        next_state(current, event)
    assert current.value in str(exc.value)


def test_unknown_event_lists_valid_options_in_error():
    """Error message must point the developer at the legal events
    so they don't have to read the source to find out what they
    can do next."""
    with pytest.raises(InvalidExecutionTransitionError) as exc:
        next_state(ExecutionState.INIT, "completely_made_up_event")
    msg = str(exc.value)
    assert "start_planning" in msg


# ─── 6. Table consistency ──────────────────────────────────────────────


def test_every_non_terminal_state_has_at_least_one_transition():
    """A non-terminal state with no outgoing transitions is a dead
    end — the executor can never leave it. Catch that immediately."""
    for state in ExecutionState:
        if state in TERMINAL_STATES:
            continue
        has_any = any(s == state for (s, _) in ALLOWED_TRANSITIONS)
        assert has_any, f"non-terminal state {state.value} has no outgoing transitions"


def test_every_transition_lands_in_known_state():
    """Sanity: ALLOWED_TRANSITIONS values must all be ExecutionState
    members. (Caught at load time by the type system, but assert at
    runtime too in case of dict mutation.)"""
    for ((src, _evt), dst) in ALLOWED_TRANSITIONS.items():
        assert isinstance(src, ExecutionState)
        assert isinstance(dst, ExecutionState)
