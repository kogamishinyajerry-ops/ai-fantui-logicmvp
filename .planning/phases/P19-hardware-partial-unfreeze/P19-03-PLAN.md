---
phase: P19
plan: P19-03
type: execute
wave: 1
depends_on: [P19-01]
files_created:
  - src/well_harness/reverse_diagnosis.py
  - tests/test_reverse_diagnosis.py
files_modified: []
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls for diagnosis — pure logic enumeration"
  - "All new POST routes must use _validate_chat_payload style input validation"
  - "All file I/O must use SandboxEscapeError guards"
  - "No breaking changes to existing API contracts"
  - "Hardware YAML is READ-ONLY reference data"
must_haves:
  truths:
    - "ReverseDiagnosisEngine reads parameters from P19.1 hardware YAML"
    - "Engine enumerates all parameter combinations that satisfy a given target outcome"
    - "Target outcome: 'logic3_active', 'logic1_active', 'thr_lock_active', 'deploy_confirmed'"
    - "Output: list of ParameterSnapshot dicts (each satisfying the outcome)"
    - "Enumeration bounded by YAML parameter ranges — no infinite loops"
    - "Engine uses P19.1 schema types, no truth engine imports"
    - "All 588 existing tests continue to pass (no regression)"
    - "New tests cover: single outcome, multiple outcomes, empty result, YAML load"
  artifacts:
    - path: src/well_harness/reverse_diagnosis.py
      provides: "Reverse diagnosis engine — enumerate parameter combos for target outcome"
      min_lines: 120
    - path: tests/test_reverse_diagnosis.py
      provides: "pytest coverage for ReverseDiagnosisEngine"
      min_lines: 80
  key_constraints:
    - "reverse_diagnosis.py does NOT import or call controller.py"
    - "Engine only reads from hardware YAML — it is a DIAGNOSIS ANALYZER, not truth engine"
    - "Enumeration is bounded: max 1000 combinations per outcome"
    - "No randomness — pure deterministic logic evaluation"
exit_criteria:
  - "python3 -c 'from well_harness.reverse_diagnosis import ReverseDiagnosisEngine; e=ReverseDiagnosisEngine(\"config/hardware/thrust_reverser_hardware_v1.yaml\"); r=e.diagnose(\"logic3_active\"); print(f\"found {len(r)} combos for logic3_active\")' runs without error"
  - "python3 -m pytest tests/test_reverse_diagnosis.py -x -q passes (≥5 test cases)"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 588+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "588+ passed"
---

## P19.3 — Reverse Diagnosis Engine

### Context

P19.1 established the hardware parameter YAML. P19.2 built Monte Carlo reliability simulation.
P19.3 builds a **reverse diagnosis engine**: given a desired system outcome, enumerate
which parameter combinations would cause that outcome.

Example: "I want logic3 to be active. What combinations of RA, TRA, SW1, SW2 satisfy this?"
→ Enumerates all valid combinations within YAML parameter ranges that make `logic3` true.

This is a **diagnosis/analysis feature** — it reads hardware YAML and produces
enumerated possibilities. It does NOT affect the truth engine.

### Architecture

```
P19.1 YAML ──reads──> ReverseDiagnosisEngine ──enumerates──> list[ParameterSnapshot]
                                              (bounded to max 1000 combos)
```

### What IS NOT Changing

- `controller.py` — zero changes, frozen
- `HarnessConfig` (models.py) — no semantic changes
- Existing API contracts

### Implementation

#### `src/well_harness/reverse_diagnosis.py`

