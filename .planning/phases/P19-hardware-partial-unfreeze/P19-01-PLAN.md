---
phase: P19
plan: P19-01
type: execute
wave: 1
depends_on: []
files_created:
  - config/hardware/thrust_reverser_hardware_v1.yaml
  - src/well_harness/hardware_schema.py
  - tests/test_hardware_schema.py
files_modified: []
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls for probability calculations"
  - "All new POST routes must use _validate_chat_payload style input validation"
  - "All file I/O must use SandboxEscapeError guards"
  - "No breaking changes to existing API contracts (demo_server.py, cli.py)"
must_haves:
  truths:
    - "YAML schema defines all thrust-reverser hardware parameters with types, ranges, and units"
    - "Loader function load_thrust_reverser_hardware(config_path) returns typed dataclass"
    - "Loader validates all fields against schema and raises HardwareSchemaValidationError on mismatch"
    - "Thrust-reverser YAML contains all parameters currently in HarnessConfig (models.py)"
    - "Loader gracefully handles missing file (returns None or raises FileNotFoundError)"
    - "All 561 existing tests continue to pass (no regression)"
    - "New tests cover: valid YAML load, missing file, invalid field type, out-of-range value"
  artifacts:
    - path: config/hardware/thrust_reverser_hardware_v1.yaml
      provides: "Static YAML file with real thrust-reverser engineering parameters"
      min_lines: 60
      schema: "hardware_schema_v1.yaml JSON Schema embedded as comment or sidecar"
    - path: src/well_harness/hardware_schema.py
      provides: "YAML loader with schema validation, returns typed ThrustReverserHardware dataclass"
      min_lines: 80
    - path: tests/test_hardware_schema.py
      provides: "pytest coverage for loader: valid load, missing file, type errors, range errors"
      min_lines: 80
  key_constraints:
    - "hardware_schema.py does NOT modify HarnessConfig or controller.py"
    - "YAML is read-only reference data for simulation/analysis features (Monte Carlo, reverse diagnosis)"
    - "Schema versioned as v1, follows existing JSON Schema pattern in docs/json_schema/"
    - "Loader uses only stdlib (PyYAML optional dependency — use ruamel.yaml or json for cross-platform)"
    - "Schema JSON Schema lives in docs/json_schema/hardware_schema_v1.schema.json"
exit_criteria:
  - "python3 -c 'from well_harness.hardware_schema import load_thrust_reverser_hardware; h=load_thrust_reverser_hardware(\"config/hardware/thrust_reverser_hardware_v1.yaml\"); print(h.logic1_ra_ft_threshold)' prints 6.0"
  - "python3 -m pytest tests/test_hardware_schema.py -x -q passes with ≥4 test cases"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 561+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "561+ passed"
---

## P19.1 — Hardware YAML Schema + Loader

### Context

Project is in **Partial Unfreeze (P19)**. The truth engine (`controller.py`) is frozen and immutable.
P19 adds hardware parameter YAML files as read-only static reference data for downstream simulation
and analysis features (Monte Carlo reliability, reverse diagnosis, presentation deck).

P19.1 establishes the schema, loader, and first data file for the thrust-reverser system.
Subsequent phases (P19.2+) will consume these parameters for simulation and analysis.

### What is NOT changing

- `controller.py` — zero changes, frozen
- `HarnessConfig` (models.py) — no semantic changes
- Existing API contracts (`/api/lever-snapshot`, `/api/chat/explain`, etc.)
- Any truth engine behavior

### What IS new

#### 1. `docs/json_schema/hardware_schema_v1.schema.json`

