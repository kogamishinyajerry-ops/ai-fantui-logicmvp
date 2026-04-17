---
phase: P19
plan: P19-05
type: execute
wave: 1
depends_on: [P19-03, P19-04]
files_created: []
files_modified:
  - src/well_harness/reverse_diagnosis.py
autonomous: false
requirements: []
user_setup: []
freeze_constraints:
  - "No truth engine semantic changes — controller.py unchanged"
  - "No LLM calls — pure data serialization"
  - "No breaking changes to existing API contracts"
  - "All existing tests continue to pass"
must_haves:
  truths:
    - "ReverseDiagnosisEngine can serialize a diagnosis report as a plain dict"
    - "Report contains: outcome, total_combos_found, grid_resolution, timestamp"
    - "Each result has all ParameterSnapshot fields"
    - "All 604 existing tests continue to pass (no regression)"
  artifacts:
    - path: src/well_harness/reverse_diagnosis.py
      provides: "ParameterSnapshot.to_dict() class method + diagnose_and_report() convenience method"
      min_lines: 20
  key_constraints:
    - "Only add methods — do NOT modify diagnose() behavior"
    - "Frozen dataclass is immutable — to_dict() must be a classmethod or standalone function"
    - "No file I/O in the engine itself"
exit_criteria:
  - "python3 -c 'from well_harness.reverse_diagnosis import ReverseDiagnosisEngine, ParameterSnapshot; e=ReverseDiagnosisEngine(\"config/hardware/thrust_reverser_hardware_v1.yaml\"); r=e.diagnose(\"logic1_active\"); print(ParameterSnapshot.to_dict(r[0]))' runs without error and prints dict'"
  - "python3 -m pytest -x --tb=short -q 2>&1 | tail -3 shows 604+ passed (no regression)"
regression_baseline:
  command: "python3 -m pytest -x --tb=short -q 2>&1 | tail -3"
  expected: "604+ passed"
---

## P19.5 — Diagnosis Report Serialization

### Context

P19.3 created `ReverseDiagnosisEngine` which returns `list[ParameterSnapshot]`. P19.4 added causal chain SVG connectors. P19.5 adds a serialization layer so the diagnosis results can be:
1. Rendered in the browser as a structured report panel
2. Exported as part of the pitch demo output

### Architecture

```
ReverseDiagnosisEngine.diagnose_and_report("logic1_active")
                                          ↓
        { outcome, total_combos, grid_resolution,
          timestamp, results: [ParameterSnapshot.to_dict() for each] }
```

### Implementation

#### 1. `src/well_harness/reverse_diagnosis.py` — additions

Add a standalone helper function and a convenience method:

```python
def _parameter_snapshot_to_dict(snapshot: ParameterSnapshot) -> dict:
    """Convert a ParameterSnapshot to a plain dict for JSON serialization."""
    return {
        "radio_altitude_ft": snapshot.radio_altitude_ft,
        "tra_deg": snapshot.tra_deg,
        "sw1_closed": snapshot.sw1_closed,
        "sw2_closed": snapshot.sw2_closed,
        "tls_unlocked": snapshot.tls_unlocked,
        "pls_unlocked": snapshot.pls_unlocked,
        "vdt_percent": snapshot.vdt_percent,
        "n1k": snapshot.n1k,
        "reverser_inhibited": snapshot.reverser_inhibited,
    }


class ReverseDiagnosisEngine:
    # ... existing code unchanged ...

    def diagnose_and_report(
        self,
        outcome: str,
        *,
        max_results: int = MAX_COMBINATIONS,
    ) -> dict:
        """
        Convenience wrapper: run diagnose() and return a serializable report dict.

        Returns:
            {
                "outcome": outcome,
                "total_combos_found": len(results),
                "grid_resolution": _GRID_RESOLUTION,
                "timestamp": "<ISO-8601>",
                "results": [list of ParameterSnapshot dicts],
            }
        """
        from datetime import datetime, timezone
        results = self.diagnose(outcome, max_results=max_results)
        return {
            "outcome": outcome,
            "total_combos_found": len(results),
            "grid_resolution": _GRID_RESOLUTION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": [_parameter_snapshot_to_dict(r) for r in results],
        }
```

### Tasks

#### Task 1: Add serialization helpers to `reverse_diagnosis.py`

- Add `_parameter_snapshot_to_dict()` standalone function
- Add `diagnose_and_report()` method to `ReverseDiagnosisEngine`
- Existing `diagnose()` behavior is unchanged

#### Task 2: Verify exit gates

```bash
# Gate 1: to_dict round-trip
python3 -c 'from well_harness.reverse_diagnosis import ReverseDiagnosisEngine, ParameterSnapshot; \
  e=ReverseDiagnosisEngine("config/hardware/thrust_reverser_hardware_v1.yaml"); \
  r=e.diagnose("logic1_active"); \
  print(e.diagnose_and_report("logic1_active"))'

# Gate 2: Full regression
python3 -m pytest -x --tb=short -q 2>&1 | tail -3
# Expected: 604+ passed
```

### Freeze Compliance Checklist

| Rule | Compliance |
|------|-----------|
| No truth engine semantic changes | ✓ No controller.py touches |
| No LLM calls | ✓ Pure data serialization |
| No breaking changes to existing API contracts | ✓ New method only |
| Existing tests continue to pass | ✓ Verified |

### Exit Gate

Verify both gates above.
