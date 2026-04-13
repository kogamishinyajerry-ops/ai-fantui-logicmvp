# Third-System Onboarding Case Study — P12-01

**System onboarded:** Bleed Air Valve Control System
**System ID:** `bleed-air-valve`
**Date:** 2026-04-13
**Onboarding agent:** MiniMax-2.7 (T1 — code implementation)
**Total elapsed time:** ~15 minutes (reading + implementation + validation)

---

## 1. What Was Onboarded

**Bleed Air Valve Control System** — a simplified environmental control system (ECS) for aircraft.

Bleed air is extracted from the engine compressor and routed to multiple downstream consumers: cabin air conditioning packs, wing anti-icing systems, and engine start. The valve under control is a pneumatically-actuated butterfly valve that must:

- **OPEN** when inlet pressure (from the engine compressor) exceeds a minimum safe threshold (~35 psi)
- **CLOSE** when inlet pressure drops below a hysteresis floor (~32 psi) OR when overpressure is detected (>65 psi)

### Spec Summary

| Field | Value |
|-------|-------|
| Components | 5 (valve_position, valve_cmd, inlet_pressure, outlet_pressure, control_unit_ready) |
| Logic nodes | 2 (valve_open_logic, valve_close_logic) |
| Acceptance scenarios | 3 (nominal_open, nominal_close, pressure_over_limit) |
| Fault modes | 3 (valve_stuck_open, valve_stuck_closed, sensor_misread_high) |
| Adapter file | `src/well_harness/adapters/bleed_air_adapter.py` |
| Intake packet | `src/well_harness/adapters/bleed_air_intake_packet.py` |

---

## 2. Onboarding Process

### Step 1 — Reading prerequisite docs (~5 min)
Before writing any code, all seven required files were read:

1. `docs/onboarding/README.md` — understood the 4-stage pipeline, entry paths, and troubleshooting section
2. `templates/new_system/README.md` — understood the placeholder naming conventions ({{system_id}}, {{SystemId}}, {{SYSTEM_UPPER}})
3. `templates/new_system/NEW_SYSTEM_SPEC.json` — understood the schema field requirements
4. `templates/new_system/new_system_adapter.py` — understood the template structure
5. `templates/new_system/new_system_intake_packet.py` — understood the intake-packet builder pattern
6. `src/well_harness/adapters/landing_gear_adapter.py` (lines 1-80, full file) — the reference implementation
7. `src/well_harness/models.py` — confirmed `ControlSystemIntakePacket` lives in `document_intake.py`
8. `docs/json_schema/control_system_spec_v1.schema.json` — cross-referenced (not fully read; landing_gear pattern was sufficient)

The dry-run tool (`tools/onboard_new_system_dry_run.py`) was also read in full to understand exactly what it validates at each stage.

### Step 2 — Creating the adapter (~5 min)
Following the landing_gear_adapter pattern exactly:

- Defined `BLEED_AIR_SYSTEM_ID`, `BLEED_AIR_SOURCE_OF_TRUTH`, threshold constants, and `BLEED_AIR_CONTROLLER_METADATA`
- Implemented `build_bleed_air_workbench_spec()` with all spec fields populated from scratch (not auto-generated from a template stub)
- Implemented `BleedAirValveControllerAdapter.evaluate_snapshot()` with proper snapshot extraction for both string signals (valve_position) and float/bool signals
- Key design decision: used a **hysteresis threshold** (35 psi min / 32 psi close floor) to prevent chattering, matching real aircraft pneumatic control practice

### Step 3 — Creating the intake packet (~2 min)
Straightforward: called `build_bleed_air_workbench_spec()`, wrapped with `workbench_spec_from_dict()`, populated one `SourceDocumentRef` pointing to the adapter file, returned a `ControlSystemIntakePacket`.

### Step 4 — Running the dry-run validation (<1 min)
```bash
PYTHONPATH=src python3 tools/onboard_new_system_dry_run.py \
  --spec-file src/well_harness/adapters/bleed_air_adapter.py \
  --format json
```

**Result: all 4 stages PASSED.**

---

## 3. Dry-Run Results

```
Stage 1 – SPEC:         PASS  (5 components, 2 logic nodes, 3 scenarios, 3 fault modes)
Stage 2 – PLAYBACK:    PASS  (scenario_id=nominal_open, completion_reached=true)
Stage 3 – DIAGNOSIS:   PASS  (fault_mode_id=valve_stuck_open, baseline_completion=true, fault_completion=true)
Stage 4 – KNOWLEDGE:   PASS  (artifact_status=diagnosed)
OVERALL: PASS
```

jsonschema was installed and active; all schema validations passed.

---

## 4. What Worked Well

1. **The landing_gear_adapter is an excellent reference.** Reading it end-to-end (not just the first 80 lines as the task suggested) gave the full picture including the `evaluate_snapshot()` implementation.
2. **The dry-run tool is well-designed.** It accepts a Python adapter file directly (via `build_<system>_workbench_spec()` discovery) — no need to manually export JSON first.
3. **Template placeholders ({{system_id}}, etc.) are unambiguous.** Easy to fill in mechanically.
4. **The threshold constant pattern** (module-level constants like `BLEED_AIR_PRESSURE_MIN_PSI`) is clean and matches the reference implementation.

---

## 5. What Was Confusing

