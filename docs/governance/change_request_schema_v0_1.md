# ChangeRequest Schema v0.1 Draft

This is a non-authoritative draft contract for recording proposed changes in the Codex Daily Lane.
It does not approve DAL changes, does not promote truth-level, and does not change adapter status.

## Authority Boundary

- `authority.status` must be `draft_non_authoritative`.
- `authority.approval_required_before_execution` must be `true`.
- A valid ChangeRequest record is only a proposal/evidence container.
- Execution authority remains outside this schema when a request touches DAL, Charter, truth-level, certified adapter status, frozen assets, or controller truth semantics.

## Required Structure

- `origin`: where the request came from, such as Linear, GitHub, Notion, repo, or manual intake.
- `owner`: who is responsible for drafting or owning evidence.
- `classification`: bookkeeping, behavior change, DAL-impacting, truth-level-impacting, or Charter-impacting.
- `impacts`: affected namespaces, adapters, and truth-level impact.
- `dal_impact`: explicit impact state and rationale.
- `evidence_anchors`: Linear/GitHub/Notion/repo/test links that justify the request.
- `decision_links`: later links to decisions or closure notes.

## Editable Workbench Handoff Extension

`workbench_handoff` is an optional v0.1 extension for sandbox candidates produced
by `/workbench`.

- `mode` must be `draft_only`.
- `mutation_status` records that Linear writes were not attempted, only dry-run,
  or completed outside the workbench manually.
- `changed_model_hash` and `diff_report_hash` identify the sandbox candidate and
  baseline-diff evidence.
- `truth_level_impact` and `dal_impact` must remain `none`.
- `red_line_impact.touched` must remain `["none"]` inside the Codex lane.
- `linear_issue_body` and `pr_proof_packet` are copy-ready text fields, not live
  Linear or GitHub mutations.

## DAL and Truth-Level Guardrail

Non-DAL bookkeeping requests may stay inside Codex Daily Lane as draft records.
Any DAL-impacting, truth-level-impacting, or Charter-impacting request must include `escalation`.
That escalation is still only a routing record; it is not approval.

## Notion Role

After the 2026-04-29 routing decision, Notion is documentation/evidence only.
Notion comments or pages are not treated as Opus review execution and are not approval gates.

## Example Bookkeeping Record

```json
{
  "schema_version": "change_request.v0.1",
  "change_request_id": "CR-DRAFT-0001",
  "title": "Record Notion as docs-only evidence surface",
  "summary": "Documents a governance-surface clarification without changing truth behavior.",
  "authority": {
    "status": "draft_non_authoritative",
    "approval_required_before_execution": true,
    "approval_routes": ["kogami_charter"]
  },
  "origin": {
    "source": "linear",
    "source_ref": "JER-146",
    "created_by": "codex-daily-lane",
    "created_at": "2026-04-29"
  },
  "owner": {
    "name": "Codex Daily Lane",
    "role": "draft_author"
  },
  "status": "draft",
  "classification": "bookkeeping",
  "impacts": {
    "namespaces": ["governance"],
    "adapters": [],
    "truth_level_impact": "none"
  },
  "dal_impact": {
    "impact": "none",
    "rationale": "Documentation-only governance record; no system behavior or DAL claim changes."
  },
  "evidence_anchors": [
    {
      "kind": "linear",
      "ref": "JER-146",
      "url": "https://linear.app/jerrykogami/issue/JER-146"
    }
  ],
  "decision_links": []
}
```
