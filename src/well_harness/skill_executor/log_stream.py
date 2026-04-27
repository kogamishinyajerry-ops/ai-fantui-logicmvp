"""P51-02 — in-memory log stream for the workbench Live Log Panel.

Why an in-memory ring buffer instead of journald / syslog / log
files: the only consumer is the workbench dashboard's Live Log
Panel, and the only goal is "let a demo observer see what the
executor is doing right now". A 500-entry deque holds the last few
seconds to a few minutes of activity (depending on event rate)
which is exactly the window an observer cares about. Persistence
is handled separately by `audit.py` (the per-execution JSON file)
and `events` on each ExecutionRecord.

Producers: orchestrator / planner / test_runner / git_ops call
`push(phase=..., level=..., message=...)` at key inflection points
(state transitions, edit applications, test runs, git commits).

Consumer: SSE endpoint `/api/workbench/log-stream` reads
`events_since(cursor)` in a polling loop and pushes new entries to
the browser. The browser renders them in a terminal-style panel.

Thread safety: pytest runs orchestrator integration tests under
ThreadingHTTPServer; multiple concurrent execute_proposal calls
will all push into the same buffer. Use a Lock around mutations.
"""

from __future__ import annotations

import collections
import dataclasses
import threading
from datetime import datetime, timezone


_RING_BUFFER_MAX = 500


@dataclasses.dataclass(frozen=True)
class LogEntry:
    """One streamed log line. Frozen so a consumer can't accidentally
    mutate the buffer's stored copy."""

    seq: int
    ts: str
    phase: str
    level: str  # "info" | "warn" | "error"
    message: str

    def to_json(self) -> dict:
        return {
            "seq": self.seq,
            "ts": self.ts,
            "phase": self.phase,
            "level": self.level,
            "message": self.message,
        }


_lock = threading.Lock()
_buffer: collections.deque[LogEntry] = collections.deque(
    maxlen=_RING_BUFFER_MAX
)
_seq_counter = 0


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def push(*, phase: str, level: str = "info", message: str) -> LogEntry:
    """Append a new entry. Truncates message to 500 chars to keep
    the SSE payload bounded — most events are short status lines,
    not full stack traces. Returns the entry so callers can read
    its seq if they want to correlate."""
    global _seq_counter
    truncated = (message or "")[:500]
    with _lock:
        _seq_counter += 1
        entry = LogEntry(
            seq=_seq_counter,
            ts=_now_iso(),
            phase=phase or "",
            level=level or "info",
            message=truncated,
        )
        _buffer.append(entry)
        return entry


def events_since(cursor: int) -> list[LogEntry]:
    """Return entries with seq > cursor, in chronological order.
    Cursor=0 returns the entire buffer (the consumer's first call).
    """
    with _lock:
        # deque iteration is O(n); buffer is bounded at 500, so this
        # is fine for SSE poll cadence (every ~0.5s).
        return [e for e in _buffer if e.seq > cursor]


def latest_seq() -> int:
    """Highest seq currently in the buffer (or 0 if empty). The SSE
    endpoint uses this to send a heartbeat cursor when the consumer
    has caught up."""
    with _lock:
        if not _buffer:
            return 0
        return _buffer[-1].seq


def buffer_size() -> int:
    """Current ring-buffer occupancy. Used by tests + diagnostics."""
    with _lock:
        return len(_buffer)


def clear() -> None:
    """Test-only reset. Production code never clears the buffer."""
    global _seq_counter
    with _lock:
        _buffer.clear()
        _seq_counter = 0
