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

from well_harness.skill_executor.audit import (
    AUDIT_DIR_NAME,
    audit_dir,
    list_audits,
    new_execution_id,
    read_audit,
    write_audit,
)
from well_harness.skill_executor.errors import (
    AuditSchemaError,
    InvalidExecutionTransitionError,
    SkillExecutorError,
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
    "Ask",
    "AskResponse",
    "AuditSchemaError",
    "AuditSource",
    "ExecutionKind",
    "ExecutionRecord",
    "ExecutionState",
    "FileEdit",
    "InvalidExecutionTransitionError",
    "PlannedChange",
    "SkillExecutorError",
    "TERMINAL_STATES",
    "TestResult",
    "audit_dir",
    "is_terminal",
    "list_audits",
    "new_execution_id",
    "next_state",
    "read_audit",
    "write_audit",
]
