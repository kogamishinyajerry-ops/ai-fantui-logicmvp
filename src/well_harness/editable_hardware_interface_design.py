"""Sandbox hardware/interface design contracts for editable workbench drafts.

This model records candidate LRU, cable, connector, port, pin, and signal
binding evidence. It is an engineering design artifact only; it never changes
controller truth, adapter truth level, DAL/PSSA status, or runtime evaluation
semantics.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import jsonschema


EDITABLE_HARDWARE_INTERFACE_DESIGN_SCHEMA_ID = (
    "https://well-harness.local/json_schema/editable_hardware_interface_design_v1.schema.json"
)
EDITABLE_HARDWARE_INTERFACE_DESIGN_KIND = "well-harness-editable-hardware-interface-design"
EDITABLE_HARDWARE_INTERFACE_DESIGN_VERSION = 1
EVIDENCE_GAP_SENTINEL = "evidence_gap"
ALLOWED_EVIDENCE_STATUSES = ("recorded", "ui_draft", "evidence_gap", "not_recorded")


class EditableHardwareInterfaceDesignValidationError(ValueError):
    """Raised when a sandbox hardware interface design violates v1 rules."""


@dataclass(frozen=True)
class LruDesignRecord:
    id: str
    display_name: str
    evidence_status: str
    source_ref: str
    quantity_per_engine: int | float | None = None
    part_number: str | None = None
    location: str | None = None
    failure_rate_per_hour: float | None = None


@dataclass(frozen=True)
class CableDesignRecord:
    id: str
    display_name: str
    source_lru_id: str
    target_lru_id: str
    evidence_status: str
    source_ref: str
    cable_type: str | None = None


@dataclass(frozen=True)
class ConnectorDesignRecord:
    id: str
    display_name: str
    lru_id: str
    connector_type: str
    evidence_status: str
    source_ref: str


@dataclass(frozen=True)
class PortDesignRecord:
    id: str
    display_name: str
    connector_id: str
    direction: str
    evidence_status: str
    source_ref: str
    signal_id: str | None = None
    value_type: str = "unknown"


@dataclass(frozen=True)
class PinDesignRecord:
    id: str
    connector_id: str
    pin_number: str
    port_id: str
    evidence_status: str
    source_ref: str
    signal_id: str | None = None


@dataclass(frozen=True)
class SignalBindingDesignRecord:
    id: str
    signal_id: str
    source_port_id: str
    target_port_id: str
    cable_id: str
    evidence_status: str
    truth_effect: str
    source_ref: str
    redundancy_status: str = "unknown"


@dataclass(frozen=True)
class EvidenceGapRecord:
    id: str
    subject_id: str
    field_ref: str
    severity: str
    impact: str
    proposed_fill: str
    source_ref: str


@dataclass(frozen=True)
class EditableHardwareInterfaceDesign:
    schema_id: str
    kind: str
    version: int
    design_id: str
    system_id: str
    candidate_state: str
    truth_level_impact: str
    dal_pssa_impact: str
    controller_truth_modified: bool
    runtime_truth_effect: str
    lrus: tuple[LruDesignRecord, ...]
    cables: tuple[CableDesignRecord, ...]
    connectors: tuple[ConnectorDesignRecord, ...]
    ports: tuple[PortDesignRecord, ...]
    pins: tuple[PinDesignRecord, ...]
    bindings: tuple[SignalBindingDesignRecord, ...]
    evidence_gaps: tuple[EvidenceGapRecord, ...]
    evidence_metadata: dict[str, Any]
    boundaries: dict[str, Any]
    payload_hash: str


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_schema() -> dict[str, Any]:
    path = (
        _project_root()
        / "docs"
        / "json_schema"
        / "editable_hardware_interface_design_v1.schema.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_validate(payload: dict[str, Any]) -> None:
    schema = _load_schema()
    try:
        jsonschema.Draft202012Validator(schema).validate(payload)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise EditableHardwareInterfaceDesignValidationError(
            f"schema validation failed{location}: {exc.message}"
        ) from exc


def _copy_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(payload, ensure_ascii=True))


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def editable_hardware_interface_design_hash(payload: Mapping[str, Any]) -> str:
    """Return a deterministic hash for sandbox design provenance."""
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def editable_hardware_interface_schema_hash() -> str:
    """Return a deterministic hash for the v1 JSON schema artifact."""
    return editable_hardware_interface_design_hash(_load_schema())


def _unique_ids(items: list[dict[str, Any]], label: str) -> set[str]:
    ids = [str(item["id"]) for item in items]
    duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
    if duplicates:
        raise EditableHardwareInterfaceDesignValidationError(
            f"duplicate {label} ids: {duplicates}"
        )
    return set(ids)


def _validate_global_ids(payload: dict[str, Any]) -> None:
    seen: dict[str, str] = {}
    for collection in ("lrus", "cables", "connectors", "ports", "pins", "bindings", "evidence_gaps"):
        for item in payload[collection]:
            item_id = str(item["id"])
            previous = seen.get(item_id)
            if previous is not None:
                raise EditableHardwareInterfaceDesignValidationError(
                    f"duplicate id across {previous} and {collection}: {item_id}"
                )
            seen[item_id] = collection


def _ref_exists_or_gap(
    *,
    value: str,
    known_ids: set[str],
    field_name: str,
    owner_id: str,
    evidence_status: str,
) -> None:
    if value == EVIDENCE_GAP_SENTINEL:
        if evidence_status != EVIDENCE_GAP_SENTINEL:
            raise EditableHardwareInterfaceDesignValidationError(
                f"{owner_id}.{field_name} is evidence_gap but evidence_status is {evidence_status}"
            )
        return
    if value not in known_ids:
        raise EditableHardwareInterfaceDesignValidationError(
            f"{owner_id}.{field_name} references missing id {value}"
        )


def _validate_truth_boundaries(payload: dict[str, Any]) -> None:
    expected = {
        "candidate_state": "sandbox_candidate",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "runtime_truth_effect": "none",
    }
    for field_name, expected_value in expected.items():
        if payload[field_name] != expected_value:
            raise EditableHardwareInterfaceDesignValidationError(
                f"{field_name} must be {expected_value}"
            )
    if payload["controller_truth_modified"] is not False:
        raise EditableHardwareInterfaceDesignValidationError(
            "controller_truth_modified must be false"
        )
    boundaries = payload["boundaries"]
    boundary_expected = {
        "runtime_scope": "sandbox_only",
        "hardware_truth_effect": "none",
        "certified_truth_modified": False,
        "dal_pssa_impact": "none",
    }
    for field_name, expected_value in boundary_expected.items():
        if boundaries[field_name] != expected_value:
            raise EditableHardwareInterfaceDesignValidationError(
                f"boundaries.{field_name} must be {expected_value}"
            )


def validate_editable_hardware_interface_design(payload: Mapping[str, Any]) -> None:
    """Validate schema plus cross-reference invariants for sandbox hardware designs."""
    copied = _copy_payload(payload)
    _schema_validate(copied)
    _validate_truth_boundaries(copied)

    lru_ids = _unique_ids(copied["lrus"], "lru")
    cable_ids = _unique_ids(copied["cables"], "cable")
    connector_ids = _unique_ids(copied["connectors"], "connector")
    port_ids = _unique_ids(copied["ports"], "port")
    _unique_ids(copied["pins"], "pin")
    _unique_ids(copied["bindings"], "binding")
    _unique_ids(copied["evidence_gaps"], "evidence gap")
    _validate_global_ids(copied)

    for lru in copied["lrus"]:
        if lru["evidence_status"] not in ALLOWED_EVIDENCE_STATUSES:
            raise EditableHardwareInterfaceDesignValidationError(
                f"lru {lru['id']} has invalid evidence_status {lru['evidence_status']}"
            )

    for cable in copied["cables"]:
        _ref_exists_or_gap(
            value=str(cable["source_lru_id"]),
            known_ids=lru_ids,
            field_name="source_lru_id",
            owner_id=str(cable["id"]),
            evidence_status=str(cable["evidence_status"]),
        )
        _ref_exists_or_gap(
            value=str(cable["target_lru_id"]),
            known_ids=lru_ids,
            field_name="target_lru_id",
            owner_id=str(cable["id"]),
            evidence_status=str(cable["evidence_status"]),
        )

    for connector in copied["connectors"]:
        _ref_exists_or_gap(
            value=str(connector["lru_id"]),
            known_ids=lru_ids,
            field_name="lru_id",
            owner_id=str(connector["id"]),
            evidence_status=str(connector["evidence_status"]),
        )

    for port in copied["ports"]:
        _ref_exists_or_gap(
            value=str(port["connector_id"]),
            known_ids=connector_ids,
            field_name="connector_id",
            owner_id=str(port["id"]),
            evidence_status=str(port["evidence_status"]),
        )

    port_to_connector = {str(port["id"]): str(port["connector_id"]) for port in copied["ports"]}
    for pin in copied["pins"]:
        _ref_exists_or_gap(
            value=str(pin["connector_id"]),
            known_ids=connector_ids,
            field_name="connector_id",
            owner_id=str(pin["id"]),
            evidence_status=str(pin["evidence_status"]),
        )
        _ref_exists_or_gap(
            value=str(pin["port_id"]),
            known_ids=port_ids,
            field_name="port_id",
            owner_id=str(pin["id"]),
            evidence_status=str(pin["evidence_status"]),
        )
        if (
            pin["port_id"] != EVIDENCE_GAP_SENTINEL
            and pin["connector_id"] != EVIDENCE_GAP_SENTINEL
            and port_to_connector[str(pin["port_id"])] != pin["connector_id"]
        ):
            raise EditableHardwareInterfaceDesignValidationError(
                f"pin {pin['id']} connector_id must match its port connector_id"
            )

    for binding in copied["bindings"]:
        if binding["truth_effect"] != "none":
            raise EditableHardwareInterfaceDesignValidationError(
                f"binding {binding['id']} truth_effect must be none"
            )
        _ref_exists_or_gap(
            value=str(binding["source_port_id"]),
            known_ids=port_ids,
            field_name="source_port_id",
            owner_id=str(binding["id"]),
            evidence_status=str(binding["evidence_status"]),
        )
        _ref_exists_or_gap(
            value=str(binding["target_port_id"]),
            known_ids=port_ids,
            field_name="target_port_id",
            owner_id=str(binding["id"]),
            evidence_status=str(binding["evidence_status"]),
        )
        _ref_exists_or_gap(
            value=str(binding["cable_id"]),
            known_ids=cable_ids,
            field_name="cable_id",
            owner_id=str(binding["id"]),
            evidence_status=str(binding["evidence_status"]),
        )


def canonicalize_editable_hardware_interface_design(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return a JSON-shaped canonical copy after sandbox validation."""
    copied = _copy_payload(payload)
    validate_editable_hardware_interface_design(copied)
    return json.loads(_canonical_json(copied))


