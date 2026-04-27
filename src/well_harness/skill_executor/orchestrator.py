"""Main pipeline — string P48-01..03 together with git + PR.

The orchestrator's job is to walk the state machine
(INIT → PLANNING → ASKING → EDITING → TESTING → PR_OPEN) writing
audit deltas at each transition, recovering cleanly from each
failure mode the lower layers expose.

Every transition is mediated by `next_state()` so a corrupt audit
can never claim a forbidden move; every failure path either
reverts file edits (if any were applied) or transitions to a
terminal state with `abort_reason` populated; every audit write
goes through `write_audit()` which validates schema before
persisting.

Caller controls these injection points:
  - `approval_callback(audit, ask)` — called when state enters
    ASKING. Returns AskResponse. P48-04 default is "raise — must
    be supplied"; tests pass a stub that auto-approves.
  - `auto_approve` — convenience: if True, skips approval_callback
    and synthesizes APPROVED. Test/CI use only.
  - `skip_pr` — don't open a PR (test mode). Pipeline still
    runs apply + test gate + commit, just no `gh pr create`.
  - `request_post_for_llm` — passed through to the planner so
    tests can canned LLM responses without a real network call.
  - `git_runner` / `gh_runner` — pass-through for git_ops /
    pr_maker. Production = None (default subprocess); tests inject.

Returns the final ExecutionRecord. The caller decides what to do
with non-LANDED terminal states (PR_OPEN means "PR is open, awaiting
review/merge"; LANDED requires the /landed callback after merge).
"""

from __future__ import annotations

import dataclasses
import os
import socket
import time
from pathlib import Path
from typing import Any, Callable

from well_harness.skill_executor.applier import (
    ApplyError,
    ApplyResult,
    apply_edits,
    revert_edits,
)
from well_harness.skill_executor.audit import new_execution_id, write_audit
from well_harness.skill_executor.errors import SkillExecutorError
from well_harness.skill_executor.git_ops import (
    GitError,
    commit_files,
    create_branch,
    push_branch,
)
from well_harness.skill_executor.llm_client import LLMUnavailableError
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    Ask,
    AskResponse,
    AuditSource,
    ExecutionEvent,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
    now_iso,
)
from well_harness.skill_executor.gate import check_test_gate
from well_harness.skill_executor.planner import PlannerError, plan_from_brief
from well_harness.skill_executor.pr_maker import (
    PRDetails,
    PRMakerError,
    build_exec_stamp,
    open_pr,
)
from well_harness.skill_executor.proposal_io import (
    ProposalIOError,
    load_brief,
    load_proposal,
)
from well_harness.skill_executor.states import (
    ALLOWED_TRANSITIONS,
    ExecutionState,
    is_terminal,
    next_state,
)
from well_harness.skill_executor.test_runner import (
    TestRunnerError,
    run_tests,
)
from well_harness.skill_executor.workbench_polling import (
    ExecutionCancelled,
    check_cancel,
    read_and_clear_governance,
)
from well_harness.skill_executor.governance import (
    GovernanceVerdict,
    evaluate_governance,
)


EXECUTOR_VERSION: str = "0.1.0"


class OrchestratorError(SkillExecutorError):
    """Wraps any failure that escapes the pipeline. The audit
    record is the source of truth for what happened; this just
    surfaces the most-recent error to the caller."""


class GovernanceTimeoutError(SkillExecutorError):
    """P49-02a: the governance gate waited longer than
    governance_timeout_sec without seeing an approve/reject
    signal. Treated as an abort — better to bail than to silently
    proceed past a sensitive gate."""


@dataclasses.dataclass
class OrchestratorResult:
    """Final outcome — the audit record after pipeline finished
    (terminal state) or returned mid-flight (PR_OPEN). `error` is
    set if the pipeline raised; the caller can inspect it without
    re-catching."""

    record: ExecutionRecord
    error: Exception | None = None


# Type aliases — the inject-able hooks
ApprovalCallback = Callable[[ExecutionRecord, Ask], AskResponse]


