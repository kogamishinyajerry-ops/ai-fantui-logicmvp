"""Planner — turn a brief into a typed PlannedChange via MiniMax.

Three-layer validator (any layer fails → plan is rejected):

  1. JSON-parse layer — strip `<think>` + fences, run json.loads
  2. Schema layer — required fields present and correctly typed
  3. Namespace layer — every file_edits[].path falls within at
     least one of the affected_namespaces' file globs

Retry exactly once. The retry prompt re-states the schema + the
specific failure ("your previous response was not valid JSON
because X"). Two failures → PlannerError → caller transitions
audit to FAILED state with the full prompt + response in
audit.plan.planner_response so a reviewer can see exactly what
the model said.

What this module does NOT do:
  - Touch any files
  - Run git
  - Talk to the workbench HTTP server
  - Decide whether to ASK or auto-apply (always returns; ASKING is
    a state owned by the caller)

What it DOES do:
  - Build a strict-JSON prompt the LLM must respond to
  - Invoke the MiniMax client with that prompt
  - Parse + validate the response into a typed PlannedChange
  - Cross-check every edit path against the proposal's namespace
  - Capture full provenance (prompt, response, timing) for audit
"""

from __future__ import annotations

import json
from typing import Any

from well_harness.skill_executor.errors import SkillExecutorError
from well_harness.skill_executor.llm_client import (
    LLMResponse,
    LLMUnavailableError,
    MINIMAX_DEFAULT_MODEL,
    call_minimax,
    resolve_minimax_api_key,
)
from well_harness.skill_executor.models import FileEdit, PlannedChange
from well_harness.skill_executor.namespaces import (
    PANEL_NAMESPACES,
    PANEL_NAMESPACES_BY_ID,
    validate_edit_path,
)


class PlannerError(SkillExecutorError):
    """The planner could not produce a valid plan after all
    retries. The full LLM exchange is in `last_response`; the
    caller should record both into the audit before transitioning
    to FAILED."""

    def __init__(
        self,
        message: str,
        *,
        attempts: list[LLMResponse],
        last_validation_error: str,
    ) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.last_validation_error = last_validation_error


_REQUIRED_PLAN_FIELDS = (
    "rationale",
    "affected_namespaces",
    "file_edits",
)


def plan_from_brief(
    *,
    proposal_record: dict,
    brief_text: str,
    api_key: str | None = None,
    model: str | None = None,
    request_post: Any = None,
) -> PlannedChange:
    """Synchronous planner entry point. Returns a validated
    PlannedChange or raises PlannerError / LLMUnavailableError.

    `proposal_record` is the raw proposal dict from
    `.planning/proposals/PROP-*.json` (must include `id`,
    `system_id`, `kind`, `interpretation`, and for revert kind the
    `revert_target_sha`).

    `brief_text` is the dev-queue brief markdown body. The planner
    uses it as ground truth for what the engineer/reviewer
    intended; the proposal JSON adds structured fields the brief
    text doesn't carry.

    `api_key` defaults to resolve_minimax_api_key(). If both env
    and ~/.minimax_key are empty, raises LLMUnavailableError.
    The planner never silently falls back to rules — that would
    defeat the audit's "we know what the LLM said" property.

    `request_post` is the test-injection hook pass-through.
    """
    chosen_key = api_key or resolve_minimax_api_key()
    if not chosen_key:
        raise LLMUnavailableError(
            "no MiniMax API key found in MINIMAX_API_KEY / "
            "Minimax_API_key env, nor in ~/.minimax_key file"
        )
    chosen_model = model or MINIMAX_DEFAULT_MODEL
    base_prompt = _build_planner_prompt(proposal_record, brief_text)

    attempts: list[LLMResponse] = []
    last_validation_error = ""
    for attempt_index in range(2):  # original + 1 retry
        prompt = (
            base_prompt
            if attempt_index == 0
            else _build_retry_prompt(base_prompt, last_validation_error)
        )
        response = call_minimax(
            prompt,
            api_key=chosen_key,
            model=chosen_model,
            request_post=request_post,
        )
        attempts.append(response)
        try:
            plan = _parse_and_validate_response(response, proposal_record)
        except _PlannerValidationError as exc:
            last_validation_error = str(exc)
            continue
        # Success — populate provenance fields and return.
        plan.planner_prompt = prompt
        plan.planner_response = response.raw_content
        plan.planner_started_at = response.started_at
        plan.planner_finished_at = response.finished_at
        plan.llm_backend = response.model
        return plan

    raise PlannerError(
        f"planner failed after {len(attempts)} attempts; "
        f"last error: {last_validation_error}",
        attempts=attempts,
        last_validation_error=last_validation_error,
    )