JSON Schema for hardware parameter YAML files.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://well-harness.local/json_schema/hardware_schema_v1.schema.json",
  "title": "well_harness.thrust_reverser_hardware v1",
  "type": "object",
  "required": ["kind", "version", "system_id", "parameters"],
  "additionalProperties": false,
  "properties": {
    "kind": { "const": "thrust-reverser-hardware" },
    "version": { "const": 1 },
    "system_id": { "type": "string" },
    "parameters": {
      "type": "object",
      "required": ["sensor", "actuator", "logic_thresholds", "timing", "physical_limits"],
      "additionalProperties": false,
      "properties": {
        "sensor": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "radio_altitude_ft": {
              "type": "object",
              "additionalProperties": false,
              "required": ["unit", "typical_range_ft", "accuracy_ft"],
              "properties": {
                "unit": { "const": "ft" },
                "typical_range_ft": { "type": "number", "minimum": 0 },
                "accuracy_ft": { "type": "number", "minimum": 0 }
              }
            }
          }
        },
        "actuator": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "tra": {
              "type": "object",
              "additionalProperties": false,
              "required": ["unit", "min_deg", "max_deg", "nominal_deployment_rate_percent_per_s"],
              "properties": {
                "unit": { "const": "deg" },
                "min_deg": { "type": "number" },
                "max_deg": { "type": "number" },
                "nominal_deployment_rate_percent_per_s": { "type": "number", "minimum": 0 }
              }
            },
            "vd": {
              "type": "object",
              "additionalProperties": false,
              "required": ["unit", "full_deploy_percent"],
              "properties": {
                "unit": { "const": "percent" },
                "full_deploy_percent": { "type": "number", "minimum": 0, "maximum": 100 }
              }
            }
          }
        },
        "logic_thresholds": {
          "type": "object",
          "additionalProperties": false,
          "required": ["logic1_ra_ft_threshold", "logic3_tra_deg_threshold", "deploy_90_threshold_percent"],
          "properties": {
            "logic1_ra_ft_threshold": { "type": "number", "minimum": 0 },
            "logic3_tra_deg_threshold": { "type": "number" },
            "deploy_90_threshold_percent": { "type": "number", "minimum": 0, "maximum": 100 }
          }
        },
        "timing": {
          "type": "object",
          "additionalProperties": false,
          "required": ["tls_unlock_delay_s", "pls_unlock_delay_s"],
          "properties": {
            "tls_unlock_delay_s": { "type": "number", "minimum": 0 },
            "pls_unlock_delay_s": { "type": "number", "minimum": 0 }
          }
        },
        "physical_limits": {
          "type": "object",
          "additionalProperties": false,
          "required": ["reverse_travel_min_deg", "reverse_travel_max_deg", "sw1_window", "sw2_window"],
          "properties": {
            "reverse_travel_min_deg": { "type": "number" },
            "reverse_travel_max_deg": { "type": "number" },
            "sw1_window": {
              "type": "object",
              "additionalProperties": false,
              "required": ["near_zero_deg", "deep_reverse_deg"],
              "properties": {
                "near_zero_deg": { "type": "number" },
                "deep_reverse_deg": { "type": "number" }
              }
            },
            "sw2_window": {
              "type": "object",
              "additionalProperties": false,
              "required": ["near_zero_deg", "deep_reverse_deg"],
              "properties": {
                "near_zero_deg": { "type": "number" },
                "deep_reverse_deg": { "type": "number" }
              }
            }
          }
        }
      }
    }
  }
}
```

#### 2. `config/hardware/thrust_reverser_hardware_v1.yaml`

Human-readable YAML with real thrust-reverser engineering parameters.

Values sourced from `HarnessConfig` defaults (models.py lines 22-43) as ground truth:

```yaml
# Thrust-Reverser Hardware Parameter Reference
# Version: 1
# System: thrust-reverser
# Source: HarnessConfig defaults (src/well_harness/models.py)
# Purpose: Read-only reference data for simulation/analysis features
# Freeze rule: Do NOT modify controller.py even if these values differ from simulator needs

kind: thrust-reverser-hardware
version: 1
system_id: thrust-reverser