def execute_proposal(
    *,
    proposal_id: str,
    repo_root: Path,
    audit_dir: Path | None = None,
    approval_callback: ApprovalCallback | None = None,
    auto_approve: bool = False,
    skip_pr: bool = False,
    skip_push: bool = False,
    api_key_override: str | None = None,
    request_post_for_llm: Any = None,
    git_runner: Any = None,
    gh_runner: Any = None,
    base_branch: str = "main",
    pr_title_override: str | None = None,
    # P50-03 (2026-04-27): planner retry on transient failures.
    # max_planner_retries is the number of EXTRA attempts after the
    # first one — so default=2 means up to 3 total attempts. Set
    # to 0 to disable retries entirely (legacy behavior).
    max_planner_retries: int = 2,
    planner_retry_delay_sec: float = 2.0,
    sleep_fn: Callable[[float], None] | None = None,
    # P49-02a: governance gate. `governance_poll_fn` is the
    # injection point for tests — signature
    # (audit_dir, exec_id) → ("approved" | "rejected", payload) | None.
    # Default polls workbench_polling.read_and_clear_governance with
    # `governance_poll_interval_sec` between checks until
    # `governance_timeout_sec` elapses (raises GovernanceTimeoutError).
    # Tests pass a fake to short-circuit.
    governance_poll_fn: Callable[..., Any] | None = None,
    governance_poll_interval_sec: float = 1.0,
    governance_timeout_sec: float = 3600.0,
    # P49-04: dry-run mode. When True, the pipeline runs through
    # PLANNING/EDITING/TESTING but stops short of commit/push/PR.
    # The captured diff is stored in record.dry_run_diff and the
    # working tree is reverted; the audit terminates at
    # DRY_RUN_COMPLETE so a reviewer can preview the change before
    # approving it for real. Honors the same governance gate as
    # live runs — a reviewer might want to see the diff exactly
    # because it touches a sensitive namespace.
    dry_run: bool = False,
    # `None` means "follow auto_approve" — auto_approve already
    # signals "skip human-in-the-loop", and governance is just
    # another HITL gate. Tests + scripted runs that pass
    # auto_approve=True don't have to ALSO remember to bypass
    # governance. Pass an explicit True/False here only when you
    # want governance behavior to differ from ASKING behavior.
    auto_approve_governance: bool | None = None,
) -> OrchestratorResult:
    """Walk a proposal through the full executor pipeline.

    See module docstring for the contract. Returns
    OrchestratorResult; never raises out of the happy path. If a
    fatal error occurs, it's recorded on result.error AND the
    audit's terminal state encodes it.

    Why not raise: callers (CLI, future REST endpoint) want the
    audit even on failure to surface to the user. Raising forces
    every caller to write the same try/except wrapper.
    """
    repo_root = Path(repo_root).resolve()
    if audit_dir is None:
        # Default to .planning/skill_executions/ under the repo
        # root we're operating on. Tests pass a tmp_path override.
        audit_dir = repo_root / ".planning" / "skill_executions"
    audit_dir.mkdir(parents=True, exist_ok=True)
    # P48-06: pin the env var for the duration of this run so any
    # other module reading audit_dir() (e.g. the demo_server when
    # the CLI runs alongside it) sees the same directory.
    os.environ["WORKBENCH_SKILL_EXECUTIONS_DIR"] = str(audit_dir)

    # ── Step 0: load proposal + brief ────────────────────────────
    try:
        proposal = load_proposal(proposal_id, repo_root=repo_root)
        brief = load_brief(proposal_id, repo_root=repo_root)
    except ProposalIOError as exc:
        # Can't even build an audit without a proposal; surface
        # to caller without persisting anything.
        # (Future: maybe write a "rejected at intake" audit.
        # For now, fail fast.)
        raise OrchestratorError(f"intake failed: {exc}") from exc

    # ── Step 1: build initial audit record ───────────────────────
    record = ExecutionRecord(
        exec_id=new_execution_id(),
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id=proposal_id,
        kind=ExecutionKind(proposal["kind"]),
        audit_source=AuditSource.LIVE,
        started_at=now_iso(),
        executor_version=EXECUTOR_VERSION,
        executor_host=socket.gethostname(),
        executor_user=os.environ.get("USER") or "",
        state=ExecutionState.INIT.value,
        dry_run=bool(dry_run),
    )
    _push_event(
        record,
        kind="init",
        note=(
            f"proposal {proposal_id}"
            + (" [DRY-RUN]" if dry_run else "")
        ),
    )
    _persist(record, audit_dir)

    applied: ApplyResult | None = None

    sleep_actual = sleep_fn or _default_sleep

    try:
        # ── Step 2: INIT → PLANNING + run planner ────────────────
        _transition(record, "start_planning", audit_dir)

        # P50-03: retry the planner on transient failures
        # (LLMUnavailableError = 5xx / network / timeout). Schema
        # / validation errors (PlannerError) are NOT retried —
        # the same prompt won't produce different output.
        plan, planner_exc = _run_planner_with_retry(
            record=record,
            audit_dir=audit_dir,
            proposal=proposal,
            brief=brief,
            api_key_override=api_key_override,
            request_post_for_llm=request_post_for_llm,
            max_retries=max_planner_retries,
            base_delay_sec=planner_retry_delay_sec,
            sleep_fn=sleep_actual,
        )
        if planner_exc is not None:
            record.plan = _planner_failure_plan(planner_exc)
            record.abort_reason = f"planner: {planner_exc}"
            _push_event(
                record, kind="planner_error",
                note=str(planner_exc)[:200],
            )
            _transition(record, "planner_error", audit_dir)
            _finish(record, audit_dir)
            return OrchestratorResult(record=record, error=planner_exc)
        record.plan = plan
        record.llm_backend = plan.llm_backend
        _push_event(record, kind="planner_invocation", note="plan ready")
        _persist(record, audit_dir)

        # P49-01c phase-boundary cancel check (post-PLANNING).
        # If a reviewer hit Cancel while the LLM was thinking, abort
        # before showing them an ASKING card they don't want.
        if _check_cancel_and_abort(record, audit_dir, applied=None):
            return OrchestratorResult(record=record)

        # ── Step 2.5 (P49-02a): governance gate ─────────────────
        # After the planner produces a concrete plan but before any
        # ASKING UX, evaluate whether the (proposal, plan) pair
        # crosses a sensitive boundary (logic_truth namespace, red
        # risk, or expand kind). If so, transition to
        # GOVERNANCE_HOLD and wait for an approve/reject signal.
        # Cancel + timeout also abort the gate.
        verdict = evaluate_governance(proposal=proposal, plan=plan)
        gate_taken = False
        # Resolve the auto-approve-governance default: None mirrors
        # auto_approve so callers that opted into the legacy
        # "skip ASKING" flag also bypass governance for free.
        effective_auto_gov = (
            auto_approve_governance
            if auto_approve_governance is not None
            else auto_approve
        )
        if verdict.required:
            governance_outcome = _run_governance_gate(
                record=record,
                audit_dir=audit_dir,
                verdict=verdict,
                poll_fn=governance_poll_fn,
                poll_interval_sec=governance_poll_interval_sec,
                timeout_sec=governance_timeout_sec,
                auto_approve=effective_auto_gov,
                sleep_fn=sleep_actual,
            )
            if governance_outcome != "approved":
                # Aborted — _run_governance_gate already updated
                # state, abort_reason, and finished_at.
                return OrchestratorResult(record=record)
            # On approved: governance_approved already transitioned
            # GOVERNANCE_HOLD → ASKING. Skip the redundant
            # plan_ready transition below.
            gate_taken = True

        # ── Step 3: PLANNING → ASKING + wait for approval ────────
        if not gate_taken:
            _transition(record, "plan_ready", audit_dir)
        ask = Ask(
            ask_id=_new_ask_id(record.exec_id),
            question=_ask_question_for(plan),
            shown_in_workbench_at=now_iso(),
        )
        record.asks.append(ask)
        _persist(record, audit_dir)

        if auto_approve:
            ask.user_response = AskResponse.APPROVED
            ask.user_responded_at = now_iso()
            ask.user_actor = "auto-approve-mode"
            ask.note = "skip_ask=true via execute_proposal"
        else:
            if approval_callback is None:
                raise OrchestratorError(
                    "approval_callback is None and auto_approve is False; "
                    "the orchestrator can't advance from ASKING"
                )
            try:
                response = approval_callback(record, ask)
            except ExecutionCancelled as cancel_exc:
                # P49-01c: cancel signal during ASKING. Distinct from
                # REJECTED — we record actor + note explicitly so the
                # audit log distinguishes "I disapprove the plan"
                # from "stop the executor right now".
                ask.user_response = None
                ask.user_actor = cancel_exc.actor
                ask.note = f"cancelled: {cancel_exc.note}".strip(": ")
                _persist(record, audit_dir)
                _abort_with_cancel(
                    record, audit_dir, cancel_exc, applied=None,
                )
                return OrchestratorResult(record=record)
            ask.user_response = response
            ask.user_responded_at = now_iso()
        _persist(record, audit_dir)

        if ask.user_response != AskResponse.APPROVED:
            event = (
                "user_rejected"
                if ask.user_response == AskResponse.REJECTED
                else "user_abort"
            )
            _push_event(
                record,
                kind=event,
                note=(ask.note or ""),
            )
            _transition(record, event, audit_dir)
            record.abort_reason = (
                f"user response: {ask.user_response.value}"
                if ask.user_response
                else "user abort"
            )
            _finish(record, audit_dir)
            return OrchestratorResult(record=record)

        # ── Step 4: ASKING → EDITING + apply ────────────────────
        _transition(record, "user_approved", audit_dir)

        # Capture baseline tests BEFORE touching files. If pytest
        # is broken to start with, fail loudly here, not after we
        # mess with the working tree.
        try:
            record.tests_before = run_tests(repo_root=repo_root)
        except TestRunnerError as exc:
            record.abort_reason = f"baseline test runner: {exc}"
            _push_event(record, kind="test_runner_error", note=str(exc))
            _transition(record, "edit_error", audit_dir)
            _finish(record, audit_dir)
            return OrchestratorResult(record=record, error=exc)
        _persist(record, audit_dir)

        try:
            applied = apply_edits(plan.file_edits, repo_root=repo_root)
        except ApplyError as exc:
            record.abort_reason = f"apply: {exc}"
            _push_event(record, kind="edit_error", note=str(exc))
            _transition(record, "edit_error", audit_dir)
            _finish(record, audit_dir)
            return OrchestratorResult(record=record, error=exc)
        _push_event(
            record,
            kind="edit_apply",
            note=f"applied {len(applied.applied)} edits",
        )

        # P49-01c phase-boundary cancel check (post-EDITING, pre-TESTING).
        # Edits ARE applied at this point — we revert before aborting
        # so the working tree is clean.
        if _check_cancel_and_abort(record, audit_dir, applied=applied):
            return OrchestratorResult(record=record)

        # ── Step 5: EDITING → TESTING + run + gate ─────────────
        _transition(record, "edits_applied", audit_dir)

        try:
            record.tests_after = run_tests(repo_root=repo_root)
        except TestRunnerError as exc:
            revert_edits(applied)
            record.abort_reason = f"after test runner: {exc}"
            _push_event(record, kind="test_runner_error", note=str(exc))
            _transition(record, "test_runner_error", audit_dir)
            _finish(record, audit_dir)
            return OrchestratorResult(record=record, error=exc)
        _push_event(record, kind="test_run", note="tests_after captured")
        _persist(record, audit_dir)

        gate = check_test_gate(
            before=record.tests_before, after=record.tests_after
        )
        if not gate.ok:
            revert_edits(applied)
            record.abort_reason = f"test gate: {gate.reason}"
            _push_event(record, kind="tests_regress", note=gate.reason)
            _transition(record, "tests_regress", audit_dir)
            _finish(record, audit_dir)
            return OrchestratorResult(record=record)

        # P49-01c phase-boundary cancel check (post-TESTING, pre-PR).
        # Last point we can cleanly bail without leaving a stale PR.
        if _check_cancel_and_abort(record, audit_dir, applied=applied):
            return OrchestratorResult(record=record)

        # ── Step 5.5 (P49-04): dry-run terminates here ─────────
        # Pipeline ran end-to-end through TESTING. Capture the
        # working-tree diff BEFORE revert_edits puts the files
        # back, stash it on the audit, then transition straight
        # to DRY_RUN_COMPLETE without touching git further.
        # The reviewer reads dry_run_diff to preview what the
        # real run would have committed.
        if dry_run:
            try:
                record.dry_run_diff = _capture_dry_run_diff(
                    repo_root=repo_root,
                    git_runner=git_runner,
                )
            except Exception as exc:  # noqa: BLE001
                # Diff capture is best-effort — if it fails we
                # still want to revert + report. Empty diff is
                # the worst case; not an abort.
                _push_event(
                    record, kind="dry_run_diff_error",
                    note=str(exc)[:200],
                )
                record.dry_run_diff = ""
            revert_edits(applied)
            _push_event(
                record, kind="dry_run_complete",
                note=(
                    f"diff length: {len(record.dry_run_diff)} bytes"
                ),
            )
            _transition(record, "dry_run_complete", audit_dir)
            _finish(record, audit_dir)
            return OrchestratorResult(record=record)

        # ── Step 6: TESTING → PR_OPEN + git + PR ───────────────
        _transition(record, "tests_pass", audit_dir)

        # Branch + commit happen even when skip_pr=True so the
        # full audit shows what would have shipped. skip_push is
        # the test-only escape hatch for "don't actually push".
        try:
            branch_name = _branch_name_for(
                proposal_id, record.exec_id, kind=record.kind,
            )
            create_branch(
                repo_root=repo_root,
                branch_name=branch_name,
                git_runner=git_runner,
            )
            record.branch = branch_name

            commit_msg = _build_commit_message(
                proposal=proposal, plan=plan, record=record
            )
            commit_paths = sorted({e.path for e in plan.file_edits} | {
                e.path for e in plan.test_changes
            })
            commit = commit_files(
                repo_root=repo_root,
                files=commit_paths,
                message=commit_msg,
                git_runner=git_runner,
            )
            record.commits.append(commit.sha)
            _push_event(
                record,
                kind="git_commit",
                note=f"{commit.sha[:8]} {commit.message_first_line[:60]}",
            )
            _persist(record, audit_dir)

            if not skip_push:
                push_branch(
                    repo_root=repo_root,
                    branch_name=branch_name,
                    git_runner=git_runner,
                )
                _push_event(record, kind="git_push", note=f"pushed {branch_name}")
                _persist(record, audit_dir)
        except GitError as exc:
            # Edits already applied — keep them; user can rescue
            # manually. But mark FAILED in audit so the gate refuses
            # any orphaned PR built on top of this exec_id.
            record.abort_reason = f"git: {exc}"
            _push_event(record, kind="git_error", note=str(exc))
            # The state machine doesn't have an EDITING→FAILED
            # transition through git error — but we entered
            # TESTING/PR_OPEN before reaching git. Use
            # pr_closed_unmerged event with explanatory note.
            try:
                _transition(record, "pr_closed_unmerged", audit_dir)
            except Exception:
                # If we somehow aren't in PR_OPEN yet, force-mark
                # FAILED via direct mutation. (next_state would
                # have been called at TESTING→PR_OPEN already.)
                record.state = ExecutionState.FAILED.value
                _persist(record, audit_dir)
            _finish(record, audit_dir)
            return OrchestratorResult(record=record, error=exc)

        if skip_pr:
            _push_event(record, kind="pr_skip", note="skip_pr=true")
            _finish(record, audit_dir)
            return OrchestratorResult(record=record)

        try:
            pr = open_pr(
                repo_root=repo_root,
                title=pr_title_override or _pr_title_for(proposal, plan),
                body=_pr_body_for(
                    proposal=proposal,
                    plan=plan,
                    record=record,
                    audit_dir=audit_dir,
                ),
                head=record.branch,
                base=base_branch,
                gh_runner=gh_runner,
            )
            record.pr_url = pr.url
            _push_event(record, kind="pr_open", note=pr.url)
            _persist(record, audit_dir)
        except PRMakerError as exc:
            record.abort_reason = f"gh: {exc}"
            _push_event(record, kind="pr_error", note=str(exc))
            try:
                _transition(record, "pr_closed_unmerged", audit_dir)
            except Exception:
                record.state = ExecutionState.FAILED.value
                _persist(record, audit_dir)
            _finish(record, audit_dir)
            return OrchestratorResult(record=record, error=exc)

        # PR_OPEN is a non-terminal state — we leave it here. The
        # /landed POST after merge transitions to LANDED in a later
        # call (P48-06 wires that to a CLI flag or workbench
        # webhook).
        _persist(record, audit_dir)
        return OrchestratorResult(record=record)

    except Exception as exc:  # noqa: BLE001 — last-resort handler
        # Never let an exception escape the pipeline without
        # leaving the audit in a sensible terminal state. Two
        # cases:
        #   - we already transitioned to a terminal state above
        #   - we didn't, and need to force-mark FAILED here
        if applied is not None:
            try:
                revert_edits(applied)
            except Exception:
                pass
        record.abort_reason = (
            record.abort_reason or f"unhandled: {type(exc).__name__}: {exc}"
        )
        if not is_terminal(ExecutionState(record.state)):
            record.state = ExecutionState.FAILED.value
        _push_event(record, kind="orchestrator_error", note=str(exc)[:200])
        _finish(record, audit_dir)
        return OrchestratorResult(record=record, error=exc)


