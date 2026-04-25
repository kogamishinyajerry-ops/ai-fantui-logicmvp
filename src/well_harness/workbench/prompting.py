from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from .proposals import validate_annotation_proposal


DEFAULT_SCOPE_FILES = (
    "src/well_harness/workbench/**",
    "src/well_harness/static/workbench.*",
    "src/well_harness/static/annotation_overlay.js",
    "schemas/annotation_proposal.schema.json",
    "docs/workbench/**",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_ticket_filename(ticket_id: str) -> str:
    candidate = re.sub(r"[^A-Za-z0-9_.-]+", "-", ticket_id).strip("-")
    if not candidate:
        raise ValueError("ticket_id must produce a safe file name")
    return f"{candidate}.json"


def _anchor_section(proposal: dict[str, Any], authorized_engineer: str) -> str:
    return "\n".join(
        [
            f"- Proposal: {proposal['id']}",
            f"- Ticket: {proposal['ticket_id']}",
            f"- System: {proposal['system_id']}",
            f"- Authorized Engineer: {authorized_engineer}",
            f"- Surface: {proposal['surface']}",
            f"- Tool: {proposal['tool']}",
            f"- Note: {proposal['note']}",
            f"- Anchor JSON: {json.dumps(proposal['anchor'], ensure_ascii=False, sort_keys=True)}",
        ]
    )


def _scope_section(scope_files: list[str]) -> str:
    return "\n".join(f"- {path}" for path in scope_files)


def _acceptance_section(proposal: dict[str, Any]) -> str:
    return "\n".join(
        [
            "- Implement only the scoped Workbench change requested by the annotation proposal.",
            f"- Preserve proposal ID `{proposal['id']}` and ticket ID `{proposal['ticket_id']}` in handoff notes.",
            "- Add or update focused tests for the changed behavior.",
            "- Run the repo's fast-lane validation before handing back.",
        ]
    )


def _non_goals_section() -> str:
    return "\n".join(
        [
            "- Do not edit controller truth, adapter truth, logic gates, pitch materials, or Parking Lot items.",
            "- Do not write to Notion directly.",
            "- Do not expand scope files without Kogami approval.",
            "- Do not present a local stub as a merged or deployed change.",
        ]
    )


def render_claude_code_prompt(
    proposal: dict[str, Any],
    *,
    authorized_engineer: str,
    scope_files: list[str] | None = None,
    template_path: str | Path,
) -> str:
    validate_annotation_proposal(proposal)
    if not authorized_engineer.strip():
        raise ValueError("authorized_engineer is required")
    scope = list(scope_files or DEFAULT_SCOPE_FILES)
    if not scope:
        raise ValueError("scope_files must not be empty")

    template = Path(template_path).read_text(encoding="utf-8")
    replacements = {
        "anchor": _anchor_section(proposal, authorized_engineer),
        "scope": _scope_section(scope),
        "acceptance": _acceptance_section(proposal),
        "non_goals": _non_goals_section(),
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", value)
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def build_ticket_payload(
    proposal: dict[str, Any],
    *,
    authorized_engineer: str,
    scope_files: list[str] | None,
    template_path: str | Path,
) -> dict[str, Any]:
    scope = list(scope_files or DEFAULT_SCOPE_FILES)
    generated_prompt = render_claude_code_prompt(
        proposal,
        authorized_engineer=authorized_engineer,
        scope_files=scope,
        template_path=template_path,
    )
    return {
        "Task": proposal["ticket_id"],
        "Type": "Workbench Annotation",
        "Source Proposal": proposal["id"],
        "Authorized Engineer": authorized_engineer,
        "Scope Files": scope,
        "Generated Prompt": generated_prompt,
        "PR URL": "",
        "Verdict": "Pending",
        "Created At": _utc_now(),
        "Proposal": proposal,
    }


def publish_ticket(
    proposal: dict[str, Any],
    *,
    authorized_engineer: str,
    scope_files: list[str] | None = None,
    ticket_root: str | Path,
    template_path: str | Path,
) -> Path:
    payload = build_ticket_payload(
        proposal,
        authorized_engineer=authorized_engineer,
        scope_files=scope_files,
        template_path=template_path,
    )
    root = Path(ticket_root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / _safe_ticket_filename(proposal["ticket_id"])
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(path)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return path