parameters:
  sensor:
    radio_altitude_ft:
      unit: ft
      typical_range_ft: 0.0      # 0-1000ft operational range
      accuracy_ft: 0.5          # typical RA system accuracy

  actuator:
    tra:
      unit: deg
      min_deg: -32.0            # physical hard stop
      max_deg: 0.0              # neutral/stowed
      nominal_deployment_rate_percent_per_s: 30.0
    vd:
      unit: percent
      full_deploy_percent: 100.0

  logic_thresholds:
    logic1_ra_ft_threshold: 6.0     # RA must be below 6ft for L1
    logic3_tra_deg_threshold: -11.74  # TRA must be <= -11.74deg for L3
    deploy_90_threshold_percent: 90.0  # VDT must reach 90% for deploy

  timing:
    tls_unlock_delay_s: 0.3        # Thrust Lock Solenoid unlock delay
    pls_unlock_delay_s: 0.2        # Power Lock Solenoid unlock delay

  physical_limits:
    reverse_travel_min_deg: -32.0
    reverse_travel_max_deg: 0.0
    sw1_window:
      near_zero_deg: -1.4          # SW1 closes as TRA approaches -1.4deg
      deep_reverse_deg: -6.2       # SW1 re-opens as TRA goes deeper
    sw2_window:
      near_zero_deg: -5.0
      deep_reverse_deg: -9.8