# ─── Helpers ──────────────────────────────────────────────────────────


def _default_sleep(seconds: float) -> None:
    import time
    time.sleep(seconds)


def _run_planner_with_retry(
    *,
    record: ExecutionRecord,
    audit_dir: Path,
    proposal: dict,
    brief: str,
    api_key_override: str | None,
    request_post_for_llm: Any,
    max_retries: int,
    base_delay_sec: float,
    sleep_fn: Callable[[float], None],
) -> tuple[PlannedChange | None, Exception | None]:
    """Run plan_from_brief with retry-on-transient. Returns
    (plan, None) on success or (None, exc) on terminal failure.

    Retry policy (P50-03):
      - LLMUnavailableError → transient, retry up to max_retries
        with exponential backoff (base_delay * 2^attempt, capped
        at 60s)
      - PlannerError → permanent, no retry (schema / validation
        errors don't get better with more attempts)
      - Any other exception → bubble up to the orchestrator's
        outer handler

    Each retry attempt is logged as a `planner_retry` audit
    event so reviewers can see how many tries it took.
    """
    attempt = 0
    while True:
        try:
            plan = plan_from_brief(
                proposal_record=proposal,
                brief_text=brief,
                api_key=api_key_override,
                request_post=request_post_for_llm,
            )
            if attempt > 0:
                _push_event(
                    record,
                    kind="planner_retry_success",
                    note=f"recovered after {attempt} retries",
                )
                _persist(record, audit_dir)
            return plan, None
        except LLMUnavailableError as exc:
            if attempt >= max_retries:
                # Exhausted — bubble back to caller for terminal handling
                return None, exc
            delay = min(60.0, base_delay_sec * (2 ** attempt))
            attempt += 1
            _push_event(
                record,
                kind="planner_retry",
                note=(
                    f"attempt={attempt}/{max_retries} "
                    f"delay={delay}s reason={exc}"
                )[:200],
            )
            _persist(record, audit_dir)
            sleep_fn(delay)
            continue
        except PlannerError as exc:
            # Schema/validation error — same prompt won't fix it
            return None, exc