1. **The task says "read the first 80 lines" of landing_gear_adapter.** But the `evaluate_snapshot()` implementation (the most important part) is at lines 299-358. The task should either say "read the full file" or explicitly list which sections to read in what order.
2. **`models.py` was listed as a required read but contains none of the `ControlSystemIntakePacket` fields** — those are in `document_intake.py`. Reading `models.py` was not useful for this task.
3. **`NEW_SYSTEM_SPEC.json` (the template) is JSON**, but the actual adapter-based workflow uses Python dataclasses. It was unclear whether a JSON spec file needs to be created separately or whether the adapter alone suffices. The dry-run tool makes it clear: the Python adapter is the primary artifact.
4. **The schema file (`control_system_spec_v1.schema.json`) was listed as a required read** but was not actually needed once the landing_gear_adapter was understood. Its inclusion adds noise for someone trying to onboard quickly.

---

## 6. Gaps in the Onboarding Guide

### Gap 1: No explicit "fill in these specific values" checklist
The template README says "fill in the adapter template" but does not specify:
- Minimum number of components (the spec schema requires at least 1, but the dry-run checks require at least 1)
- Which component kinds are valid (`sensor`, `command`, `pilot_input` — listed in onboarding README but easy to miss)
- Which `fault_kind` values are valid (from `fault_taxonomy.py`, not mentioned in onboarding README)

### Gap 2: `_snapshot_str` helper is not in the template
The template only provides `_snapshot_bool` and `_snapshot_float`. For discrete-state signals (like `valve_position: "CLOSED" / "OPEN"`), `_snapshot_str` is needed. The landing_gear_adapter also doesn't use `_snapshot_str` (its discrete signal `gear_handle_position` uses `_snapshot_str`), but it's easy to miss. The template should include it.

### Gap 3: The `GenericControllerTruthAdapter` protocol (from `controller_adapter.py`) is never mentioned
The onboarding README references the protocol briefly but never links to the file. The protocol requires both `load_spec()` and `evaluate_snapshot()`. A first-time engineer might not know to check `controller_adapter.py`.

### Gap 4: The "4th file" confusion
The task description refers to "templates/new_system/NEW_SYSTEM_SPEC.json" and "templates/new_system/new_system_adapter.py" and "templates/new_system/new_system_intake_packet.py" — that's 3 files. The landing_gear_adapter is a 4th "reference" file that is critical but not a template. This is confusing.

### Gap 5: Intake packet `clarification_answers` default
When the intake packet uses `clarification_answers=()`, the `assess_intake_packet()` function does not fail even with unanswered questions — it just records them as unanswered. This is fine for dry-run, but a newcomer might not realize they need to answer questions for a real intake.

---

## 7. Recommendations for Improving the Onboarding Tools

### Recommendation 1: Create a `new_system_adapter_with_str.py` template variant
Include `_snapshot_str` alongside `_snapshot_bool` and `_snapshot_float`.

### Recommendation 2: Add a "Quick Start" section in `docs/onboarding/README.md`
A 5-step TL;DR at the top:
1. Copy `landing_gear_adapter.py` → `your_system_adapter.py`
2. Fill in system ID, constants, components, logic nodes, scenarios, fault modes
3. Implement `evaluate_snapshot()`
4. Create `your_system_intake_packet.py`
5. Run `tools/onboard_new_system_dry_run.py --spec-file your_system_adapter.py`

### Recommendation 3: Add a `validate_onboarding_readiness.py` tool
A pre-flight check that validates whether an adapter has all required fields before the full dry-run. Could check:
- All snapshot keys used in `evaluate_snapshot()` match component IDs
- All `downstream_component_ids` reference components of `kind="command"`
- All `acceptance_scenario.monitored_signal_ids` are valid component IDs

### Recommendation 4: Mention `fault_taxonomy.py` in the onboarding guide
The valid `fault_kind` values should be listed directly in the onboarding README, not require a separate file read.

### Recommendation 5: Clarify the JSON spec vs Python adapter distinction
The README discusses both "adapter path" and "intake path" but the relationship is still confusing. A diagram would help:

```
Python Adapter (your_system_adapter.py)
  └─ build_<system>_workbench_spec() → dict
        │
        ├─→ [Dry-run via onboard_new_system_dry_run.py]
        │       (converts dict → ControlSystemWorkbenchSpec → runs 4 stages)
        │
        └─→ Intake Packet (your_system_intake_packet.py)
                └─→ ControlSystemIntakePacket
                        ├─→ assess_intake_packet()
                        ├─→ build_playback_report()
                        ├─→ build_fault_diagnosis_report()
                        └─→ build_knowledge_artifact()
```

---

## 8. Conclusion

The P11 onboarding tools **worked correctly for a non-project-owner third system**. The bleed-air valve was onboarded in approximately 15 minutes with zero errors. The dry-run tool is the right abstraction: it accepts a Python file directly, runs all 4 stages, and produces clear pass/fail output with schema validation.

The main friction points are **documentation clarity** (which file to read for what, what the minimum viable spec looks like) rather than technical gaps. With the recommendations above, a future third-party engineer should be able to onboard a new system in under 10 minutes.

**Files created:**
- `src/well_harness/adapters/bleed_air_adapter.py` — 380 lines
- `src/well_harness/adapters/bleed_air_intake_packet.py` — 53 lines
- `docs/onboarding/THIRD_SYSTEM_CASE_STUDY.md` — this document