# ─── Prompt building ─────────────────────────────────────────────────


def _build_planner_prompt(proposal_record: dict, brief_text: str) -> str:
    """Strict-JSON prompt the planner must respond to. Lists the
    namespaces by name so the LLM knows what to declare in
    `affected_namespaces`, and lists the path globs so it knows
    which files are in-scope for each."""
    proposal_id = proposal_record.get("id", "PROP-?")
    system_id = proposal_record.get("system_id", "thrust-reverser")
    kind = proposal_record.get("kind", "modify")
    interp = proposal_record.get("interpretation") or {}

    namespace_listing = "\n".join(
        f"- {ns['namespace']}: {ns['label_zh']} · {ns['label_en']}\n"
        f"    files = {list(ns['files'])}"
        for ns in PANEL_NAMESPACES
    )

    revert_addendum = ""
    if kind == "revert":
        target_sha = proposal_record.get("revert_target_sha", "?")
        revert_of = proposal_record.get("revert_of_proposal_id", "?")
        revert_addendum = (
            f"\n\nIMPORTANT — this is a REVERT proposal. The plan "
            f"should restore the truth-engine state that existed at "
            f"`{target_sha}~1` (parent of {target_sha}). The original "
            f"forward change was {revert_of}. Use plan/ask/edit "
            f"semantics, not blind `git revert` — read the brief's "
            f"'Reverse-target state' section."
        )

    return (
        f"You are the planner for the AI FANTUI control logic skill "
        f"executor. Your job: read the engineer's accepted proposal "
        f"and the dev-queue brief, then produce a PRECISE PLAN of "
        f"file edits + risk assessment as a SINGLE JSON OBJECT.\n\n"
        f"Proposal id: {proposal_id}\n"
        f"System: {system_id}\n"
        f"Kind: {kind}\n"
        f"Engineer's interpretation: {json.dumps(interp, ensure_ascii=False)}\n\n"
        f"Truth-engine namespaces (every file_edits[].path MUST fall "
        f"within one of these, AND that namespace MUST appear in "
        f"affected_namespaces):\n{namespace_listing}\n"
        f"{revert_addendum}\n\n"
        f"=== Dev-queue brief ===\n{brief_text}\n=== end brief ===\n\n"
        f"Respond with ONLY a JSON object (no prose, no markdown "
        f"fences) matching this exact schema:\n"
        f"{{\n"
        f'  "rationale":           "string — why this plan is correct",\n'
        f'  "affected_namespaces": ["logic_truth"|"requirements"|"simulation_workbench", ...],\n'
        f'  "risk_assessment":     {{"logic_truth": "red"|"yellow"|"green", ...}},\n'
        f'  "estimated_loc":       12,\n'
        f'  "file_edits": [\n'
        f'    {{\n'
        f'      "path":         "src/well_harness/controller.py",\n'
        f'      "old_snippet":  "exact text in the current file",\n'
        f'      "new_snippet":  "the replacement",\n'
        f'      "reason":       "string — why THIS edit"\n'
        f'    }}\n'
        f'  ],\n'
        f'  "test_changes": [\n'
        f'    /* same shape as file_edits — empty list is allowed */\n'
        f'  ]\n'
        f'}}\n\n'
        f"old_snippet must match the file's current text exactly; "
        f"the executor will reject the plan if no match is found."
    )


def _build_retry_prompt(original_prompt: str, error_reason: str) -> str:
    """If the first response fails validation, give the LLM one
    targeted shot at fixing it. We restate the schema + the
    specific reason the previous response was invalid."""
    return (
        f"{original_prompt}\n\n"
        f"=== Retry context ===\n"
        f"Your previous response was invalid: {error_reason}\n"
        f"Return ONLY the JSON object. Do not include any "
        f"explanation, apology, or markdown fences."
    )


# ─── Parse + validate ────────────────────────────────────────────────


class _PlannerValidationError(Exception):
    """Internal — caught and converted to a retry within the
    planner. Should never escape to the caller."""