def _run_governance_gate(
    *,
    record: ExecutionRecord,
    audit_dir: Path,
    verdict: GovernanceVerdict,
    poll_fn: Callable[..., Any] | None,
    poll_interval_sec: float,
    timeout_sec: float,
    auto_approve: bool,
    sleep_fn: Callable[[float], None],
) -> str:
    """Drive the GOVERNANCE_HOLD state. Returns one of:
      "approved" — caller should continue to ASKING
      "rejected" — caller should bail; record is already terminal
      "cancelled" — caller should bail; record is already terminal
      "timeout"  — caller should bail; record is already terminal

    Mutates `record` (state, governance_review, events, abort_reason,
    finished_at) and persists via _persist/_finish so the audit
    reflects every transition the gate took.

    Polls the file-based approve/reject signals (P49-01-style IPC)
    every `poll_interval_sec`. Cancel signal also aborts. If
    `timeout_sec` elapses with no decision, the run aborts —
    silent advance past a sensitive gate is unsafe.
    """
    # Move into GOVERNANCE_HOLD and stamp the verdict so a reviewer
    # can see exactly which rules fired.
    review_payload = dict(verdict.to_json())
    review_payload.update({
        "decision": None,
        "decided_at": "",
        "decided_by": "",
        "decision_note": "",
    })
    record.governance_review = review_payload
    _push_event(
        record,
        kind="governance_required",
        note="; ".join(verdict.reasons())[:240],
    )
    _transition(record, "governance_required", audit_dir)

    # Auto-approve path (CLI flag for power users / tests)
    if auto_approve:
        review_payload["decision"] = "approved"
        review_payload["decided_at"] = now_iso()
        review_payload["decided_by"] = "auto-approve-mode"
        review_payload["decision_note"] = (
            "auto_approve_governance=True via execute_proposal"
        )
        _push_event(
            record, kind="governance_approved",
            note="auto-approve-mode",
        )
        _transition(record, "governance_approved", audit_dir)
        _persist(record, audit_dir)
        return "approved"

    # Polling loop
    poller = poll_fn or _default_governance_poll
    deadline = time.monotonic() + timeout_sec
    while True:
        # Cancel takes precedence over the gate decision — a
        # reviewer who hits Cancel mid-hold means "stop everything",
        # not "approve via the back door".
        info = check_cancel(audit_dir=audit_dir, exec_id=record.exec_id)
        if info is not None:
            cancel_exc = ExecutionCancelled(
                actor=info["actor"], note=info.get("note", ""),
            )
            review_payload["decision"] = "cancelled"
            review_payload["decided_at"] = now_iso()
            review_payload["decided_by"] = info["actor"]
            review_payload["decision_note"] = info.get("note", "")
            _abort_with_cancel(record, audit_dir, cancel_exc, applied=None)
            return "cancelled"

        result = poller(audit_dir=audit_dir, exec_id=record.exec_id)
        if result is not None:
            kind, payload = result
            review_payload["decided_at"] = (
                payload.get("at") or now_iso()
            )
            review_payload["decided_by"] = (
                payload.get("actor") or "anonymous"
            )
            review_payload["decision_note"] = payload.get("note", "")
            if kind == "approved":
                review_payload["decision"] = "approved"
                _push_event(
                    record, kind="governance_approved",
                    note=(payload.get("note") or "")[:240],
                )
                _transition(record, "governance_approved", audit_dir)
                _persist(record, audit_dir)
                return "approved"
            # rejected
            review_payload["decision"] = "rejected"
            record.abort_reason = (
                "governance: rejected by "
                f"{payload.get('actor') or 'anonymous'}"
                + (
                    f" ({payload.get('note', '')})"
                    if payload.get("note")
                    else ""
                )
            )
            _push_event(
                record, kind="governance_rejected",
                note=(payload.get("note") or "")[:240],
            )
            _transition(record, "governance_rejected", audit_dir)
            _finish(record, audit_dir)
            return "rejected"

        if time.monotonic() >= deadline:
            review_payload["decision"] = "timeout"
            review_payload["decided_at"] = now_iso()
            record.abort_reason = (
                f"governance: no decision within {timeout_sec:.0f}s"
            )
            _push_event(
                record, kind="governance_timeout",
                note=record.abort_reason,
            )
            _transition(record, "user_abort", audit_dir)
            _finish(record, audit_dir)
            return "timeout"

        sleep_fn(poll_interval_sec)


