"""
Hardware schema loader for well_harness.

Loads and validates thrust-reverser hardware parameter YAML files.
These parameters are READ-ONLY reference data — they do NOT override
controller.py truth engine behavior.

Schema: docs/json_schema/hardware_schema_v1.schema.json
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any

import jsonschema

# ─── Exceptions ────────────────────────────────────────────────────────────────


class HardwareSchemaError(Exception):
    """Base exception for hardware schema loading."""

    pass


class HardwareSchemaValidationError(HardwareSchemaError):
    """Raised when hardware YAML fails schema validation."""

    pass


class HardwareSchemaNotFoundError(HardwareSchemaError, FileNotFoundError):
    """Raised when hardware YAML file does not exist."""

    pass


# ─── Dataclasses ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SensorSpec:
    unit: str
    typical_range_ft: float
    accuracy_ft: float


@dataclass(frozen=True)
class ActuatorTraSpec:
    unit: str
    min_deg: float
    max_deg: float
    nominal_deployment_rate_percent_per_s: float


@dataclass(frozen=True)
class ActuatorVDSpec:
    unit: str
    full_deploy_percent: float


@dataclass(frozen=True)
class SwitchWindowSpec:
    near_zero_deg: float
    deep_reverse_deg: float


@dataclass(frozen=True)
class LogicThresholds:
    logic1_ra_ft_threshold: float
    logic3_tra_deg_threshold: float
    deploy_90_threshold_percent: float


@dataclass(frozen=True)
class TimingSpec:
    tls_unlock_delay_s: float
    pls_unlock_delay_s: float


@dataclass(frozen=True)
class PhysicalLimits:
    reverse_travel_min_deg: float
    reverse_travel_max_deg: float
    sw1_window: SwitchWindowSpec
    sw2_window: SwitchWindowSpec


@dataclass(frozen=True)
class HardwareValueRef:
    status: str
    value: str | int | float | None


@dataclass(frozen=True)
class LruInventoryItem:
    id: str
    display_name: str
    quantity_per_engine: int | float | None
    value_status: str
    part_number: HardwareValueRef
    location: HardwareValueRef
    failure_rate_per_hour: HardwareValueRef
    source_ref: str


@dataclass(frozen=True)
class SignalCarrierBinding:
    signal_id: str
    direction: str
    source_hardware_id: str
    peer_hardware_id: str
    cable: HardwareValueRef
    connector: HardwareValueRef
    port_local: HardwareValueRef
    port_peer: HardwareValueRef
    redundancy_status: str
    evidence_status: str
    feeds_logic_nodes: tuple[str, ...]
    source_ref: str


@dataclass(frozen=True)
class ThrustReverserHardware:
    kind: str
    version: int
    system_id: str
    lru_inventory: tuple[LruInventoryItem, ...]
    signal_carrier_bindings: tuple[SignalCarrierBinding, ...]
    sensor: SensorSpec
    actuator_tra: ActuatorTraSpec
    actuator_vd: ActuatorVDSpec
    logic_thresholds: LogicThresholds
    timing: TimingSpec
    physical_limits: PhysicalLimits


# ─── Serialization ─────────────────────────────────────────────────────────────


def _hardware_to_dict(hw: ThrustReverserHardware) -> dict:
    """Convert a ThrustReverserHardware (and nested frozen dataclasses) to a plain dict."""
    import dataclasses

    def _to_dict(obj):
        if dataclasses.is_dataclass(obj):
            result = {}
            for field in dataclasses.fields(obj):
                result[field.name] = _to_dict(getattr(obj, field.name))
            return result
        if isinstance(obj, dict):
            return {k: _to_dict(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_to_dict(item) for item in obj]
        return obj

    return _to_dict(hw)


# ─── Schema resolution ────────────────────────────────────────────────────────

_SCHEMA_RESOURCE = "docs/json_schema/hardware_schema_v1.schema.json"


def _get_schema() -> dict:
    """Load hardware schema JSON from package resources.

    Schema lives at <repo-root>/docs/json_schema/hardware_schema_v1.schema.json.
    well_harness package is at <repo-root>/src/well_harness/, so we need
    pkg_root.parent.parent to reach the repo root.
    """
    try:
        import well_harness

        pkg_root = Path(well_harness.__file__).parent
        # <repo-root>/src/well_harness/ -> <repo-root>/src/ -> <repo-root>/
        schema_path = pkg_root.parent.parent / _SCHEMA_RESOURCE
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        raise HardwareSchemaError(f"Cannot load hardware schema JSON: {exc}") from exc


def _parse_value_ref(raw: dict[str, Any]) -> HardwareValueRef:
    return HardwareValueRef(
        status=str(raw["status"]),
        value=raw.get("value"),
    )


def _parse_lru_inventory(raw_items: list[dict[str, Any]] | None) -> tuple[LruInventoryItem, ...]:
    if not raw_items:
        return ()
    return tuple(
        LruInventoryItem(
            id=str(item["id"]),
            display_name=str(item["display_name"]),
            quantity_per_engine=item.get("quantity_per_engine"),
            value_status=str(item["value_status"]),
            part_number=_parse_value_ref(item["part_number"]),
            location=_parse_value_ref(item["location"]),
            failure_rate_per_hour=_parse_value_ref(item["failure_rate_per_hour"]),
            source_ref=str(item["source_ref"]),
        )
        for item in raw_items
    )


def _parse_signal_carrier_bindings(
    raw_items: list[dict[str, Any]] | None,
) -> tuple[SignalCarrierBinding, ...]:
    if not raw_items:
        return ()
    return tuple(
        SignalCarrierBinding(
            signal_id=str(item["signal_id"]),
            direction=str(item["direction"]),
            source_hardware_id=str(item["source_hardware_id"]),
            peer_hardware_id=str(item["peer_hardware_id"]),
            cable=_parse_value_ref(item["cable"]),
            connector=_parse_value_ref(item["connector"]),
            port_local=_parse_value_ref(item["port_local"]),
            port_peer=_parse_value_ref(item["port_peer"]),
            redundancy_status=str(item["redundancy_status"]),
            evidence_status=str(item["evidence_status"]),
            feeds_logic_nodes=tuple(str(node) for node in item["feeds_logic_nodes"]),
            source_ref=str(item["source_ref"]),
        )
        for item in raw_items
    )


# ─── Public API ───────────────────────────────────────────────────────────────


def load_thrust_reverser_hardware(
    config_path: str | Path,
    *,
    validate: bool = True,
) -> ThrustReverserHardware:
    """
    Load and optionally validate a thrust-reverser hardware YAML file.

    Args:
        config_path: Path to the hardware YAML file.
        validate: If True, validate YAML against hardware_schema_v1.schema.json.

    Returns:
        ThrustReverserHardware dataclass with all parameters.

    Raises:
        HardwareSchemaNotFoundError: YAML file does not exist.
        HardwareSchemaValidationError: YAML fails schema validation.
        HardwareSchemaError: Unexpected error during loading.

    Example:
        h = load_thrust_reverser_hardware("config/hardware/thrust_reverser_hardware_v1.yaml")
        print(h.logic_thresholds.logic1_ra_ft_threshold)  # 6.0
    """
    path = Path(config_path)
    if not path.is_file():
        raise HardwareSchemaNotFoundError(f"Hardware config not found: {path}")

    try:
        import yaml  # PyYAML — optional dependency

        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError as exc:
        raise HardwareSchemaError(
            f"PyYAML is required to load hardware YAML files: {exc}"
        ) from exc
    except Exception as exc:  # pragma: no cover
        raise HardwareSchemaError(
            f"Failed to read hardware YAML from {path}: {exc}"
        ) from exc

    if not isinstance(raw, dict):
        raise HardwareSchemaValidationError(
            f"Hardware YAML must be a JSON object, got {type(raw).__name__}"
        )

    if validate:
        schema = _get_schema()
        validator = jsonschema.Draft7Validator(schema)
        errors = list(validator.iter_errors(raw))
        if errors:
            first = errors[0]
            path_str = ".".join(str(p) for p in first.path) if first.path else "root"
            raise HardwareSchemaValidationError(
                f"Hardware YAML validation failed at {path_str}: {first.message}"
            )

    # Build typed return value
    p = raw["parameters"]
    sw1w = p["physical_limits"]["sw1_window"]
    sw2w = p["physical_limits"]["sw2_window"]

    return ThrustReverserHardware(
        kind=raw["kind"],
        version=raw["version"],
        system_id=raw["system_id"],
        lru_inventory=_parse_lru_inventory(raw.get("lru_inventory")),
        signal_carrier_bindings=_parse_signal_carrier_bindings(
            raw.get("signal_carrier_bindings")
        ),
        sensor=SensorSpec(
            unit=p["sensor"]["radio_altitude_ft"]["unit"],
            typical_range_ft=p["sensor"]["radio_altitude_ft"]["typical_range_ft"],
            accuracy_ft=p["sensor"]["radio_altitude_ft"]["accuracy_ft"],
        ),
        actuator_tra=ActuatorTraSpec(
            unit=p["actuator"]["tra"]["unit"],
            min_deg=p["actuator"]["tra"]["min_deg"],
            max_deg=p["actuator"]["tra"]["max_deg"],
            nominal_deployment_rate_percent_per_s=p["actuator"]["tra"][
                "nominal_deployment_rate_percent_per_s"
            ],
        ),
        actuator_vd=ActuatorVDSpec(
            unit=p["actuator"]["vd"]["unit"],
            full_deploy_percent=p["actuator"]["vd"]["full_deploy_percent"],
        ),
        logic_thresholds=LogicThresholds(
            logic1_ra_ft_threshold=p["logic_thresholds"]["logic1_ra_ft_threshold"],
            logic3_tra_deg_threshold=p["logic_thresholds"][
                "logic3_tra_deg_threshold"
            ],
            deploy_90_threshold_percent=p["logic_thresholds"][
                "deploy_90_threshold_percent"
            ],
        ),
        timing=TimingSpec(
            tls_unlock_delay_s=p["timing"]["tls_unlock_delay_s"],
            pls_unlock_delay_s=p["timing"]["pls_unlock_delay_s"],
        ),
        physical_limits=PhysicalLimits(
            reverse_travel_min_deg=p["physical_limits"]["reverse_travel_min_deg"],
            reverse_travel_max_deg=p["physical_limits"]["reverse_travel_max_deg"],
            sw1_window=SwitchWindowSpec(
                near_zero_deg=sw1w["near_zero_deg"],
                deep_reverse_deg=sw1w["deep_reverse_deg"],
            ),
            sw2_window=SwitchWindowSpec(
                near_zero_deg=sw2w["near_zero_deg"],
                deep_reverse_deg=sw2w["deep_reverse_deg"],
            ),
        ),
    )