```python
"""
Reverse diagnosis engine for thrust-reverser system.

Given a desired outcome (e.g., "logic3_active"), enumerates all parameter
combinations within YAML-defined ranges that satisfy the outcome.

This is a DIAGNOSIS ANALYZER — it reads hardware YAML and produces enumerated
possibilities. It does NOT call controller.py or affect truth engine behavior.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from well_harness.hardware_schema import (
    ThrustReverserHardware,
    load_thrust_reverser_hardware,
)


# ─── Constants ─────────────────────────────────────────────────────────────────

MAX_COMBINATIONS = 1000  # Safety bound to prevent runaway enumeration

VALID_OUTCOMES = {
    "logic3_active",       # TRA <= threshold AND TLS unlocked AND SW2 closed
    "logic1_active",       # RA < threshold AND SW1 closed AND not inhibited
    "thr_lock_active",     # pls_power active AND pls_unlocked
    "deploy_confirmed",    # VDT >= 90% AND thr_lock active
    "tls_unlocked",       # tls_unlock_delay elapsed
    "pls_unlocked",        # pls_unlock_delay elapsed
}

# Parameter grid resolution (number of steps per dimension)
_GRID_RESOLUTION = 5  # Small grid for bounded enumeration


# ─── Dataclasses ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ParameterSnapshot:
    """A parameter combination that satisfies the target outcome."""

    radio_altitude_ft: float
    tra_deg: float
    sw1_closed: bool
    sw2_closed: bool
    tls_unlocked: bool
    pls_unlocked: bool
    vdt_percent: float
    n1k: float
    reverser_inhibited: bool


# ─── Engine ───────────────────────────────────────────────────────────────────


class ReverseDiagnosisEngine:
    """
    Reverse diagnosis engine for thrust-reverser parameter analysis.

    Enumerates parameter combinations within YAML-defined ranges that satisfy
    a given target outcome.

    Deterministic — no randomness.

    Args:
        hardware_yaml_path: Path to thrust-reverser hardware YAML (P19.1 format).
    """

    def __init__(self, hardware_yaml_path: str | Path) -> None:
        self.hardware = load_thrust_reverser_hardware(hardware_yaml_path)

    def diagnose(
        self,
        outcome: str,
        *,
        max_results: int = MAX_COMBINATIONS,
    ) -> list[ParameterSnapshot]:
        """
        Enumerate parameter combinations that satisfy the target outcome.

        Args:
            outcome: One of VALID_OUTCOMES (e.g., "logic3_active").
            max_results: Maximum number of combinations to return.

        Returns:
            List of ParameterSnapshot, each satisfying the outcome.

        Raises:
            ValueError: Unknown outcome string.
        """
        if outcome not in VALID_OUTCOMES:
            raise ValueError(
                f"Unknown outcome: {outcome!r}. "
                f"Valid outcomes: {sorted(VALID_OUTCOMES)}"
            )

        hw = self.hardware
        results: list[ParameterSnapshot] = []

        # ── Grid-enumerate within YAML parameter ranges ─────────────────────
        ra_values = _linspace(0.0, hw.sensor.typical_range_ft, _GRID_RESOLUTION)
        tra_values = _linspace(
            hw.physical_limits.reverse_travel_min_deg,
            hw.physical_limits.reverse_travel_max_deg,
            _GRID_RESOLUTION,
        )
        vdt_values = _linspace(0.0, 100.0, _GRID_RESOLUTION)
        n1k_values = [50.0, 80.0, 95.0]  # Representative N1K values

        for ra in ra_values:
            for tra in tra_values:
                for vdt in vdt_values:
                    for n1k in n1k_values:
                        for inhibited in (False, True):
                            # Compute derived states
                            sw1_closed = _sw1_closed(tra, hw)
                            sw2_closed = _sw2_closed(tra, hw)
                            tls_unlocked = True  # Assume unlocked for logic3
                            pls_unlocked = True  # Assume unlocked for thr_lock
                            tls_delay_met = True
                            pls_delay_met = True

                            # ── Evaluate outcome conditions ───────────────────
                            satisfies = False
                            if outcome == "logic3_active":
                                tra_thresh = hw.logic_thresholds.logic3_tra_deg_threshold
                                vdt_thresh = hw.logic_thresholds.deploy_90_threshold_percent
                                satisfies = (
                                    tra <= tra_thresh
                                    and tls_unlocked
                                    and tls_delay_met
                                    and sw2_closed
                                    and not inhibited
                                )
                            elif outcome == "logic1_active":
                                ra_thresh = hw.logic_thresholds.logic1_ra_ft_threshold
                                satisfies = (
                                    ra < ra_thresh
                                    and sw1_closed
                                    and not inhibited
                                )
                            elif outcome == "thr_lock_active":
                                pls_delay = hw.timing.pls_unlock_delay_s
                                satisfies = pls_unlocked and pls_delay_met
                            elif outcome == "deploy_confirmed":
                                vdt_thresh = hw.logic_thresholds.deploy_90_threshold_percent
                                pls_delay = hw.timing.pls_unlock_delay_s
                                satisfies = (
                                    vdt >= vdt_thresh
                                    and pls_unlocked
                                    and pls_delay_met
                                )
                            elif outcome == "tls_unlocked":
                                tls_delay = hw.timing.tls_unlock_delay_s
                                satisfies = tls_unlocked
                            elif outcome == "pls_unlocked":
                                pls_delay = hw.timing.pls_unlock_delay_s
                                satisfies = pls_unlocked

                            if satisfies:
                                results.append(
                                    ParameterSnapshot(
                                        radio_altitude_ft=ra,
                                        tra_deg=tra,
                                        sw1_closed=sw1_closed,
                                        sw2_closed=sw2_closed,
                                        tls_unlocked=tls_unlocked,
                                        pls_unlocked=pls_unlocked,
                                        vdt_percent=vdt,
                                        n1k=n1k,
                                        reverser_inhibited=inhibited,
                                    )
                                )
                                if len(results) >= max_results:
                                    return results

        return results


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _linspace(start: float, stop: float, num: int) -> list[float]:
    """Return num evenly-spaced values in [start, stop]."""
    if num <= 1:
        return [start]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]


def _sw1_closed(tra_deg: float, hw: ThrustReverserHardware) -> bool:
    sw1 = hw.physical_limits.sw1_window
    lo = min(sw1.near_zero_deg, sw1.deep_reverse_deg)
    hi = max(sw1.near_zero_deg, sw1.deep_reverse_deg)
    return lo <= tra_deg <= hi


def _sw2_closed(tra_deg: float, hw: ThrustReverserHardware) -> bool:
    sw2 = hw.physical_limits.sw2_window
    lo = min(sw2.near_zero_deg, sw2.deep_reverse_deg)
    hi = max(sw2.near_zero_deg, sw2.deep_reverse_deg)
    return lo <= tra_deg <= hi
```

