"""Backfill audits — synthesize after-the-fact audit JSONs for
proposals that landed before P48-05's gate went into effect.

Per Q7(a) (2026-04-27): rather than have two regulatory regimes
(pre-P48 honor system + post-P48 audited), backfill the missing
audits so EVERY landed proposal has a record. Backfill records
are flagged via `audit_source=backfill` and `kind=backfill`,
and they always live in the LANDED state — they skip the
INIT→PLANNING→ASKING→… lifecycle.

What we can recover post-hoc from git + proposal JSON:
  - exec_id        (synthesized: EXEC-{landed_at}-bf{6hex})
  - proposal_id    (from input)
  - landed_sha     (from input — caller provides via git log search)
  - kind/audit_source = backfill
  - executor_version = "0.0-backfill"
  - state = LANDED
  - finished_at = the merged commit's authored timestamp
  - events = [{kind: "backfill_synthesized", note: "..."}]
  - plan = stub with rationale=("backfill — no LLM record exists")

What we CANNOT recover:
  - planner_prompt / planner_response (no LLM ran)
  - asks (the engineer approved via different mechanism)
  - tests_before / tests_after (we don't know the exact baselines)
  - branch (we know the merge SHA but not the original feature
    branch unless we parse it from the commit message)

Backfill audits pass the P48-05 gate but trigger a warning note
("audit_source=backfill — sanity-check proposal lineage manually")
so reviewers know the audit is reconstructed, not first-hand.
"""

from __future__ import annotations

import hashlib
import re
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from well_harness.skill_executor.audit import write_audit
from well_harness.skill_executor.errors import SkillExecutorError
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionEvent,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
)
from well_harness.skill_executor.states import ExecutionState


class BackfillError(SkillExecutorError):
    """Backfill could not produce a valid audit. Caller decides
    whether to fail loudly or log + skip."""


_FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def synthesize_backfill_audit(
    *,
    proposal_id: str,
    landed_sha: str,
    repo_root: Path,
    executor_version: str = "0.0-backfill",
    note: str = "",
    git_runner: callable | None = None,
) -> ExecutionRecord:
    """Build + persist a backfill ExecutionRecord for a proposal
    that landed before P48-05.

    `landed_sha` MUST be a full 40-char SHA — we use it to query
    the commit's authored timestamp so finished_at reflects when
    the change really shipped, not when this script ran.

    Returns the persisted record. Raises BackfillError if landed_sha
    is malformed or the git lookup fails.
    """
    if not _FULL_SHA_PATTERN.match(landed_sha or ""):
        raise BackfillError(
            f"landed_sha must be a 40-char hex; got {landed_sha!r}"
        )
    repo_root = Path(repo_root).resolve()

    runner = git_runner or _default_git_runner
    proc = runner(
        ["git", "show", "-s", "--format=%cI%n%s", landed_sha],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise BackfillError(
            f"git show {landed_sha} failed: "
            f"{(proc.stderr or proc.stdout).strip()}"
        )
    output = (proc.stdout or "").strip()
    parts = output.split("\n", 1)
    landed_at = parts[0] if parts else ""
    subject = parts[1] if len(parts) > 1 else ""

    # Synthesize an EXEC-id from the landed SHA so the same backfill
    # call twice produces the same id (idempotency). The hash is a
    # deterministic function of (proposal_id, landed_sha) so retries
    # don't double-write.
    exec_id = _synthetic_exec_id(proposal_id=proposal_id, landed_sha=landed_sha)

    record = ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id=proposal_id,
        kind=ExecutionKind.BACKFILL,
        audit_source=AuditSource.BACKFILL,
        started_at=landed_at or _now_iso(),
        finished_at=landed_at or _now_iso(),
        state=ExecutionState.LANDED.value,
        executor_version=executor_version,
        landed_sha=landed_sha,
        commits=[landed_sha],
        plan=PlannedChange(
            rationale=(
                "backfilled audit — no live planner record exists; "
                "this proposal landed before P48-05's gate. See git "
                f"log {landed_sha} for the actual change."
            ),
            file_edits=[],
            planner_response=(
                f"(backfill: original commit subject was {subject!r})"
                if subject
                else ""
            ),
        ),
        events=[
            ExecutionEvent(
                at=_now_iso(),
                kind="backfill_synthesized",
                note=note or f"backfilled from {landed_sha}",
            )
        ],
    )
    write_audit(record)
    return record


def _synthetic_exec_id(*, proposal_id: str, landed_sha: str) -> str:
    """Deterministic EXEC-id: same proposal+sha always produces
    the same id, so re-running backfill is idempotent.

    Format: EXEC-YYYYMMDDTHHMMSSffffff-bf{4hex}
    The 4-hex suffix is derived from sha256(proposal_id+landed_sha)
    so it's stable. The timestamp portion is current — we don't
    have the original execution time anyway, so "now" is the most
    honest representation. To preserve idempotency we also embed
    a hash of the inputs into the suffix.
    """
    digest = hashlib.sha256(
        f"{proposal_id}::{landed_sha}".encode("utf-8")
    ).hexdigest()
    # 4-hex from digest + 2-hex random salt so pattern matches
    # the canonical EXEC- regex (which requires 6 hex). The 4
    # deterministic chars guarantee idempotency for the typical
    # case while the 2-char random tail keeps the schema regex
    # happy across multiple backfill calls if we ever decide to
    # allow them.
    deterministic = digest[:6]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    # Build a stable pseudo-timestamp by hashing the digest into
    # the microsecond field, so the id is fully deterministic for
    # a given (proposal_id, landed_sha) pair.
    stable_micro = digest[6:14]  # 8 hex → 8 digits-ish
    # Fall back to current timestamp shape but replace the micro
    # portion with hash bytes. The audit-id regex requires exactly
    # 8 digits + T + 12 digits, so we synthesize a stable form.
    base = digest[:8]
    base_hex_to_decimal = "{:08d}".format(int(base, 16) % 10**8)
    micro = digest[8:14]
    micro_decimal = "{:012d}".format(int(micro, 16) % 10**12)
    # NB: deterministic id only — we don't roll random suffix
    return f"EXEC-{base_hex_to_decimal}T{micro_decimal}-{deterministic}"


def _default_git_runner(
    cmd: list[str],
    *,
    cwd: str,
    capture_output: bool,
    text: bool,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        timeout=10,
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
