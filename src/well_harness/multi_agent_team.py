"""Canonical active team roster for the multi-agent queue surfaces."""
from __future__ import annotations

from typing import Any


FIVE_AGENT_TEAM_MODE = "five_agent_context_cap"
LEGACY_ROLE_POLICY = (
    "Historical queue target_agent and milestone role labels are task categories, "
    "not additional active prompt participants."
)

ACTIVE_AGENT_TEAM: tuple[dict[str, str], ...] = (
    {
        "agent_id": "chief-engineer-orchestrator",
        "name": "ChiefEngineerOrchestrator",
        "scope": "Owns queue selection, stop conditions, and cross-surface coordination.",
    },
    {
        "agent_id": "logic-ir-repair-agent",
        "name": "LogicIRRepairAgent",
        "scope": "Handles candidate IR, state, transition, and safety-priority repairs.",
    },
    {
        "agent_id": "evidence-validation-agent",
        "name": "EvidenceValidationAgent",
        "scope": "Handles tests, simulation evidence, trace coverage, and validation proof.",
    },
    {
        "agent_id": "safety-requirements-reviewer",
        "name": "SafetyRequirementsReviewer",
        "scope": "Reviews safety findings, requirement ambiguity, and unresolved requirement risk.",
    },
    {
        "agent_id": "packaging-pr-readiness-agent",
        "name": "PackagingPRReadinessAgent",
        "scope": "Owns pathspec staging, PR readiness, browser geometry, and release evidence.",
    },
)

ACTIVE_AGENT_NAMES = frozenset(agent["name"] for agent in ACTIVE_AGENT_TEAM)


def active_agent_team_payload() -> dict[str, Any]:
    """Return a schema-ready copy of the five-agent active team definition."""
    return {
        "mode": FIVE_AGENT_TEAM_MODE,
        "team_size": len(ACTIVE_AGENT_TEAM),
        "active_agents": [dict(agent) for agent in ACTIVE_AGENT_TEAM],
        "retired_role_policy": LEGACY_ROLE_POLICY,
    }


def canonical_agent_for_text(*parts: object) -> str:
    """Map legacy task labels onto the capped five-agent active team."""
    combined = " ".join(str(part or "") for part in parts).lower()
    if any(
        marker in combined
        for marker in (
            "evidence",
            "simulation",
            "test-result",
            "test_oracle",
            "trace",
            "validation",
        )
    ):
        return "EvidenceValidationAgent"
    if any(marker in combined for marker in ("requirement", "ambiguity", "unresolved")):
        return "SafetyRequirementsReviewer"
    if any(
        marker in combined
        for marker in (
            "safety",
            "logic",
            "state",
            "transition",
            "output-command",
            "undefined-signal",
        )
    ):
        return "LogicIRRepairAgent"
    if any(
        marker in combined
        for marker in (
            "packaging",
            "pathspec",
            "preflight",
            "merge",
            "readiness",
            "pull-request",
            "status",
            "browser",
            "geometry",
        )
    ):
        return "PackagingPRReadinessAgent"
    return "ChiefEngineerOrchestrator"
