# P7-01 Summary - Introduce A Reusable Control-System Spec Foundation

## What Changed

- Added `src/well_harness/system_spec.py` as the first reusable control-system workbench spec layer.
- Captured the current thrust-reverser deploy chain as the first reference system, including:
  - component definitions
  - logic-node definitions
  - a compressed acceptance-scenario baseline
  - fault-mode scaffolding
  - mandatory clarification questions for future unknown systems
- Added `tests/test_system_spec.py` to verify the reference spec stays complete and JSON-serializable.
- Updated `.planning/PROJECT.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md` so the new product direction is explicit in project truth.

## Why It Matters

- Strict acceptance playback, fault injection, and future-system generalization now have a shared architectural foundation instead of three disconnected feature ideas.
- The current project still preserves `controller.py` as the confirmed truth source for the reference system.
- Future phases can now build scenario playback, diagnostic documents, and knowledge capture on top of the same spec object.

## Verification

- `PYTHONPATH=src python3 -m pytest -q tests/test_system_spec.py`
- `PYTHONPATH=src python3 -m pytest -q tests/test_demo.py`

## Follow-On Work

- Add a scenario-ingestion layer that can convert structured engineer process descriptions into monitor-vs-time traces from the shared spec.
- Add a fault-diagnosis engine that walks the logic graph and produces engineer-readable reasoning artifacts.
- Decide which document adapters come first for external inputs: structured JSON/YAML, Notion/Markdown tables, or mixed/PDF workflows.
