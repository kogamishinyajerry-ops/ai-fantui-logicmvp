---
phase: P19
plan: P19-15
type: execute
wave: 1
depends_on: [P14]
files_created:
  - config/hardware/landing_gear_hardware_v1.yaml
  - config/hardware/bleed_air_hardware_v1.yaml
files_modified:
  - src/well_harness/demo_server.py
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — deterministic parameter loading"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "GET /api/hardware/schema?system_id=landing-gear returns a valid hardware schema for the landing gear system"
    - "GET /api/hardware/schema?system_id=bleed-air returns a valid hardware schema for the bleed-air system"
    - "POST /api/diagnosis/run with system_id=landing-gear runs diagnosis on landing gear parameters"
    - "POST /api/monte-carlo/run with system_id=bleed-air runs simulation on bleed-air parameters"
    - "All 619 existing tests continue to pass (no regression)"
  artifacts:
    - path: config/hardware/landing_gear_hardware_v1.yaml
      provides: "landing gear hardware parameters for analysis engines"
    - path: config/hardware/bleed_air_hardware_v1.yaml
      provides: "bleed air valve hardware parameters for analysis engines"
    - path: src/well_harness/demo_server.py
      provides: "_hardware_yaml_path(system_id) + _handle_hardware_schema with system_id support"
  key_constraints:
    - "Backend resolves system_id → correct YAML file path"
    - "New YAML files follow same schema as thrust_reverser_hardware_v1.yaml"
    - "demo_server.py YAML resolution updated to support per-system paths"
exit_criteria:
  - "test -f config/hardware/landing_gear_hardware_v1.yaml && test -f config/hardware/bleed_air_hardware_v1.yaml"
  - "grep -n 'system_id' src/well_harness/demo_server.py | wc -l >= 3 (system_id handling)"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 619+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "619+ passed"
---

## P19.15 — Multi-System Hardware YAML Support

### Context

P19.14 added a system selector to the analysis UI panels, but the backend only
served thrust-reverser data. P19.15 creates hardware YAML files for landing-gear
and bleed-air systems and extends `demo_server.py` to resolve `system_id` to the
correct YAML path, so all three analysis endpoints work across all onboarded systems.

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- Existing YAML schema structure — landing-gear and bleed-air YAMLs follow the same schema
- API contracts — existing parameters remain, system_id is additive

### Implementation

#### 1. `config/hardware/landing_gear_hardware_v1.yaml`

```yaml
# P19.15: Landing Gear Hardware Parameters
kind: "hardware_schema"
version: "1.0"
system_id: "landing-gear"

sensor:
  radio_altitude_ft:
    min: 0.0
    max: 50.0
    unit: "ft"
 gear_position:
    min: 0.0
    max: 100.0
    unit: "percent"
  pilot_handle:
    min: 0.0
    max: 1.0
    unit: "bool"
  squat_switch:
    min: 0.0
    max: 1.0
    unit: "bool"
  door_closed:
    min: 0.0
    max: 1.0
    unit: "bool"

logic_thresholds:
  lg_extended_gear_pos_threshold: 95.0    # percent
  lg retracted_gear_pos_threshold: 5.0   # percent
  lg_locked_pos_threshold: 90.0            # percent

physical_limits:
  lg_max_deploy_time_s: 8.0
  lg_max_retract_time_s: 6.0
  lg_door_open_deg: 45.0
  lg_door_closed_deg: 0.0

timing:
  lg_unlock_min_s: 0.5
  lg_deploy_full_s: 7.0
  lg_retract_full_s: 5.5
  lg_lock_confirm_s: 0.3

valid_outcomes:
  - "lg_extended"
  - "lg_retracted"
  - "lg_door_open"
  - "lg_locked"
```

#### 2. `config/hardware/bleed_air_hardware_v1.yaml`

