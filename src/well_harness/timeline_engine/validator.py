"""JSON payload → Timeline parsing with explicit error reporting."""

from __future__ import annotations

from typing import Any

from well_harness.timeline_engine.schema import (
    EVENT_KINDS,
    FaultScheduleEntry,
    Timeline,
    TimelineEvent,
)


class ValidationError(ValueError):
    """Structured validation error carrying the failing field path."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")
        self.field = field
        self.message = message


def _type_label(expected_type) -> str:
    if isinstance(expected_type, tuple):
        return " or ".join(t.__name__ for t in expected_type)
    return expected_type.__name__


def _require(payload: dict, key: str, expected_type, field: str) -> Any:
    if key not in payload:
        raise ValidationError(field, f"required key {key!r} missing")
    value = payload[key]
    # Reject bool where numeric is expected (Python's bool is int).
    if expected_type in (int, float) or (
        isinstance(expected_type, tuple) and expected_type == (int, float)
    ):
        if isinstance(value, bool) or not isinstance(value, expected_type):
            raise ValidationError(
                field, f"expected {_type_label(expected_type)}, got {type(value).__name__}"
            )
        return value
    if not isinstance(value, expected_type):
        raise ValidationError(
            field, f"expected {_type_label(expected_type)}, got {type(value).__name__}"
        )
    return value


def _parse_event(raw: dict, idx: int) -> TimelineEvent:
    field = f"events[{idx}]"
    if not isinstance(raw, dict):
        raise ValidationError(field, "event must be an object")

    t_s = raw.get("t_s")
    if not isinstance(t_s, (int, float)):
        raise ValidationError(f"{field}.t_s", "must be a number")
    if t_s < 0:
        raise ValidationError(f"{field}.t_s", "must be non-negative")

    kind = raw.get("kind")
    if kind not in EVENT_KINDS:
        raise ValidationError(f"{field}.kind", f"must be one of {EVENT_KINDS}")

    target = raw.get("target", "")
    if not isinstance(target, str):
        raise ValidationError(f"{field}.target", "must be a string")

    value = raw.get("value")
    duration_s = raw.get("duration_s")
    if duration_s is not None and not isinstance(duration_s, (int, float)):
        raise ValidationError(f"{field}.duration_s", "must be a number or null")
    if kind == "ramp_input" and (duration_s is None or duration_s <= 0):
        raise ValidationError(
            f"{field}.duration_s", "ramp_input requires positive duration_s"
        )

    phase = raw.get("phase", "")
    if not isinstance(phase, str):
        raise ValidationError(f"{field}.phase", "must be a string")
    note = raw.get("note", "")
    if not isinstance(note, str):
        raise ValidationError(f"{field}.note", "must be a string")

    return TimelineEvent(
        t_s=float(t_s),
        kind=kind,
        target=target,
        value=value,
        duration_s=float(duration_s) if duration_s is not None else None,
        phase=phase,
        note=note,
    )


def _parse_static_schedule_entry(
    raw: dict, duration_s: float, idx: int
) -> FaultScheduleEntry:
    field = f"fault_schedule[{idx}]"
    if not isinstance(raw, dict):
        raise ValidationError(field, "must be an object")
    node_id = raw.get("node_id")
    if not isinstance(node_id, str) or not node_id:
        raise ValidationError(f"{field}.node_id", "required non-empty string")
    fault_type = raw.get("fault_type", "")
    if not isinstance(fault_type, str):
        raise ValidationError(f"{field}.fault_type", "must be a string")
    start_s = raw.get("start_s", 0.0)
    end_s = raw.get("end_s", duration_s)
    if not isinstance(start_s, (int, float)):
        raise ValidationError(f"{field}.start_s", "must be a number")
    if not isinstance(end_s, (int, float)):
        raise ValidationError(f"{field}.end_s", "must be a number")
    if end_s <= start_s:
        raise ValidationError(field, f"end_s ({end_s}) must be > start_s ({start_s})")
    return FaultScheduleEntry(
        node_id=node_id,
        fault_type=fault_type,
        start_s=float(start_s),
        end_s=float(end_s),
    )


def parse_timeline(payload: dict) -> Timeline:
    """Parse a JSON-decoded dict into a Timeline, raising ValidationError on malformed input."""
    if not isinstance(payload, dict):
        raise ValidationError("<root>", "payload must be an object")

    system = _require(payload, "system", str, "system")
    if system not in ("fantui", "c919-etras"):
        raise ValidationError(
            "system", f"must be 'fantui' or 'c919-etras'; got {system!r}"
        )

    step_s = _require(payload, "step_s", (int, float), "step_s")  # type: ignore[arg-type]
    if step_s <= 0:
        raise ValidationError("step_s", "must be positive")

    duration_s = _require(payload, "duration_s", (int, float), "duration_s")  # type: ignore[arg-type]
    if duration_s <= 0:
        raise ValidationError("duration_s", "must be positive")

    initial_inputs = payload.get("initial_inputs", {})
    if not isinstance(initial_inputs, dict):
        raise ValidationError("initial_inputs", "must be an object")

    raw_events = payload.get("events", [])
    if not isinstance(raw_events, list):
        raise ValidationError("events", "must be a list")
    events = [_parse_event(ev, i) for i, ev in enumerate(raw_events)]

    # Events must be in non-decreasing t_s order. We sort them stably
    # to be forgiving but warn nothing — stable sort preserves user
    # authoring order for simultaneous events.
    events.sort(key=lambda e: e.t_s)

    raw_schedule = payload.get("fault_schedule", [])
    if not isinstance(raw_schedule, list):
        raise ValidationError("fault_schedule", "must be a list")
    fault_schedule = [
        _parse_static_schedule_entry(entry, float(duration_s), i)
        for i, entry in enumerate(raw_schedule)
    ]

    return Timeline(
        system=system,  # type: ignore[arg-type]
        step_s=float(step_s),
        duration_s=float(duration_s),
        initial_inputs=dict(initial_inputs),
        events=events,
        fault_schedule=fault_schedule,
        title=str(payload.get("title", "")),
        description=str(payload.get("description", "")),
    )
