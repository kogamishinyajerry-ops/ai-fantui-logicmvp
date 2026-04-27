"""PR-merge gate — verify a PR carries a valid EXEC-id stamp +
matching audit JSON before allowing merge.

This is the machine-enforced version of "every truth-engine
change must come from the skill executor". The gate only fires on
PRs that touch files in PANEL_NAMESPACES; doc / CI / test-only
PRs pass through unchanged.

Verification chain (any link broken → block merge):

  1. PR diff includes a file inside one of PANEL_NAMESPACES
     → if no, skip gate (return ok=True, gate_required=False)
  2. PR body contains the EXEC-id stamp block
     (parse_exec_stamp returns dict)
  3. The audit file at `Audit:` path exists in the repo tree
  4. The audit JSON validates against AUDIT_SCHEMA_VERSION
  5. audit.proposal_id matches stamp.proposal
  6. audit.exec_id matches stamp.exec_id
  7. audit.state is PR_OPEN or LANDED (the only states a
     mergeable PR can reasonably be in)

The function returns a structured `GateCheckResult` so the CLI
can format failures as human-readable PR comments.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from well_harness.skill_executor.errors import AuditSchemaError
from well_harness.skill_executor.namespaces import namespace_for_path
from well_harness.skill_executor.pr_maker import parse_exec_stamp
from well_harness.skill_executor.schema import validate_audit_dict
from well_harness.skill_executor.states import ExecutionState


# States a mergeable PR can claim. INIT/PLANNING/ASKING/EDITING/
# TESTING are mid-flight; ABORTED/FAILED are terminal-bad.
_MERGEABLE_AUDIT_STATES = {
    ExecutionState.PR_OPEN.value,
    ExecutionState.LANDED.value,
}


@dataclasses.dataclass
class GateCheckResult:
    """Outcome of the PR audit gate. `ok=True` + `gate_required=False`
    means the PR doesn't touch truth-engine code so we waved it
    through; `ok=True` + `gate_required=True` means the audit
    chain validated. `ok=False` always implies `gate_required=True`."""

    ok: bool
    gate_required: bool
    reasons: list[str] = dataclasses.field(default_factory=list)
    matched_files: list[str] = dataclasses.field(default_factory=list)
    stamp: dict | None = None
    audit_path: str = ""


def check_pr_audit_compliance(
    *,
    pr_body: str,
    changed_files: list[str],
    repo_root: Path,
) -> GateCheckResult:
    """Run all 7 verification rules. Returns GateCheckResult.

    `pr_body` is the PR description text (whatever GitHub stored
    in the body field).
    `changed_files` is the list of paths touched by the PR diff,
    each relative to repo root with forward slashes.
    `repo_root` is where audit JSON paths are resolved against.
    """
    repo_root = Path(repo_root).resolve()

    # ── Step 1: does the PR touch any namespace file? ─────────────
    matched = [
        path for path in changed_files
        if namespace_for_path(path) is not None
    ]
    if not matched:
        return GateCheckResult(
            ok=True,
            gate_required=False,
            reasons=[
                "PR touches no PANEL_NAMESPACES files; gate not required"
            ],
            matched_files=[],
        )

    # ── Step 2: stamp present + parseable ─────────────────────────
    stamp = parse_exec_stamp(pr_body)
    if stamp is None:
        return GateCheckResult(
            ok=False,
            gate_required=True,
            matched_files=matched,
            reasons=[
                "PR body has no EXEC-id stamp; truth-engine changes "
                "must come from the skill executor. Expected a "
                "trailing block:\n"
                "    ---\n"
                "    Exec-Id: EXEC-...\n"
                "    Audit: .planning/skill_executions/EXEC-...json\n"
                "    Proposal: PROP-...\n"
                "    Skill-Executor-Version: 0.1.0"
            ],
        )

    # ── Step 3-7: validate audit chain ────────────────────────────
    audit_rel = stamp["audit"]
    audit_abs = (repo_root / audit_rel).resolve()
    # Path must stay under repo_root (defend against `Audit: /etc/passwd`)
    try:
        audit_abs.relative_to(repo_root)
    except ValueError:
        return GateCheckResult(
            ok=False,
            gate_required=True,
            matched_files=matched,
            stamp=stamp,
            audit_path=audit_rel,
            reasons=[
                f"Audit path {audit_rel!r} resolves outside repo root"
            ],
        )

    if not audit_abs.is_file():
        return GateCheckResult(
            ok=False,
            gate_required=True,
            matched_files=matched,
            stamp=stamp,
            audit_path=audit_rel,
            reasons=[
                f"Audit file not found in repo: {audit_rel}. The "
                f"executor must commit the audit JSON in the same "
                f"PR as the truth-engine change."
            ],
        )

    # The audit file must ALSO be among `changed_files` — otherwise
    # the PR could reference a pre-existing audit unrelated to
    # the current changes (replay attack).
    if audit_rel not in changed_files:
        return GateCheckResult(
            ok=False,
            gate_required=True,
            matched_files=matched,
            stamp=stamp,
            audit_path=audit_rel,
            reasons=[
                f"Audit file {audit_rel!r} exists in tree but is NOT "
                f"in this PR's changed files. The audit must be "
                f"committed in the same PR as the truth-engine change "
                f"(replay-attack defense)."
            ],
        )

    try:
        audit_data = json.loads(audit_abs.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return GateCheckResult(
            ok=False,
            gate_required=True,
            matched_files=matched,
            stamp=stamp,
            audit_path=audit_rel,
            reasons=[f"Audit file unreadable / not valid JSON: {exc}"],
        )

    try:
        validate_audit_dict(audit_data)
    except AuditSchemaError as exc:
        return GateCheckResult(
            ok=False,
            gate_required=True,
            matched_files=matched,
            stamp=stamp,
            audit_path=audit_rel,
            reasons=[f"Audit schema invalid: {exc}"],
        )

    # ── Cross-checks between stamp and audit ──────────────────────
    if audit_data["exec_id"] != stamp["exec_id"]:
        return GateCheckResult(
            ok=False,
            gate_required=True,
            matched_files=matched,
            stamp=stamp,
            audit_path=audit_rel,
            reasons=[
                f"Stamp exec_id ({stamp['exec_id']!r}) does not "
                f"match audit exec_id ({audit_data['exec_id']!r})"
            ],
        )
    if audit_data["proposal_id"] != stamp["proposal"]:
        return GateCheckResult(
            ok=False,
            gate_required=True,
            matched_files=matched,
            stamp=stamp,
            audit_path=audit_rel,
            reasons=[
                f"Stamp proposal ({stamp['proposal']!r}) does not "
                f"match audit proposal_id ({audit_data['proposal_id']!r})"
            ],
        )
    if audit_data["state"] not in _MERGEABLE_AUDIT_STATES:
        return GateCheckResult(
            ok=False,
            gate_required=True,
            matched_files=matched,
            stamp=stamp,
            audit_path=audit_rel,
            reasons=[
                f"Audit state {audit_data['state']!r} is not "
                f"mergeable. Must be one of "
                f"{sorted(_MERGEABLE_AUDIT_STATES)}; "
                f"FAILED/ABORTED/mid-flight states are blocked."
            ],
        )

    # All checks passed — backfill audits flagged but allowed (Q7(a)).
    notes: list[str] = ["all checks passed"]
    if audit_data.get("audit_source") == "backfill":
        notes.append(
            "audit_source=backfill — synthesized after-the-fact; "
            "reviewer should sanity-check the proposal lineage"
        )

    return GateCheckResult(
        ok=True,
        gate_required=True,
        matched_files=matched,
        stamp=stamp,
        audit_path=audit_rel,
        reasons=notes,
    )