def _default_governance_poll(*, audit_dir: Path, exec_id: str):
    return read_and_clear_governance(
        audit_dir=audit_dir, exec_id=exec_id,
    )


def _capture_dry_run_diff(*, repo_root: Path, git_runner: Any) -> str:
    """Run `git diff` over the working tree to capture the
    edits-applied state BEFORE revert_edits restores files. Used
    by the P49-04 dry-run path so the audit carries a unified-
    diff preview for reviewer scrutiny.

    Empty string if git fails (rare — the planner+applier already
    ran inside the same repo). Truncated to 64KB so an audit JSON
    doesn't balloon for a refactor that touches a thousand lines;
    the truncation is signaled inline so a reader knows to look
    elsewhere for the full diff.
    """
    from well_harness.skill_executor.git_ops import _default_runner
    runner = git_runner or _default_runner
    result = runner(
        ["git", "diff", "--no-color"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=30.0,
    )
    diff_text = ""
    if hasattr(result, "stdout"):
        diff_text = result.stdout or ""
    if hasattr(result, "returncode") and int(result.returncode or 0) != 0:
        # Non-zero exit but stdout still available — git diff in a
        # working tree shouldn't fail, but if it did we capture
        # whatever we got.
        return diff_text
    DIFF_MAX_BYTES = 65_536
    if len(diff_text) > DIFF_MAX_BYTES:
        truncated = diff_text[:DIFF_MAX_BYTES]
        return (
            truncated
            + "\n\n[... dry-run diff truncated at 64KB. "
            "Re-run interactively for the full output.]\n"
        )
    return diff_text


def _check_cancel_and_abort(
    record: ExecutionRecord,
    audit_dir: Path,
    *,
    applied: ApplyResult | None,
) -> bool:
    """Check the cancel signal at a phase boundary. If present:
    revert any applied edits, set abort_reason, fire user_abort,
    persist + finish. Returns True if cancelled (caller must
    bail out), False otherwise.

    Why a centralized helper: each phase boundary has the same
    abort recipe (revert if applied / set reason / transition /
    finish). One helper keeps the recipe consistent and lets us
    add behavior (e.g. metrics, notifications) in one place.
    """
    info = check_cancel(audit_dir=audit_dir, exec_id=record.exec_id)
    if info is None:
        return False
    cancel_exc = ExecutionCancelled(
        actor=info["actor"], note=info.get("note", "")
    )
    _abort_with_cancel(record, audit_dir, cancel_exc, applied=applied)
    return True


def _abort_with_cancel(
    record: ExecutionRecord,
    audit_dir: Path,
    cancel_exc: ExecutionCancelled,
    *,
    applied: ApplyResult | None,
) -> None:
    """Drive the audit to ABORTED on a cancel signal. Reverts any
    applied edits first so the working tree is clean. Idempotent
    against an already-terminal record (no-op if already terminal,
    so concurrent cancel signals don't double-fire transitions)."""
    if is_terminal(ExecutionState(record.state)):
        return
    if applied is not None:
        try:
            revert_edits(applied)
        except Exception:
            # Best-effort revert; the abort proceeds either way.
            # Engineer can `git status` to inspect the residue.
            pass
    note = cancel_exc.note or ""
    record.abort_reason = (
        f"cancelled by {cancel_exc.actor}"
        + (f": {note}" if note else "")
    )
    _push_event(
        record,
        kind="user_cancel",
        note=f"actor={cancel_exc.actor} note={note}"[:200],
    )
    _transition(record, "user_abort", audit_dir)
    _finish(record, audit_dir)


def _transition(record: ExecutionRecord, event: str, audit_dir: Path) -> None:
    """Apply the state transition + write the corresponding event
    to the audit. Raises InvalidExecutionTransitionError (from
    next_state) if the transition isn't allowed — that's a
    programmer error and should crash the pipeline."""
    current = ExecutionState(record.state)
    target = next_state(current, event)
    record.state = target.value
    record.events.append(
        ExecutionEvent(
            at=now_iso(),
            kind="state_transition",
            from_state=current.value,
            to_state=target.value,
        )
    )
    _persist(record, audit_dir)


def _push_event(record: ExecutionRecord, *, kind: str, note: str = "") -> None:
    record.events.append(ExecutionEvent(at=now_iso(), kind=kind, note=note))


def _finish(record: ExecutionRecord, audit_dir: Path) -> None:
    """Mark terminal-state finished_at + persist."""
    if not record.finished_at:
        record.finished_at = now_iso()
    _persist(record, audit_dir)


def _persist(record: ExecutionRecord, audit_dir: Path) -> None:
    """Wrap write_audit so we can swap the dir without polluting
    the env. (write_audit honors WORKBENCH_SKILL_EXECUTIONS_DIR;
    we set it here just before the call.)"""
    prev = os.environ.get("WORKBENCH_SKILL_EXECUTIONS_DIR")
    os.environ["WORKBENCH_SKILL_EXECUTIONS_DIR"] = str(audit_dir)
    try:
        write_audit(record)
    finally:
        if prev is None:
            os.environ.pop("WORKBENCH_SKILL_EXECUTIONS_DIR", None)
        else:
            os.environ["WORKBENCH_SKILL_EXECUTIONS_DIR"] = prev


def _new_ask_id(exec_id: str) -> str:
    """Derived from exec_id so an ask is locatable just from the
    exec audit. Replaces 'EXEC' prefix with 'ASK'."""
    return exec_id.replace("EXEC-", "ASK-", 1)


def _ask_question_for(plan: PlannedChange) -> str:
    """Human-readable approval prompt the workbench card will
    render. Truncated to keep the chip readable."""
    bullet = "; ".join(
        f"{e.path}:{e.reason or 'edit'}" for e in plan.file_edits[:5]
    )
    suffix = "" if len(plan.file_edits) <= 5 else f" (and {len(plan.file_edits) - 5} more)"
    return (
        f"Approve plan? {plan.rationale}\n"
        f"namespaces={plan.affected_namespaces}; "
        f"edits={bullet}{suffix}"
    )


def _planner_failure_plan(exc: Exception) -> PlannedChange:
    """When the planner fails, we still want a plan stub in audit
    so the failure surface is uniform (audit.plan != None always
    after PLANNING). Records what we know."""
    return PlannedChange(
        rationale=f"planner failed: {type(exc).__name__}",
        file_edits=[],
        planner_response=str(exc)[:1000],
    )


def _branch_name_for(
    proposal_id: str,
    exec_id: str,
    *,
    kind: ExecutionKind = ExecutionKind.MODIFY,
) -> str:
    """`feat/exec-PROP-XXX-{6char}` for modify, `revert/exec-...`
    for revert. Short suffix from exec_id keeps the branch name
    compact while still unique if the same proposal runs twice.
    """
    short = exec_id.split("-")[-1]
    prefix = "revert" if kind == ExecutionKind.REVERT else "feat"
    return f"{prefix}/exec-{proposal_id}-{short}"


def _build_commit_message(
    *,
    proposal: dict,
    plan: PlannedChange,
    record: ExecutionRecord,
) -> str:
    """Commit message format mirrors the existing repo convention
    (see PR #48 dogfood) and includes the EXEC-id so
    `git log --grep` finds it."""
    interp = proposal.get("interpretation") or {}
    change_kind = interp.get("change_kind") or proposal.get("kind") or "modify"
    system_id = proposal.get("system_id", "thrust-reverser")
    proposal_id = proposal["id"]
    subject = (
        f"{'revert' if record.kind == ExecutionKind.REVERT else 'feat'}"
        f"({system_id}): {change_kind} per {proposal_id}"
    )
    body = (
        f"Implements proposal {proposal_id} via skill executor.\n"
        f"\n"
        f"Plan rationale: {plan.rationale}\n"
        f"Affected namespaces: {plan.affected_namespaces}\n"
        f"\n"
        f"Exec-Id: {record.exec_id}\n"
        f"Audit: .planning/skill_executions/{record.exec_id}.json\n"
    )
    return f"{subject}\n\n{body}"


def _pr_title_for(proposal: dict, plan: PlannedChange) -> str:
    """`feat(...)` for modify, `revert(...)` for revert. Bound to
    70 chars so the GitHub PR list view doesn't truncate."""
    interp = proposal.get("interpretation") or {}
    change_kind = interp.get("change_kind") or proposal.get("kind") or "modify"
    is_revert = (proposal.get("kind") or "modify") == "revert"
    prefix = "revert" if is_revert else "feat"
    if is_revert:
        # For reverts the change_kind is "revert"; surface the
        # original target SHA in the title so reviewers see what's
        # being undone without opening the PR body.
        target_sha = (proposal.get("revert_target_sha") or "?")[:8]
        return (
            f"{prefix}({proposal.get('system_id', 'thrust-reverser')}): "
            f"undo {target_sha} per {proposal['id']}"
        )[:70]
    return (
        f"{prefix}({proposal.get('system_id', 'thrust-reverser')}): "
        f"{change_kind} per {proposal['id']}"
    )[:70]


def _pr_body_for(
    *,
    proposal: dict,
    plan: PlannedChange,
    record: ExecutionRecord,
    audit_dir: Path,
) -> str:
    """PR body = human summary + the EXEC stamp the P48-05 gate
    parses."""
    summary = (
        f"## Summary\n\n"
        f"Skill-executor PR for proposal `{proposal['id']}`.\n\n"
        f"**Plan rationale**: {plan.rationale}\n\n"
        f"**Affected namespaces**: {', '.join(plan.affected_namespaces)}\n\n"
        f"**Edits**:\n"
        + "\n".join(f"- `{e.path}` — {e.reason or 'edit'}" for e in plan.file_edits)
        + "\n"
    )
    audit_rel = f".planning/skill_executions/{record.exec_id}.json"
    stamp = build_exec_stamp(
        exec_id=record.exec_id,
        proposal_id=proposal["id"],
        audit_path=audit_rel,
        executor_version=EXECUTOR_VERSION,
    )
    return f"{summary}\n{stamp}\n"
