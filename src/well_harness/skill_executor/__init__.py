"""Skill executor — the standalone module that executes proposal
modifications against the truth-engine. P48 phase arc.

Why this exists (2026-04-27 user direction): the prior workflow had
Claude Code reading a markdown skill spec and improvising every step.
That made the most critical link of the engineer→reviewer→executor
loop unstandardized, untraceable, and impossible to mechanically
constrain. The skill_executor module owns the orchestration; the LLM
is invoked as a tool with a typed-output contract, not as the
orchestrator.

Public API (P48-01 surface area — schema/types/audit only; no LLM, no
file edits, no git):

    from well_harness.skill_executor import (
        ExecutionRecord,
        ExecutionState,
        AuditSource,
        ExecutionKind,
        PlannedChange,
        FileEdit,
        Ask,
        TestResult,
        new_execution_id,
        write_audit,
        read_audit,
        list_audits,
        AUDIT_SCHEMA_VERSION,
        AUDIT_DIR_NAME,
    )

Subsequent phases (NOT in P48-01):
    P48-02: planner LLM integration
    P48-03: apply edits + test gate
    P48-04: branch + commit + PR + EXEC-id stamp
    P48-05: GitHub Action pre-merge gate
    P48-06: CLI entry point + workbench-mediated ASKING UX
    P48-07: revert flow protocol
"""

from well_harness.skill_executor.applier import (
    AppliedEdit,
    ApplyError,
    ApplyResult,
    apply_edits,
    revert_edits,
)
from well_harness.skill_executor.audit import (
    AUDIT_DIR_NAME,
    audit_dir,
    list_audits,
    new_execution_id,
    read_audit,
    write_audit,
)
from well_harness.skill_executor.backfill import (
    BackfillError,
    synthesize_backfill_audit,
)
from well_harness.skill_executor.errors import (
    AuditSchemaError,
    InvalidExecutionTransitionError,
    SkillExecutorError,
)
from well_harness.skill_executor.executor_spawner import (
    SpawnResult,
    SpawnStatus,
    SpawnerError,
    is_auto_spawn_enabled,
    spawn_executor_for_proposal,
    spawn_log_path,
    spawn_marker_path,
)
from well_harness.skill_executor.gate import (
    GateResult,
    check_test_gate,
)
from well_harness.skill_executor.gate_check import (
    GateCheckResult,
    check_pr_audit_compliance,
)
from well_harness.skill_executor.git_ops import (
    CommitResult,
    GitError,
    commit_files,
    create_branch,
    current_branch,
    head_sha,
    push_branch,
)
from well_harness.skill_executor.orchestrator import (
    EXECUTOR_VERSION,
    OrchestratorError,
    OrchestratorResult,
    execute_proposal,
)
from well_harness.skill_executor.pr_maker import (
    EXEC_STAMP_DELIMITER,
    PRDetails,
    PRMakerError,
    build_exec_stamp,
    open_pr,
    parse_exec_stamp,
)
from well_harness.skill_executor.proposal_io import (
    ProposalIOError,
    brief_path,
    load_brief,
    load_proposal,
    proposal_path,
)
from well_harness.skill_executor.workbench_polling import (
    ApprovalTimeoutError,
    WorkbenchApprovalCallback,
    approval_signal_path,
    read_and_clear_approval,
    write_approval_signal,
)
from well_harness.skill_executor.test_runner import (
    TestRunnerError,
    parse_pytest_output,
    run_tests,
)
from well_harness.skill_executor.llm_client import (
    LLMResponse,
    LLMResponseError,
    LLMUnavailableError,
    MINIMAX_API_BASE,
    MINIMAX_DEFAULT_MODEL,
    MINIMAX_REQUEST_TIMEOUT_SEC,
    call_minimax,
    resolve_minimax_api_key,
    strip_json_fences,
)
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    Ask,
    AskResponse,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
    FileEdit,
    PlannedChange,
    TestResult,
)
from well_harness.skill_executor.namespaces import (
    PANEL_NAMESPACES,
    PANEL_NAMESPACES_BY_ID,
    namespace_for_path,
    validate_edit_path,
)
from well_harness.skill_executor.planner import (
    PlannerError,
    plan_from_brief,
)
from well_harness.skill_executor.states import (
    ALLOWED_TRANSITIONS,
    TERMINAL_STATES,
    ExecutionState,
    is_terminal,
    next_state,
)


__all__ = [
    "AUDIT_DIR_NAME",
    "AUDIT_SCHEMA_VERSION",
    "ALLOWED_TRANSITIONS",
    "AppliedEdit",
    "ApplyError",
    "ApplyResult",
    "ApprovalTimeoutError",
    "Ask",
    "AskResponse",
    "AuditSchemaError",
    "AuditSource",
    "BackfillError",
    "CommitResult",
    "EXEC_STAMP_DELIMITER",
    "EXECUTOR_VERSION",
    "ExecutionKind",
    "ExecutionRecord",
    "ExecutionState",
    "FileEdit",
    "GateCheckResult",
    "GateResult",
    "GitError",
    "InvalidExecutionTransitionError",
    "LLMResponse",
    "LLMResponseError",
    "LLMUnavailableError",
    "MINIMAX_API_BASE",
    "MINIMAX_DEFAULT_MODEL",
    "MINIMAX_REQUEST_TIMEOUT_SEC",
    "OrchestratorError",
    "OrchestratorResult",
    "PANEL_NAMESPACES",
    "PANEL_NAMESPACES_BY_ID",
    "PRDetails",
    "PRMakerError",
    "PlannedChange",
    "PlannerError",
    "ProposalIOError",
    "SkillExecutorError",
    "SpawnResult",
    "SpawnStatus",
    "SpawnerError",
    "TERMINAL_STATES",
    "TestResult",
    "TestRunnerError",
    "WorkbenchApprovalCallback",
    "apply_edits",
    "approval_signal_path",
    "audit_dir",
    "brief_path",
    "build_exec_stamp",
    "call_minimax",
    "check_pr_audit_compliance",
    "check_test_gate",
    "commit_files",
    "create_branch",
    "current_branch",
    "execute_proposal",
    "head_sha",
    "is_auto_spawn_enabled",
    "is_terminal",
    "list_audits",
    "load_brief",
    "load_proposal",
    "namespace_for_path",
    "new_execution_id",
    "next_state",
    "open_pr",
    "parse_exec_stamp",
    "parse_pytest_output",
    "plan_from_brief",
    "proposal_path",
    "push_branch",
    "read_and_clear_approval",
    "read_audit",
    "resolve_minimax_api_key",
    "revert_edits",
    "spawn_executor_for_proposal",
    "spawn_log_path",
    "spawn_marker_path",
    "write_approval_signal",
    "run_tests",
    "strip_json_fences",
    "synthesize_backfill_audit",
    "validate_edit_path",
    "write_audit",
]