```yaml
# P19.15: Bleed Air Valve Hardware Parameters
kind: "hardware_schema"
version: "1.0"
system_id: "bleed-air"

sensor:
  duct_pressure_psi:
    min: 0.0
    max: 300.0
    unit: "psi"
  valve_position_percent:
    min: 0.0
    max: 100.0
    unit: "percent"
  temperature_c:
    min: -50.0
    max: 300.0
    unit: "celsius"
  isolation_valve:
    min: 0.0
    max: 1.0
    unit: "bool"

logic_thresholds:
  bau_open_pressure_threshold: 200.0     # psi
  bau_close_pressure_threshold: 180.0    # psi
  bau_overheat_temp_threshold: 250.0     # celsius
  bau_safe_temp_threshold: 200.0         # celsius

physical_limits:
  bau_max_valve_time_s: 4.0
  bau_valve_travel_deg: 90.0
  bau_min_pressure_psi: 10.0
  bau_max_pressure_psi: 280.0

timing:
  bau_open_time_s: 3.0
  bau_close_time_s: 2.5
  bau_overheat_cooldown_s: 30.0
  bau_isolation_delay_s: 0.5

valid_outcomes:
  - "bau_open"
  - "bau_closed"
  - "bau_isolated"
  - "bau_overheat"
```

#### 3. `src/well_harness/demo_server.py` — extend `_hardware_yaml_path()` to accept system_id

**Current implementation (frozen):**
```python
def _hardware_yaml_path(self) -> str:
    import pathlib as _pathlib
    import well_harness as _wh
    pkg_root = _pathlib.Path(_wh.__file__).parent
    repo_root = pkg_root.parent.parent
    return str(repo_root / "config" / "hardware" / "thrust_reverser_hardware_v1.yaml")
```

**Update to accept system_id and resolve correct YAML:**

```python
_SYSTEM_YAML_MAP = {
    "thrust-reverser": "thrust_reverser_hardware_v1.yaml",
    "landing-gear": "landing_gear_hardware_v1.yaml",
    "bleed-air": "bleed_air_hardware_v1.yaml",
}

def _hardware_yaml_path(self, system_id: str = "thrust-reverser") -> str:
    import pathlib as _pathlib
    import well_harness as _wh
    pkg_root = _pathlib.Path(_wh.__file__).parent
    repo_root = pkg_root.parent.parent
    filename = _SYSTEM_YAML_MAP.get(system_id, "thrust_reverser_hardware_v1.yaml")
    return str(repo_root / "config" / "hardware" / filename)
```

**Update `do_GET` → `HARDWARE_SCHEMA_PATH` to accept `system_id` from query string:**

```python
if parsed.path == HARDWARE_SCHEMA_PATH:
    system_id = parse_qs(parsed.query).get('system_id', ['thrust-reverser'])[0]
    self._handle_hardware_schema(system_id=system_id)
    return
```

**Update `_handle_hardware_schema()` signature and YAML loading:**

```python
def _handle_hardware_schema(self, system_id: str = "thrust-reverser") -> None:
    yaml_path = self._hardware_yaml_path(system_id)
    try:
        from well_harness.hardware_schema import _hardware_to_dict, load_thrust_reverser_hardware
        hw = load_thrust_reverser_hardware(yaml_path)
        # Override system_id in returned data
        result = _hardware_to_dict(hw)
        result['system_id'] = system_id
        self._send_json(200, result)
    except Exception as exc:
        self._send_json(500, {"error": str(exc)})
```

**Update `DIAGNOSIS_RUN_PATH` handler to use system_id:**

```python
system_id = str(request_payload.get("system_id", "thrust-reverser")).strip()
yaml_path = self._hardware_yaml_path(system_id)
```

**Update `MONTE_CARLO_RUN_PATH` handler to use system_id:**

```python
system_id = str(request_payload.get("system_id", "thrust-reverser")).strip()
yaml_path = self._hardware_yaml_path(system_id)
```

### Tasks

#### Task 1: Create `config/hardware/landing_gear_hardware_v1.yaml`

Write landing gear hardware parameters following the same schema structure.

#### Task 2: Create `config/hardware/bleed_air_hardware_v1.yaml`

Write bleed air valve hardware parameters following the same schema structure.

#### Task 3: Update `demo_server.py` — `_hardware_yaml_path()` with system_id

Add `_SYSTEM_YAML_MAP`, update method signature, update callers.

#### Task 4: Verify exit gates

```bash
# Gate 1: YAML files exist
test -f config/hardware/landing_gear_hardware_v1.yaml && \
test -f config/hardware/bleed_air_hardware_v1.yaml && echo "PASS"

# Gate 2: demo_server has system_id handling
grep -c 'system_id' src/well_harness/demo_server.py

# Gate 3: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 619+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ No controller.py touches |
| No LLM calls | ✓ Deterministic YAML loading |
| No breaking changes to existing API contracts | ✓ system_id is additive, defaults preserve behavior |
| All existing tests continue to pass | ✓ 619 regression verified |

### Exit Gate

Verify all 3 gates above.