def _record(cls: type[Any], raw: Mapping[str, Any]) -> Any:
    field_names = {field.name for field in dataclasses.fields(cls)}
    return cls(**{key: value for key, value in raw.items() if key in field_names})


def _to_design(payload: dict[str, Any]) -> EditableHardwareInterfaceDesign:
    return EditableHardwareInterfaceDesign(
        schema_id=str(payload["$schema"]),
        kind=str(payload["kind"]),
        version=int(payload["version"]),
        design_id=str(payload["design_id"]),
        system_id=str(payload["system_id"]),
        candidate_state=str(payload["candidate_state"]),
        truth_level_impact=str(payload["truth_level_impact"]),
        dal_pssa_impact=str(payload["dal_pssa_impact"]),
        controller_truth_modified=bool(payload["controller_truth_modified"]),
        runtime_truth_effect=str(payload["runtime_truth_effect"]),
        lrus=tuple(_record(LruDesignRecord, item) for item in payload["lrus"]),
        cables=tuple(_record(CableDesignRecord, item) for item in payload["cables"]),
        connectors=tuple(_record(ConnectorDesignRecord, item) for item in payload["connectors"]),
        ports=tuple(_record(PortDesignRecord, item) for item in payload["ports"]),
        pins=tuple(_record(PinDesignRecord, item) for item in payload["pins"]),
        bindings=tuple(_record(SignalBindingDesignRecord, item) for item in payload["bindings"]),
        evidence_gaps=tuple(_record(EvidenceGapRecord, item) for item in payload["evidence_gaps"]),
        evidence_metadata=dict(payload["evidence_metadata"]),
        boundaries=dict(payload["boundaries"]),
        payload_hash=editable_hardware_interface_design_hash(payload),
    )


