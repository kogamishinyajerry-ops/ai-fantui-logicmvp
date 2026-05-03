from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ENDPOINT = "https://api.linear.app/graphql"
DEFAULT_TEAM_KEY = "JER"
DEFAULT_PROJECT_NAME = "AI FANTUI LogicMVP · Codex Daily Lane"
DEFAULT_DESIRED_STATE = "Queued"
DEFAULT_RISK = "Low"
DEFAULT_PRIORITY = "High"


class IssueFactoryError(ValueError):
    pass


@dataclass(frozen=True)
class LiveIssueSpec:
    title: str
    repository: str
    outcome: str
    acceptance: tuple[str, ...]
    boundaries: tuple[str, ...]
    evidence_required: tuple[str, ...]
    repo_local_label: str | None = None
    desired_state: str = DEFAULT_DESIRED_STATE
    priority: str = DEFAULT_PRIORITY
    risk: str = DEFAULT_RISK
    agent_eligible: bool = True
    context: tuple[str, ...] = ()


def _clean_items(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(item.strip() for item in values if isinstance(item, str) and item.strip())


def validate_spec(spec: LiveIssueSpec) -> None:
    missing: list[str] = []
    for field_name in ("title", "repository", "outcome", "desired_state", "priority", "risk"):
        value = getattr(spec, field_name)
        if not isinstance(value, str) or not value.strip():
            missing.append(field_name)
    for field_name in ("acceptance", "boundaries", "evidence_required"):
        if not _clean_items(getattr(spec, field_name)):
            missing.append(field_name)
    if missing:
        raise IssueFactoryError(f"missing required live issue field(s): {', '.join(missing)}")


def _checklist_lines(items: tuple[str, ...]) -> str:
    return "\n".join(f"- [ ] {item}" for item in items)


def _bullet_lines(items: tuple[str, ...]) -> str:
    return "\n".join(f"- {item}" for item in items)


def collision_guard_text(repo_local_label: str | None) -> str:
    label = repo_local_label.strip() if isinstance(repo_local_label, str) and repo_local_label.strip() else None
    if not label:
        return (
            "After Linear creates this issue, always report the returned identifier as "
            "`live Linear <identifier>`. Do not shorten it to a repo-local historical "
            "JER label unless the report explicitly says `repo-local`."
        )
    return (
        "After Linear creates this issue, always report the returned identifier as "
        f"`live Linear <identifier>`. It is not the same artifact as repo-local "
        f"historical `{label}`; use `repo-local {label}` when referring to the "
        "older repository label."
    )


def issue_description(spec: LiveIssueSpec) -> str:
    validate_spec(spec)
    context_lines = _bullet_lines(_clean_items(spec.context))
    if not context_lines:
        context_lines = "- Repository is the code truth; Linear is the work-control truth."
    return "\n".join(
        [
            "## Outcome",
            "",
            spec.outcome.strip(),
            "",
            "## Context",
            "",
            context_lines,
            "",
            "## Identifier Collision Guard",
            "",
            collision_guard_text(spec.repo_local_label),
            "",
            "## Acceptance",
            "",
            _checklist_lines(_clean_items(spec.acceptance)),
            "",
            "## Boundaries",
            "",
            _checklist_lines(_clean_items(spec.boundaries)),
            "",
            "## Evidence Required",
            "",
            _checklist_lines(_clean_items(spec.evidence_required)),
            "",
            "## Metadata",
            "",
            f"- Repository: {spec.repository.strip()}",
            f"- Desired state: {spec.desired_state.strip()}",
            f"- Priority: {spec.priority.strip()}",
            f"- Risk: {spec.risk.strip()}",
            f"- Agent eligible: {'Yes' if spec.agent_eligible else 'No'}",
            "",
        ]
    )


def priority_to_linear_value(priority: str) -> int:
    normalized = priority.strip().lower()
    if normalized in {"urgent", "critical"}:
        return 1
    if normalized == "high":
        return 2
    if normalized == "medium":
        return 3
    if normalized == "low":
        return 4
    return 0


def issue_create_input(spec: LiveIssueSpec, *, team_id: str, project_id: str | None = None) -> dict[str, Any]:
    validate_spec(spec)
    payload: dict[str, Any] = {
        "teamId": team_id,
        "title": spec.title.strip(),
        "description": issue_description(spec),
        "priority": priority_to_linear_value(spec.priority),
    }
    if project_id:
        payload["projectId"] = project_id
    return payload


def dry_run_payload(
    spec: LiveIssueSpec,
    *,
    team_key: str = DEFAULT_TEAM_KEY,
    project_name: str = DEFAULT_PROJECT_NAME,
) -> dict[str, Any]:
    return {
        "ok": True,
        "dry_run": True,
        "team_key": team_key,
        "project_name": project_name,
        "title": spec.title.strip(),
        "description": issue_description(spec),
        "write_requires_confirm": True,
        "credential_source": "environment",
        "helper_contract": {
            "creates_issue": True,
            "comments": False,
            "state_transitions": False,
            "agent_spawning": False,
            "secret_persistence": False,
        },
        "next_action": "Rerun with --confirm-write to create the live Linear issue.",
    }


def auth_header(environ: dict[str, str] | None = None) -> str | None:
    env = environ if environ is not None else os.environ
    if env.get("LINEAR_API_KEY"):
        return env["LINEAR_API_KEY"]
    if env.get("LINEAR_OAUTH_TOKEN"):
        return f"Bearer {env['LINEAR_OAUTH_TOKEN']}"
    if env.get("LINEAR_TOKEN"):
        token = env["LINEAR_TOKEN"]
        return token if token.lower().startswith("bearer ") else f"Bearer {token}"
    return None


def graphql_request(
    query: str,
    variables: dict[str, Any] | None = None,
    *,
    endpoint: str = ENDPOINT,
    environ: dict[str, str] | None = None,
    timeout: int = 20,
) -> dict[str, Any]:
    auth = auth_header(environ)
    if not auth:
        raise RuntimeError("No Linear credential found. Run `source ~/.zshrc` or export LINEAR_API_KEY.")
    req = urllib.request.Request(
        endpoint,
        data=json.dumps({"query": query, "variables": variables or {}}).encode("utf-8"),
        headers={
            "Authorization": auth,
            "Content-Type": "application/json",
            "User-Agent": "ai-fantui-linear-live-issue-factory/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Linear HTTP {exc.code}: {raw}") from exc
    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"], ensure_ascii=False))
    return payload.get("data") or {}


def resolve_linear_context(
    *,
    team_key: str,
    project_name: str | None,
    graphql: Callable[[str, dict[str, Any] | None], dict[str, Any]] = graphql_request,
) -> dict[str, Any]:
    data = graphql(
        """
        query LiveIssueFactoryContext {
          teams(first: 50) {
            nodes {
              id key name
              projects(first: 50) { nodes { id name state url } }
            }
          }
        }
        """,
        None,
    )
    teams = data.get("teams", {}).get("nodes", [])
    selected_team = next(
        (team for team in teams if str(team.get("key", "")).lower() == team_key.lower()),
        None,
    )
    if not selected_team:
        raise RuntimeError(f"Linear team not found: {team_key}")
    selected_project = None
    if project_name:
        selected_project = next(
            (
                project
                for project in selected_team.get("projects", {}).get("nodes", [])
                if project.get("name") == project_name
            ),
            None,
        )
        if not selected_project:
            raise RuntimeError(f"Linear project not found under {team_key}: {project_name}")
    return {"team": selected_team, "project": selected_project}


def create_live_issue(
    spec: LiveIssueSpec,
    *,
    team_key: str = DEFAULT_TEAM_KEY,
    project_name: str = DEFAULT_PROJECT_NAME,
    graphql: Callable[[str, dict[str, Any] | None], dict[str, Any]] = graphql_request,
) -> dict[str, Any]:
    context = resolve_linear_context(team_key=team_key, project_name=project_name, graphql=graphql)
    issue_input = issue_create_input(
        spec,
        team_id=context["team"]["id"],
        project_id=context["project"]["id"] if context.get("project") else None,
    )
    data = graphql(
        """
        mutation LiveIssueFactoryCreate($input: IssueCreateInput!) {
          issueCreate(input: $input) {
            success
            issue { id identifier title url state { id name type } project { id name } }
          }
        }
        """,
        {"input": issue_input},
    )
    result = data.get("issueCreate") or {}
    return {
        "ok": bool(result.get("success")),
        "dry_run": False,
        "team": {"id": context["team"]["id"], "key": context["team"]["key"], "name": context["team"]["name"]},
        "project": context.get("project"),
        "issue": result.get("issue"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create live Linear issues from a guarded repo-local template.")
    parser.add_argument("--team-key", default=DEFAULT_TEAM_KEY)
    parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)
    parser.add_argument("--title", required=True)
    parser.add_argument("--repository", default=str(Path.cwd()))
    parser.add_argument("--outcome", required=True)
    parser.add_argument("--acceptance", action="append", default=[])
    parser.add_argument("--boundary", action="append", default=[])
    parser.add_argument("--evidence-required", action="append", default=[])
    parser.add_argument("--context", action="append", default=[])
    parser.add_argument("--repo-local-label")
    parser.add_argument("--desired-state", default=DEFAULT_DESIRED_STATE)
    parser.add_argument("--priority", default=DEFAULT_PRIORITY)
    parser.add_argument("--risk", default=DEFAULT_RISK)
    parser.add_argument("--agent-eligible", choices=("yes", "no"), default="yes")
    parser.add_argument("--confirm-write", action="store_true")
    return parser


def spec_from_args(args: argparse.Namespace) -> LiveIssueSpec:
    return LiveIssueSpec(
        title=args.title,
        repository=args.repository,
        outcome=args.outcome,
        acceptance=tuple(args.acceptance),
        boundaries=tuple(args.boundary),
        evidence_required=tuple(args.evidence_required),
        context=tuple(args.context),
        repo_local_label=args.repo_local_label,
        desired_state=args.desired_state,
        priority=args.priority,
        risk=args.risk,
        agent_eligible=args.agent_eligible == "yes",
    )


def emit(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        spec = spec_from_args(args)
        if not args.confirm_write:
            emit(dry_run_payload(spec, team_key=args.team_key, project_name=args.project_name))
            return 0
        emit(create_live_issue(spec, team_key=args.team_key, project_name=args.project_name))
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI reports machine-readable failure.
        emit({"ok": False, "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
