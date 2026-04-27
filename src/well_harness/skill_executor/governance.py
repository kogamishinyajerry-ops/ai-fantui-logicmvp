"""Governance gate — pause execution before EDITING when a plan
matches a sensitive criterion, and require an explicit human
approval to proceed (P49-02a).

Why: P48-01..P50-12 made the executor reliable, observable, and
alertable. The next safety boundary is **what executions should
even start**. Right now any ACCEPTED proposal that planned cleanly
sails through to EDITING. That's fine for low-risk modify-on-
existing-logic work; it's not fine when the plan touches the
logic_truth namespace (the safety contract surface) or when the
planner self-assessed any namespace as "red" risk.

This module decides whether a (proposal, plan) pair needs human
review. The orchestrator wires the verdict in: required → state
machine pauses at GOVERNANCE_HOLD until an explicit approval
signal arrives or a reject/cancel signal aborts.

Default rules (all OR'd; any match → required):
  - `logic_truth_namespace` — affected_namespaces contains
    "logic_truth" (the truth-engine red-line surface)
  - `red_risk` — risk_assessment[ns] == "red" for any namespace
  - `expand_kind` — kind == "expand" (creating new control logic
    rather than modifying existing — bigger blast radius)

Each match contributes a reason + rule_id so the workbench can
explain "this needs review because X". A reviewer who has the
context can then approve or reject knowingly, rather than the
gate being a black box.

What this is NOT (deferred):
  - Per-reviewer auth. The first slice trusts whoever can write
    the approval signal file. Future P49-02c could add an actor
    field + audit-trail.
  - Configurable rule sets per environment. Default rules are
    hardcoded; an env override can ADD more required namespaces
    but the rule SHAPES are fixed.
  - Dry-run preview. The plan is already audited; reviewer reads
    the audit JSON. A future UI slice (P49-02b) can render it.

Pure of IO. Caller (orchestrator) translates the verdict into
state transitions + signal-file polling.
"""

from __future__ import annotations

import dataclasses
import os


# Env override: a comma-separated list of additional namespaces
# whose presence in `affected_namespaces` triggers the gate. Adds
# to the default {"logic_truth"} set; doesn't replace it.
EXTRA_GUARDED_NAMESPACES_ENV: str = "WORKBENCH_GOVERNANCE_EXTRA_NAMESPACES"
DEFAULT_GUARDED_NAMESPACES: frozenset[str] = frozenset({"logic_truth"})


# Master kill switch. When set to "0" / "false" / "off" the
# evaluator returns required=False unconditionally. Useful for:
#   - test suites that exercise the executor pipeline but
#     don't want to manage approval signals
#   - emergency production override (the human running the
#     executor wants to bypass the gate for one run; they get
#     audited via the env-set actor anyway)
# Default (unset / "1" / "true" / "on") leaves the gate active.
GOVERNANCE_ENABLED_ENV: str = "WORKBENCH_GOVERNANCE_ENABLED"


def _is_disabled_via_env() -> bool:
    raw = os.environ.get(GOVERNANCE_ENABLED_ENV)
    if raw is None:
        return False
    normalized = raw.strip().lower()
    return normalized in {"0", "false", "off", "no"}


# Rule identifiers — string-stable so audit logs and tests can
# reference them without importing constants.
RULE_LOGIC_TRUTH_NAMESPACE: str = "logic_truth_namespace"
RULE_RED_RISK: str = "red_risk"
RULE_EXPAND_KIND: str = "expand_kind"


@dataclasses.dataclass
class GovernanceMatch:
    """One rule that fired. The orchestrator stamps these into the
    audit log so a reviewer can see exactly which criterion held
    up the execution."""

    rule_id: str
    reason: str
    detail: str

    def to_json(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "reason": self.reason,
            "detail": self.detail,
        }


@dataclasses.dataclass
class GovernanceVerdict:
    """`required` is the only field the orchestrator branches on;
    `matches` carries the rule fingerprints for the audit log."""

    required: bool
    matches: list[GovernanceMatch]

    def to_json(self) -> dict:
        return {
            "required": self.required,
            "matches": [m.to_json() for m in self.matches],
        }

    def reasons(self) -> list[str]:
        """Human-readable reason summaries — each match contributes
        one line. Useful for the workbench card."""
        return [m.reason for m in self.matches]


def _resolve_guarded_namespaces() -> frozenset[str]:
    """Default {"logic_truth"} plus any env-supplied additions.
    The env value is a comma-separated list; whitespace + empties
    are stripped."""
    extras_raw = os.environ.get(EXTRA_GUARDED_NAMESPACES_ENV, "")
    extras = {
        ns.strip() for ns in extras_raw.split(",") if ns.strip()
    }
    return frozenset(DEFAULT_GUARDED_NAMESPACES | extras)


def evaluate_governance(
    *,
    proposal: object,
    plan: object,
) -> GovernanceVerdict:
    """Decide whether this (proposal, plan) pair requires human
    review before EDITING. `proposal` and `plan` are passed as
    `object` and read by attribute to avoid circular imports.

    Returns a verdict; the orchestrator decides what to do with it.
    Empty matches → required=False (path is clear).
    """
    # Master kill switch — short-circuits before any rule fires
    # so disabled deployments don't pay the rule-evaluation cost
    # and the verdict is unambiguous in the audit log.
    if _is_disabled_via_env():
        return GovernanceVerdict(required=False, matches=[])
    matches: list[GovernanceMatch] = []
    guarded = _resolve_guarded_namespaces()

    # ─── Rule 1: guarded namespace touched ────────────────────────
    affected = list(getattr(plan, "affected_namespaces", []) or [])
    crossed = [ns for ns in affected if ns in guarded]
    for ns in crossed:
        matches.append(
            GovernanceMatch(
                rule_id=RULE_LOGIC_TRUTH_NAMESPACE,
                reason=(
                    f"plan touches guarded namespace {ns!r} — "
                    "human review required"
                ),
                detail=ns,
            )
        )

    # ─── Rule 2: any namespace self-assessed as red ────────────────
    risk = dict(getattr(plan, "risk_assessment", {}) or {})
    red_namespaces = sorted(
        ns for ns, level in risk.items()
        if str(level).strip().lower() == "red"
    )
    for ns in red_namespaces:
        matches.append(
            GovernanceMatch(
                rule_id=RULE_RED_RISK,
                reason=(
                    f"planner self-assessed risk in {ns!r} as RED"
                ),
                detail=ns,
            )
        )

    # ─── Rule 3: 'expand' kind creates new logic ───────────────────
    # ExecutionKind / proposal kind is sometimes a string, sometimes
    # an enum value with .value attribute. Read both shapes.
    kind = getattr(proposal, "kind", None)
    if kind is None:
        kind_str = ""
    elif hasattr(kind, "value"):
        kind_str = str(kind.value)
    else:
        kind_str = str(kind)
    if kind_str.strip().lower() == "expand":
        matches.append(
            GovernanceMatch(
                rule_id=RULE_EXPAND_KIND,
                reason=(
                    "proposal kind is 'expand' (new logic, not "
                    "modify) — human review required"
                ),
                detail=kind_str,
            )
        )

    return GovernanceVerdict(
        required=len(matches) > 0,
        matches=matches,
    )
