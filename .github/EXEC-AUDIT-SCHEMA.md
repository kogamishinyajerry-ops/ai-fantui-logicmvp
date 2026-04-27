# Skill Executor Audit Schema (v1)

This document describes the JSON shape of every file under
`.planning/skill_executions/EXEC-*.json`. The file is the
human-readable contract for the schema; the machine-enforced version
is the validator at
`src/well_harness/skill_executor/schema.py::validate_audit_dict`.

The two MUST agree. If you change the validator, update this doc in
the same PR (and bump `AUDIT_SCHEMA_VERSION`).

## Why this exists

Per user direction (2026-04-27): the skill that executes proposal
modifications is the most critical link in the engineer→reviewer→
executor loop. To build trust:

- **Standardized** — every execution produces an audit JSON in the
  same shape, regardless of which engineer ran it
- **Traceable** — every state transition, ask, and edit is recorded
  with a UTC timestamp
- **Verifiable** — the P48-05 GitHub Action refuses to merge any
  truth-engine PR whose `Exec-Id: EXEC-XXX` stamp doesn't have a
  matching, schema-valid audit JSON in the same PR

## File location and naming

```
.planning/skill_executions/EXEC-YYYYMMDDTHHMMSSffffff-{6hex}.json
```

The `EXEC-` prefix mirrors `PROP-` for proposals. The microsecond
timestamp + 6-hex suffix protects against collisions when two
executors start in the same second.

## Top-level fields

### Required

| Field | Type | Description |
|---|---|---|
| `exec_id` | string | Must match the filename (without `.json`). Pattern: `^EXEC-\d{20}-[0-9a-f]{6}$`. |
| `schema_version` | int | Currently `1`. Records with unknown versions are rejected — migrate or bump. |
| `proposal_id` | string | The `PROP-...` id this execution is implementing. |
| `kind` | string | One of `modify`, `revert`, `backfill`. |
| `audit_source` | string | One of `live`, `backfill`. |
| `started_at` | string | ISO-8601 UTC with `Z` suffix. |
| `state` | string | One of `INIT`, `PLANNING`, `ASKING`, `EDITING`, `TESTING`, `PR_OPEN`, `LANDED`, `ABORTED`, `FAILED`. |

### Optional

| Field | Type | Description |
|---|---|---|
| `finished_at` | string | ISO-8601 UTC. Set when state becomes terminal. |
| `executor_version` | string | Module version at time of run. |
| `executor_host` | string | `socket.gethostname()` of the box that ran it. |
| `executor_user` | string | OS user. |
| `llm_backend` | string | E.g. `minimax-m2.7-highspeed`. |
| `plan` | object \| null | The structured planner output (see below). |
| `asks` | array | Approval rounds with the engineer (see below). |
| `tests_before` | object \| null | Pytest summary before edits. |
| `tests_after` | object \| null | Pytest summary after edits. |
| `branch` | string | Feature branch name. |
| `commits` | array of string | SHAs of commits this execution produced. |
| `pr_url` | string | The `https://github.com/.../pull/N` URL. |
| `landed_sha` | string | Final merged commit SHA (terminal LANDED state). |
| `abort_reason` | string | Free text for ABORTED/FAILED states. |
| `events` | array | Per-step breadcrumbs (see below). |

## `plan` object

Set by the planner LLM after the `start_planning` event. Once set,
should not be mutated; if the engineer rejects the plan in ASKING
state, a new plan is recorded as a separate audit entry on a fresh
EXEC-id, not by overwriting the existing one.

```json
{
  "rationale": "string — why this plan",
  "file_edits": [
    {
      "path": "src/well_harness/controller.py",
      "old_snippet": "exact string to match",
      "new_snippet": "exact replacement",
      "reason": "string — optional"
    }
  ],
  "test_changes": [ /* same shape as file_edits */ ],
  "estimated_loc": 12,
  "affected_namespaces": ["logic_truth"],
  "risk_assessment": {"logic_truth": "yellow"},
  "planner_prompt": "the full prompt sent to the LLM",
  "planner_response": "the raw LLM response",
  "planner_started_at": "ISO 8601",
  "planner_finished_at": "ISO 8601",
  "llm_backend": "minimax-m2.7-highspeed"
}
```

The planner prompt and response are stored verbatim so a future
session can replay the planning step and compare.

## `asks` array

Each entry captures one round-trip with the engineer in ASKING state.
Most executions have exactly one entry (engineer approves), but
needs-changes can produce multiple over the same EXEC-id.

```json
{
  "ask_id": "ASK-...",
  "question": "human-readable question shown in the workbench card",
  "shown_in_workbench_at": "ISO 8601",
  "user_response": "approved" | "rejected" | "needs_changes" | null,
  "user_responded_at": "ISO 8601 — empty if user_response is null",
  "user_actor": "name from workbench session",
  "note": "engineer's free-text note, optional"
}
```

`user_response` is null while the executor is waiting for the
engineer to click in the workbench; once they click, both
`user_response` and `user_responded_at` are filled.

## `tests_before` / `tests_after` object

```json
{
  "passed": 1448,
  "failed": 0,
  "skipped": 0,
  "errors": 0,
  "duration_sec": 132.4,
  "ran_at": "ISO 8601",
  "failed_test_ids": ["tests/test_foo.py::test_bar"]
}
```

The test gate (P48-03) refuses to advance to PR_OPEN unless:
- `tests_after.passed >= tests_before.passed`
- `tests_after.failed_test_ids` doesn't include any id that wasn't
  in `tests_before.failed_test_ids`

## `events` array

Append-only breadcrumb log. Every state transition emits one entry;
non-transition events (e.g. "planner started", "branch created") may
also append.

```json
{
  "at": "ISO 8601",
  "kind": "state_transition" | "init" | "planner_invocation" | "edit_apply" | "test_run" | "pr_open" | "merge_recorded" | ...,
  "note": "optional human text",
  "from": "INIT",        // only present for state_transition
  "to": "PLANNING"
}
```

## Special audit_source values

### `live`
Default. Written incrementally as the executor ran. Trustworthy in
the strict sense — every field reflects something the executor
observed first-hand.

### `backfill`
Synthesized after the fact. Used for:
- PR #48 (the pre-P48 dogfood) — backfilled per Q7(a) so it
  participates in the new gate
- Any PR landed before P48-05 went into effect

Backfill records have:
- `audit_source: "backfill"` — flag is the canonical signal
- `state: "LANDED"` — backfilled audits skip the lifecycle
- `plan.planner_prompt` and `planner_response` are typically empty
  (we don't have them) with a note in `rationale` saying so
- `events` may be sparse — only fields we can recover from git
  metadata

The CI gate accepts backfill records but flags them with a comment
on the PR so reviewers can sanity-check.

## Adding a new state or event

1. Add the state to `models.ExecutionState` and to the transition
   table in `states.ALLOWED_TRANSITIONS`
2. Update this doc's "Top-level fields" → `state` row
3. Bump `AUDIT_SCHEMA_VERSION` if the change is non-additive
4. Update the validator if a new field becomes required
5. Update the CI gate's allow-list of states if the new state
   should pass merge

The CI gate's source of truth is the validator, not this doc — if
the two disagree, the validator wins, but a doc that lies about the
schema is a defect that should be fixed in the same PR.