```

#### 3. `src/well_harness/hardware_schema.py`

```python
"""
Hardware schema loader for well_harness.

Loads and validates thrust-reverser hardware parameter YAML files.
These parameters are READ-ONLY reference data — they do NOT override
controller.py truth engine behavior.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Optional

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
class ActuatorSpec:
    unit: str
    min_deg: float
    max_deg: float
    nominal_deployment_rate_percent_per_s: float

@dataclass(frozen=True)
class VDVaneSpec:
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
class ThrustReverserHardware:
    kind: str
    version: int
    system_id: str
    sensor: SensorSpec
    actuator_tra: ActuatorSpec
    actuator_vd: VDVaneSpec
    logic_thresholds: LogicThresholds
    timing: TimingSpec
    physical_limits: PhysicalLimits

# ─── Schema resolution ────────────────────────────────────────────────────────

_SCHEMA_RESOURCE = "docs/json_schema/hardware_schema_v1.schema.json"

def _get_schema() -> dict:
    """Load hardware schema JSON from package resources."""
    try:
        import well_harness
        pkg_root = Path(well_harness.__file__).parent
        schema_path = pkg_root.parent / _SCHEMA_RESOURCE
        return json.loads(schema_path.read_text())
    except Exception as exc:
        raise HardwareSchemaError(f"Cannot load hardware schema JSON: {exc}") from exc

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
        raise HardwareSchemaNotFoundError(
            f"Hardware config not found: {path}"
        )

    try:
        import yaml  # PyYAML — optional dependency
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise HardwareSchemaValidationError(
            f"Invalid YAML syntax in {path}: {exc}"
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
            raise HardwareSchemaValidationError(
                f"Hardware YAML validation failed at {'.'.join(str(p) for p in first.path)}: {first.message}"
            )

    # Build typed return value
    p = raw["parameters"]
    sw1w = p["physical_limits"]["sw1_window"]
    sw2w = p["physical_limits"]["sw2_window"]

    return ThrustReverserHardware(
        kind=raw["kind"],
        version=raw["version"],
        system_id=raw["system_id"],
        sensor=SensorSpec(
            unit=p["sensor"]["radio_altitude_ft"]["unit"],
            typical_range_ft=p["sensor"]["radio_altitude_ft"]["typical_range_ft"],
            accuracy_ft=p["sensor"]["radio_altitude_ft"]["accuracy_ft"],
        ),
        actuator_tra=ActuatorSpec(
            unit=p["actuator"]["tra"]["unit"],
            min_deg=p["actuator"]["tra"]["min_deg"],
            max_deg=p["actuator"]["tra"]["max_deg"],
            nominal_deployment_rate_percent_per_s=p["actuator"]["tra"]["nominal_deployment_rate_percent_per_s"],
        ),
        actuator_vd=VDVaneSpec(
            unit=p["actuator"]["vd"]["unit"],
            full_deploy_percent=p["actuator"]["vd"]["full_deploy_percent"],
        ),
        logic_thresholds=LogicThresholds(
            logic1_ra_ft_threshold=p["logic_thresholds"]["logic1_ra_ft_threshold"],
            logic3_tra_deg_threshold=p["logic_thresholds"]["logic3_tra_deg_threshold"],
            deploy_90_threshold_percent=p["logic_thresholds"]["deploy_90_threshold_percent"],
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
```

### Tasks

#### Task 1: Create `docs/json_schema/hardware_schema_v1.schema.json`

Write the JSON Schema file as defined above. Schema validates:
- `kind` must be `thrust-reverser-hardware`
- `version` must be `1`
- All required fields present and type-correct
- Numeric ranges enforced (`minimum`, `maximum`)

#### Task 2: Create `config/hardware/thrust_reverser_hardware_v1.yaml`

Write the YAML file with all thrust-reverser hardware parameters.
Values sourced from `HarnessConfig` defaults in `models.py`:
- `logic1_ra_ft_threshold = 6.0` (line 36)
- `logic3_tra_deg_threshold = -11.74` (line 37)
- `reverse_travel_min_deg = -32.0`, `reverse_travel_max_deg = 0.0` (lines 38-39)
- `deploy_90_threshold_percent = 90.0` (line 40)
- `tls_unlock_delay_s = 0.3`, `pls_unlock_delay_s = 0.2` (lines 41-42)
- `deploy_rate_percent_per_s = 30.0` (line 43)
- `SW1 window: near_zero=-1.4, deep_reverse=-6.2` (lines 25-26)
- `SW2 window: near_zero=-5.0, deep_reverse=-9.8` (lines 32-33)

#### Task 3: Create `src/well_harness/hardware_schema.py`

Write the loader module as defined above. Key requirements:
- `load_thrust_reverser_hardware(config_path)` returns `ThrustReverserHardware` dataclass
- Validates YAML against `hardware_schema_v1.schema.json` using `jsonschema` library
- Custom exceptions: `HardwareSchemaValidationError`, `HardwareSchemaNotFoundError`
- Graceful handling of missing file (raises `HardwareSchemaNotFoundError`)
- Frozen dataclasses for all spec types
- Uses `jsonschema` (already a project dependency via P7/P8 schemas)

#### Task 4: Create `tests/test_hardware_schema.py`

Write pytest tests covering:

1. **test_load_valid_hardware_yaml** — Load the real YAML, assert all 8 parameter values match expected ground truth (6.0, -11.74, -32.0, 90.0, 0.3, 0.2, -1.4/-6.2, -5.0/-9.8)
2. **test_missing_file_raises** — Call loader with non-existent path, assert `HardwareSchemaNotFoundError`
3. **test_invalid_yaml_syntax** — Write YAML with syntax error, assert `HardwareSchemaValidationError`
4. **test_wrong_kind_rejected** — Change `kind` to `wrong-kind`, assert validation fails
5. **test_out_of_range_value_rejected** — Set `logic1_ra_ft_threshold` to `-5.0` (below `minimum: 0`), assert validation fails

#### Task 5: Verify regression

Run the full test suite:
```bash
python3 -m pytest -x --tb=short -q
```
Expected: **561+ passed** (all existing tests pass, new tests add to count).

Run new tests in isolation:
```bash
python3 -m pytest tests/test_hardware_schema.py -v
```
Expected: **5 passed**.

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ `controller.py` unchanged |
| No LLM for probability calculations | ✓ N/A — no LLM in this phase |
| New POST routes use `_validate_chat_payload` style | ✓ N/A — no new POST routes |
| All file I/O uses `SandboxEscapeError` guards | ✓ N/A — read-only YAML loading |
| No breaking changes to existing API contracts | ✓ verified |
| Backward compatible | ✓ Existing archives without `integrity` still pass |
| New schema versioned | ✓ `hardware_schema_v1.schema.json` |

### Exit Gate

Before claiming P19.1 complete, verify:
1. `python3 -c 'from well_harness.hardware_schema import load_thrust_reverser_hardware; print(load_thrust_reverser_hardware("config/hardware/thrust_reverser_hardware_v1.yaml").logic_thresholds.logic1_ra_ft_threshold)'` → `6.0`
2. `python3 -m pytest tests/test_hardware_schema.py -x -q` → **5 passed**
3. `python3 -m pytest -x --tb=short -q 2>&1 | tail -3` → **561+ passed**
