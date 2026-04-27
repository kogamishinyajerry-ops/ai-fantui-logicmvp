"""Forensics bundle — zip a snapshot of skill_executor state for
offline inspection, sharing with a colleague, or attaching to an
incident review (P50-10).

Why this exists: P50-09's webhook pings an oncall when something
breaks. Their first move is "what was the system doing at the
moment this fired?" Without a bundle, they'd have to scp /
manually copy individual audit JSONs + the slo_history file.
This endpoint hands them a single tarball that reproduces the
dashboard state.

Bundle layout:

    forensics_<exec_id_window>_<utc_iso>.zip
    ├── manifest.json              # bundle metadata
    ├── README.txt                 # human-readable hand-off
    ├── audits/
    │   ├── EXEC-...json           # one file per audit included
    │   └── ...
    └── slo_history.jsonl          # full transition log (no filter)

Filtering:
  - `since` (ISO timestamp): drop audits whose started_at is older
    than this. Default None → keep all.
  - `limit`: cap on number of audits included (newest first).
    Default 100.

Why slo_history is unfiltered: the timeline file is small (one
line per real transition), and seeing the full history puts the
incident in context. An audit dir with 10K records would produce
a giant zip; the audit filter exists for that, not for the
transition log.

What this is NOT:
  - A backup tool. There's no recovery semantics here — the
    bundle is for forensics, not restoration.
  - Streaming. The zip is built in memory before returning. For
    a single-engineer dashboard with <10K audits this is fine;
    if the dataset grows orders of magnitude we'd revisit.
"""

from __future__ import annotations

import dataclasses
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from well_harness.skill_executor.slo_history import SLO_HISTORY_FILENAME


# Folder names inside the zip — string-stable so consumers can
# script around them.
BUNDLE_AUDITS_DIR: str = "audits"
BUNDLE_MANIFEST_NAME: str = "manifest.json"
BUNDLE_README_NAME: str = "README.txt"
BUNDLE_HISTORY_NAME: str = "slo_history.jsonl"


@dataclasses.dataclass
class BundleManifest:
    """Top-level metadata in the zip's manifest.json. Lets a
    consumer answer 'what's in this file' without unzipping
    everything."""

    created_at: str           # ISO-8601 UTC of bundle creation
    audit_count: int          # number of audit JSONs included
    history_line_count: int   # number of slo_history lines included
    since_filter: str | None  # echo of caller's `since` arg
    limit_filter: int | None  # echo of caller's `limit` arg
    audit_dir_name: str       # the source dir name (audit_dir)
    bundle_format_version: str = "p50-10"

    def to_json(self) -> dict:
        return dataclasses.asdict(self)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _filename_safe_iso() -> str:
    """Filename-friendly ISO (no colons, which break Windows
    filesystems and most consumer-side handling)."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def default_bundle_filename() -> str:
    """`forensics_<utc>.zip` — what the HTTP endpoint suggests as
    a default download filename."""
    return f"forensics_{_filename_safe_iso()}.zip"


def _selected_audits(
    audit_dir: Path,
    *,
    since: str | None,
    limit: int | None,
) -> list[Path]:
    """Pick which audit JSONs end up in the zip. Newest-first
    (mirrors list_audits ordering); apply `since` cutoff if given;
    truncate to `limit` after that."""
    if not audit_dir.is_dir():
        return []
    candidates = sorted(audit_dir.glob("EXEC-*.json"), reverse=True)
    if since:
        cutoff = since.strip()
        kept: list[Path] = []
        for path in candidates:
            try:
                with path.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
            except (OSError, json.JSONDecodeError):
                # A corrupt audit file shouldn't block the bundle —
                # skip and continue. The download path is best-effort.
                continue
            started = str(raw.get("started_at") or "").strip()
            # Lexical compare on ISO-8601 Z timestamps is correct
            # since they're all UTC + fixed-width; avoids parsing.
            if started and started >= cutoff:
                kept.append(path)
        candidates = kept
    if limit is not None and limit >= 0:
        candidates = candidates[:limit]
    return candidates


def _read_history(audit_dir: Path) -> tuple[bytes, int]:
    """Return (raw bytes, line count) for slo_history.jsonl, or
    (b"", 0) when missing. Counted by newlines so we can record
    the value in the manifest without re-parsing."""
    path = audit_dir / SLO_HISTORY_FILENAME
    if not path.is_file():
        return b"", 0
    try:
        data = path.read_bytes()
    except OSError:
        return b"", 0
    line_count = sum(
        1 for line in data.splitlines() if line.strip()
    )
    return data, line_count


def _readme_text(manifest: BundleManifest) -> str:
    """Human-readable orientation. Kept short — operators want
    the layout, not a treatise."""
    return (
        "skill_executor forensics bundle\n"
        "================================\n"
        f"Generated: {manifest.created_at}\n"
        f"Format:    {manifest.bundle_format_version}\n"
        f"Audits:    {manifest.audit_count}\n"
        f"History:   {manifest.history_line_count} lines\n"
        f"Source:    {manifest.audit_dir_name}\n"
        "\n"
        "Layout:\n"
        f"  {BUNDLE_MANIFEST_NAME}    bundle metadata (this matches README)\n"
        f"  {BUNDLE_README_NAME}      this file\n"
        f"  {BUNDLE_AUDITS_DIR}/        ExecutionRecord JSONs\n"
        f"  {BUNDLE_HISTORY_NAME}   SLO transition log (newest-last)\n"
        "\n"
        "Each audit is independently parseable JSON. The slo_history\n"
        "file is JSONL — one transition per line. The manifest carries\n"
        "the filters that were applied so the recipient knows the\n"
        "scope (since/limit).\n"
    )


def build_bundle(
    audit_dir: Path,
    *,
    since: str | None = None,
    limit: int | None = 100,
) -> tuple[bytes, BundleManifest]:
    """Zip a forensics snapshot of `audit_dir`. Returns
    (zip_bytes, manifest). Pure of HTTP — the caller (demo_server)
    is responsible for setting Content-Type + Content-Disposition.

    Args:
      audit_dir: directory containing EXEC-*.json + slo_history.jsonl
      since: optional ISO timestamp; drop audits older than this
      limit: cap on number of audits (newest-first). None means
             no cap.

    Empty input is fine — manifest reports 0 counts and the zip
    contains just the manifest + README + an empty history file.
    """
    audit_paths = _selected_audits(
        audit_dir, since=since, limit=limit,
    )
    history_bytes, history_lines = _read_history(audit_dir)

    manifest = BundleManifest(
        created_at=_now_iso(),
        audit_count=len(audit_paths),
        history_line_count=history_lines,
        since_filter=since,
        limit_filter=limit,
        audit_dir_name=audit_dir.name,
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            BUNDLE_MANIFEST_NAME,
            json.dumps(manifest.to_json(), indent=2, ensure_ascii=False),
        )
        zf.writestr(BUNDLE_README_NAME, _readme_text(manifest))
        for path in audit_paths:
            try:
                arcname = f"{BUNDLE_AUDITS_DIR}/{path.name}"
                zf.write(path, arcname=arcname)
            except OSError:
                # Skip individual unreadable files; manifest count
                # already reflects what we INTENDED to include, but
                # corruption mid-bundle shouldn't fail the download.
                # Future P50-10b could add a `partial_failures`
                # field if this turns out to matter in practice.
                continue
        zf.writestr(BUNDLE_HISTORY_NAME, history_bytes)

    return buf.getvalue(), manifest