def _read_payload(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Hardware interface design file not found: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            import yaml

            raw = yaml.safe_load(text)
        else:
            raw = json.loads(text)
    except Exception as exc:  # pragma: no cover - parser messages are dependency-specific
        raise EditableHardwareInterfaceDesignValidationError(
            f"failed to parse hardware interface design {path}: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise EditableHardwareInterfaceDesignValidationError(
            f"hardware interface design must be a JSON object, got {type(raw).__name__}"
        )
    return raw


def load_editable_hardware_interface_design(
    path: str | Path,
    *,
    validate: bool = True,
) -> EditableHardwareInterfaceDesign:
    """Load a JSON/YAML sandbox hardware interface design from disk."""
    payload = _read_payload(Path(path))
    if validate:
        payload = canonicalize_editable_hardware_interface_design(payload)
    return _to_design(payload)


@lru_cache(maxsize=32)
def load_editable_hardware_interface_design_cached(
    path: str,
) -> EditableHardwareInterfaceDesign:
    """Cached sandbox catalog loader keyed by absolute/relative path string."""
    return load_editable_hardware_interface_design(path, validate=True)


def clear_editable_hardware_interface_design_cache() -> None:
    """Clear the sandbox hardware interface design loader cache."""
    load_editable_hardware_interface_design_cached.cache_clear()
