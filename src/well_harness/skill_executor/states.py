"""Skill executor state machine.

Eight states, three terminal. Transitions are the ONLY way an
execution moves forward — the audit log records every transition
with a timestamp, so a later reader can replay the run.

```
INIT
  └─ start_planning ──→ PLANNING
PLANNING
  ├─ plan_ready          ──→ ASKING
  ├─ governance_required ──→ GOVERNANCE_HOLD   (P49-02a)
  ├─ planner_error       ──→ FAILED
  └─ user_abort          ──→ ABORTED
GOVERNANCE_HOLD                                  (P49-02a)
  ├─ governance_approved ──→ ASKING
  ├─ governance_rejected ──→ ABORTED
  └─ user_abort          ──→ ABORTED
ASKING
  ├─ user_approved ──→ EDITING
  ├─ user_rejected ──→ ABORTED
  └─ user_abort    ──→ ABORTED
EDITING
  ├─ edits_applied ──→ TESTING
  ├─ edit_error    ──→ FAILED
  └─ user_abort    ──→ ABORTED
TESTING
  ├─ tests_pass        ──→ PR_OPEN
  ├─ tests_regress     ──→ ABORTED
  ├─ test_runner_error ──→ FAILED
  └─ user_abort        ──→ ABORTED
PR_OPEN
  ├─ merge_recorded     ──→ LANDED
  ├─ pr_closed_unmerged ──→ ABORTED
  └─ user_abort         ──→ ABORTED
LANDED   (terminal)
ABORTED  (terminal)
FAILED   (terminal)
```
"""

from __future__ import annotations

import enum

from well_harness.skill_executor.errors import InvalidExecutionTransitionError


class ExecutionState(str, enum.Enum):
    """Where in the lifecycle an execution currently sits.
    String-valued so it serializes cleanly into JSON without a
    custom encoder."""

    INIT = "INIT"
    PLANNING = "PLANNING"
    # P49-02a: human-review pause between PLANNING and ASKING.
    # Entered when evaluate_governance(proposal, plan) returns
    # required=True; exits via governance_approved (→ ASKING) or
    # governance_rejected/user_abort (→ ABORTED).
    GOVERNANCE_HOLD = "GOVERNANCE_HOLD"
    ASKING = "ASKING"
    EDITING = "EDITING"
    TESTING = "TESTING"
    PR_OPEN = "PR_OPEN"
    LANDED = "LANDED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"


TERMINAL_STATES: frozenset[ExecutionState] = frozenset(
    {ExecutionState.LANDED, ExecutionState.ABORTED, ExecutionState.FAILED}
)


# event_name → (allowed_from, target_state)
# Each entry says: when event X fires while we're in state Y, we
# transition to state Z. Anything not in this table is rejected.
ALLOWED_TRANSITIONS: dict[tuple[ExecutionState, str], ExecutionState] = {
    (ExecutionState.INIT, "start_planning"): ExecutionState.PLANNING,
    (ExecutionState.PLANNING, "plan_ready"): ExecutionState.ASKING,
    (ExecutionState.PLANNING, "planner_error"): ExecutionState.FAILED,
    (ExecutionState.PLANNING, "user_abort"): ExecutionState.ABORTED,
    # P49-02a governance gate
    (ExecutionState.PLANNING, "governance_required"): ExecutionState.GOVERNANCE_HOLD,
    (ExecutionState.GOVERNANCE_HOLD, "governance_approved"): ExecutionState.ASKING,
    (ExecutionState.GOVERNANCE_HOLD, "governance_rejected"): ExecutionState.ABORTED,
    (ExecutionState.GOVERNANCE_HOLD, "user_abort"): ExecutionState.ABORTED,
    (ExecutionState.ASKING, "user_approved"): ExecutionState.EDITING,
    (ExecutionState.ASKING, "user_rejected"): ExecutionState.ABORTED,
    (ExecutionState.ASKING, "user_abort"): ExecutionState.ABORTED,
    (ExecutionState.EDITING, "edits_applied"): ExecutionState.TESTING,
    (ExecutionState.EDITING, "edit_error"): ExecutionState.FAILED,
    (ExecutionState.EDITING, "user_abort"): ExecutionState.ABORTED,
    (ExecutionState.TESTING, "tests_pass"): ExecutionState.PR_OPEN,
    (ExecutionState.TESTING, "tests_regress"): ExecutionState.ABORTED,
    (ExecutionState.TESTING, "test_runner_error"): ExecutionState.FAILED,
    (ExecutionState.TESTING, "user_abort"): ExecutionState.ABORTED,
    (ExecutionState.PR_OPEN, "merge_recorded"): ExecutionState.LANDED,
    (ExecutionState.PR_OPEN, "pr_closed_unmerged"): ExecutionState.ABORTED,
    (ExecutionState.PR_OPEN, "user_abort"): ExecutionState.ABORTED,
}


def next_state(current: ExecutionState, event: str) -> ExecutionState:
    """Return the state that results from `event` firing while in
    `current`. Raises InvalidExecutionTransitionError if the
    transition isn't permitted.

    The state machine is the single source of truth for "what can
    happen next" — even the audit writer enforces it, so a corrupt
    audit can never claim a forbidden transition (the writer would
    have refused to record it).
    """
    key = (current, event)
    if key not in ALLOWED_TRANSITIONS:
        raise InvalidExecutionTransitionError(
            f"no transition for ({current.value}, {event!r}); "
            f"valid events from {current.value}: "
            f"{sorted(e for (s, e) in ALLOWED_TRANSITIONS if s == current)}"
        )
    return ALLOWED_TRANSITIONS[key]


def is_terminal(state: ExecutionState) -> bool:
    """LANDED / ABORTED / FAILED are terminal — no transitions out."""
    return state in TERMINAL_STATES