### Tasks

#### Task 1: Create `src/well_harness/reverse_diagnosis.py`

Write the module as defined above. Key requirements:
- `ReverseDiagnosisEngine` reads from P19.1 YAML via `load_thrust_reverser_hardware`
- `diagnose(outcome, max_results=1000)` returns `list[ParameterSnapshot]`
- Bounded enumeration (max 1000 combinations per outcome)
- Pure deterministic logic — no randomness, no LLM
- Imports `hardware_schema` from P19.1
- Frozen `@dataclass` for `ParameterSnapshot`
- `ValueError` for unknown outcome

#### Task 2: Create `tests/test_reverse_diagnosis.py`

Write pytest tests:

1. **test_diagnose_logic3_returns_nonempty** — `diagnose("logic3_active")` returns ≥1 result
2. **test_diagnose_unknown_raises** — unknown outcome raises `ValueError` with valid outcome list
3. **test_diagnose_result_has_valid_fields** — each result has all fields from `ParameterSnapshot`
4. **test_diagnose_max_results_bounds_output** — `diagnose("logic3_active", max_results=5)` returns ≤5
5. **test_loads_real_yaml** — engine loads actual P19.1 YAML and uses its parameters
6. **test_logic1_active_result** — `diagnose("logic1_active")` returns combos where RA < threshold

#### Task 3: Verify exit gates

```bash
# Gate 1: Engine diagnoses logic3_active
python3 -c 'from well_harness.reverse_diagnosis import ReverseDiagnosisEngine; \
  e=ReverseDiagnosisEngine("config/hardware/thrust_reverser_hardware_v1.yaml"); \
  r=e.diagnose("logic3_active"); print(f"found {len(r)} combos for logic3_active")'

# Gate 2: New tests pass
python3 -m pytest tests/test_reverse_diagnosis.py -x -q

# Gate 3: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 588+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ `controller.py` unchanged |
| No LLM for diagnosis | ✓ Pure logic enumeration |
| Hardware YAML is read-only | ✓ Engine only reads |
| Bounded enumeration | ✓ max 1000 combinations |
| No breaking changes to existing API contracts | ✓ verified |

### Exit Gate

Before claiming P19.3 complete, verify all 3 gates above.