def _parse_and_validate_response(
    response: LLMResponse,
    proposal_record: dict,
) -> PlannedChange:
    """Layer 1 + 2 + 3 validation. Returns a PlannedChange with
    provenance fields still empty (caller fills those)."""

    # Layer 1: JSON parse
    try:
        parsed = json.loads(response.content)
    except json.JSONDecodeError as exc:
        raise _PlannerValidationError(
            f"response is not valid JSON: {exc}"
        ) from exc
    if not isinstance(parsed, dict):
        raise _PlannerValidationError(
            f"response is not a JSON object (got {type(parsed).__name__})"
        )

    # Layer 2: required-field schema check
    for field in _REQUIRED_PLAN_FIELDS:
        if field not in parsed:
            raise _PlannerValidationError(
                f"missing required field {field!r}"
            )
    if not isinstance(parsed["rationale"], str):
        raise _PlannerValidationError(
            "rationale must be a string"
        )
    if not isinstance(parsed["affected_namespaces"], list):
        raise _PlannerValidationError(
            "affected_namespaces must be a list"
        )
    if not parsed["affected_namespaces"]:
        raise _PlannerValidationError(
            "affected_namespaces cannot be empty"
        )
    for ns in parsed["affected_namespaces"]:
        if not isinstance(ns, str) or ns not in PANEL_NAMESPACES_BY_ID:
            raise _PlannerValidationError(
                f"affected_namespaces contains unknown namespace {ns!r}; "
                f"must be one of {sorted(PANEL_NAMESPACES_BY_ID)}"
            )
    if not isinstance(parsed["file_edits"], list):
        raise _PlannerValidationError(
            "file_edits must be a list"
        )
    if not parsed["file_edits"]:
        raise _PlannerValidationError(
            "file_edits cannot be empty (a no-op plan is rejected)"
        )

    raw_edits: list[dict] = []
    for i, edit in enumerate(parsed["file_edits"]):
        if not isinstance(edit, dict):
            raise _PlannerValidationError(
                f"file_edits[{i}] must be an object"
            )
        for sub in ("path", "old_snippet", "new_snippet"):
            if sub not in edit:
                raise _PlannerValidationError(
                    f"file_edits[{i}].{sub} is required"
                )
            if not isinstance(edit[sub], str):
                raise _PlannerValidationError(
                    f"file_edits[{i}].{sub} must be a string"
                )
        raw_edits.append(edit)

    # Layer 3: namespace coverage check
    affected: list[str] = list(parsed["affected_namespaces"])
    for i, edit in enumerate(raw_edits):
        ok, reason = validate_edit_path(
            edit["path"],
            affected_namespaces=affected,
        )
        if not ok:
            raise _PlannerValidationError(
                f"file_edits[{i}]: {reason}"
            )

    # Optional fields
    test_changes_raw: list[dict] = []
    if "test_changes" in parsed:
        if not isinstance(parsed["test_changes"], list):
            raise _PlannerValidationError(
                "test_changes must be a list when present"
            )
        for i, edit in enumerate(parsed["test_changes"]):
            if not isinstance(edit, dict):
                raise _PlannerValidationError(
                    f"test_changes[{i}] must be an object"
                )
            for sub in ("path", "old_snippet", "new_snippet"):
                if sub not in edit or not isinstance(edit[sub], str):
                    raise _PlannerValidationError(
                        f"test_changes[{i}].{sub} required string"
                    )
            test_changes_raw.append(edit)

    risk_raw = parsed.get("risk_assessment") or {}
    if not isinstance(risk_raw, dict):
        raise _PlannerValidationError(
            "risk_assessment must be an object when present"
        )
    risk_assessment: dict[str, str] = {}
    for k, v in risk_raw.items():
        if not isinstance(k, str) or not isinstance(v, str):
            continue
        if v not in ("red", "yellow", "green"):
            continue
        risk_assessment[k] = v

    estimated_loc = parsed.get("estimated_loc", 0)
    if not isinstance(estimated_loc, int) or estimated_loc < 0:
        estimated_loc = 0

    return PlannedChange(
        rationale=parsed["rationale"],
        file_edits=[
            FileEdit(
                path=e["path"],
                old_snippet=e["old_snippet"],
                new_snippet=e["new_snippet"],
                reason=str(e.get("reason") or ""),
            )
            for e in raw_edits
        ],
        test_changes=[
            FileEdit(
                path=e["path"],
                old_snippet=e["old_snippet"],
                new_snippet=e["new_snippet"],
                reason=str(e.get("reason") or ""),
            )
            for e in test_changes_raw
        ],
        estimated_loc=estimated_loc,
        affected_namespaces=affected,
        risk_assessment=risk_assessment,
    )
