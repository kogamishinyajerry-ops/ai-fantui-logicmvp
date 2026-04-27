"""Typed error tree for the skill executor."""

from __future__ import annotations


class SkillExecutorError(Exception):
    """Base class. Catch this if you only care that *something*
    skill-executor-shaped failed."""


class AuditSchemaError(SkillExecutorError):
    """Raised when an audit JSON record violates the documented
    schema (P48-01 .github/EXEC-AUDIT-SCHEMA.md). Either:
      - missing a required field
      - field has wrong type
      - state name not in ExecutionState
      - schema_version unknown to this module
    Read/write paths both raise this; the CI gate (P48-05) catches
    audit files committed in the wrong shape."""


class InvalidExecutionTransitionError(SkillExecutorError):
    """Raised when next_state(current, event) is asked for a
    transition not in ALLOWED_TRANSITIONS. This is a programmer
    error — the state machine is fixed at module-load time."""
