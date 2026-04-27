"""P51-03 — persistent governance decision history.

Why a dedicated file instead of relying on per-execution audit
JSONs: a reviewer scrolling the workbench wants ONE list of "what
governance decisions have been made and by whom, across all
executions". Audit JSONs live one-per-exec under
`.planning/skill_executions/`; aggregating them at read time means
re-scanning a directory of 1000s of files on every dashboard
refresh, which doesn't scale. Append-on-decide → cheap O(1) reads.

The file is the SECONDARY source of truth — the canonical record
is still `record.governance_review` on the per-exec audit. If the
two ever disagree, the audit JSON wins. This file is for fast
listing and dashboard visibility; consumers needing forensic
detail should fall back to the per-exec audit.

Format: JSON Lines (one decision per line, append-only). Lets us
recover from a partial write (skip the malformed last line) and
keeps the reader simple. 500-entry tail kept in memory for fast
list reads; older lines stay on disk for audit replay.
"""

from __future__ import annotations

import dataclasses
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path


_DEFAULT_PATH_ENV = "WORKBENCH_GOVERNANCE_HISTORY_PATH"


def _resolve_path() -> Path:
    """Return the configured history file path. Default lives under
    `data/governance_decisions.jsonl` relative to the repo root so
    it survives a clean checkout (the dir is gitignored)."""
    override = os.environ.get(_DEFAULT_PATH_ENV)
    if override:
        return Path(override)
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "data" / "governance_decisions.jsonl"


@dataclasses.dataclass(frozen=True)
class DecisionEntry:
    """One row in the governance history. `verdict` carries the
    rule matches that fired — useful for showing a reviewer WHY
    the gate triggered after the fact."""

    recorded_at: str
    exec_id: str
    proposal_id: str
    decision: str  # "approved" | "rejected" | "cancelled" | "timeout"
    decided_at: str
    decided_by: str
    decision_note: str
    verdict: dict

    def to_json(self) -> dict:
        return {
            "recorded_at": self.recorded_at,
            "exec_id": self.exec_id,
            "proposal_id": self.proposal_id,
            "decision": self.decision,
            "decided_at": self.decided_at,
            "decided_by": self.decided_by,
            "decision_note": self.decision_note,
            "verdict": self.verdict,
        }

    @classmethod
    def from_json(cls, data: dict) -> "DecisionEntry":
        return cls(
            recorded_at=str(data.get("recorded_at") or ""),
            exec_id=str(data.get("exec_id") or ""),
            proposal_id=str(data.get("proposal_id") or ""),
            decision=str(data.get("decision") or ""),
            decided_at=str(data.get("decided_at") or ""),
            decided_by=str(data.get("decided_by") or ""),
            decision_note=str(data.get("decision_note") or ""),
            verdict=dict(data.get("verdict") or {}),
        )


_lock = threading.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def record_decision(
    *,
    exec_id: str,
    proposal_id: str,
    decision: str,
    decided_at: str,
    decided_by: str,
    decision_note: str,
    verdict: dict,
) -> DecisionEntry:
    """Append a decision to the history file. Creates the parent
    directory on demand. Best-effort: on IO failure we swallow the
    error (the per-exec audit JSON already captures the canonical
    record; persisting to history is supplementary)."""
    entry = DecisionEntry(
        recorded_at=_now_iso(),
        exec_id=exec_id,
        proposal_id=proposal_id,
        decision=decision,
        decided_at=decided_at,
        decided_by=decided_by,
        decision_note=decision_note,
        verdict=dict(verdict or {}),
    )
    path = _resolve_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with _lock:
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry.to_json(), ensure_ascii=False))
                fh.write("\n")
    except OSError:
        # IO failure must not break the executor. Audit JSON is
        # still the canonical record.
        pass
    return entry


def read_history(*, limit: int | None = None) -> list[DecisionEntry]:
    """Return decisions newest-first. Returns [] if the file
    doesn't exist yet (fresh deploy). Skips malformed lines so a
    partial-write tail doesn't crash the reader."""
    path = _resolve_path()
    if not path.exists():
        return []
    entries: list[DecisionEntry] = []
    try:
        with _lock:
            with path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(
                            DecisionEntry.from_json(json.loads(line))
                        )
                    except (json.JSONDecodeError, KeyError):
                        # Malformed line — skip rather than crash.
                        continue
    except OSError:
        return []
    entries.reverse()  # newest-first
    if limit is not None and limit > 0:
        return entries[:limit]
    return entries


def clear() -> None:
    """Test-only reset. Production code never clears the history."""
    path = _resolve_path()
    with _lock:
        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass
