---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: Workbench v5 deep-water implementation active · JER-229 merged · JER-230 empty-canvas authoring in progress
last_updated: "2026-05-02T09:18:10.000+08:00"
last_activity: 2026-05-02
progress:
  total_phases: 55
  completed_phases: 45
  total_plans: 2
  completed_plans: 1
  notes: "JER-204 merged PR #186 and closed Runtime v3 project. JER-205 merged PR #187 with the Workbench v4 acceptance model. JER-206 through JER-219 built the current single-user authoring base: templates, subsystems, hardware/interface evidence, debug/diff/handoff packets, archive validation, workspace_document, and canvas_interaction_summary. JER-220 reset the active roadmap to foundation-first: editor -> runner -> test bench -> debugger -> archive, with thrust-reverser and C919 E-TRAS treated as reference/sample packs. JER-221 and JER-222 closed canonical editable graph and port/wire route metadata. JER-223 closed the first sandbox scenario test bench run report for candidate graph inputs/assertions. JER-224 closed selected candidate debugging over run failures, watched values, and archive checksums. JER-225 closed a sandbox-only preflight analyzer that classifies candidates as ready, needs_evidence, or invalid_candidate before handoff/archive. JER-226 closed the first UI-facing hardware/interface design authoring surface for sandbox LRUs, cables, connectors, ports, pins, bindings, evidence gaps, validation, and archive checksums. JER-227 closed the foundation review archive bundle. JER-228 closed validation-suite timeout isolation and clean origin/main worktree hygiene. JER-229 launched Workbench v5 deep-water planning: empty-canvas graph authoring, canonical graph document v2, port drag wiring, scenario library, runner trace kernel, debug timeline, hardware evidence attachment, command palette ergonomics, and archive restore v3. JER-230 starts v5 implementation with empty-canvas sandbox authoring, input/output primitives, and canvas_authoring_mode export/import/archive evidence. JER-171 mypy wrapper remains honest evidence and may report blocked; do not claim mypy clean until it reports pass."
---

# State

Last activity: 2026-05-02

## 2026-05-01 Session — Workbench Runtime v3 Closure And v4 Launch

**Current position**: JER-204 through JER-228 are merged on the v4 line, and
JER-229 has launched Workbench v5 deep-water planning, and JER-230 starts the
first implementation slice with empty-canvas graph authoring. The active mainline is the
generic single-user foundation: editor, runner, test bench, debugger, archive,
and hardware/interface evidence. The existing thrust-reverser and C919 chains
are reference samples, not the next dedicated product panels.

**Linear control plane**:

- Runtime v3 implementation chain reached JER-203 on `origin/main`.
- New project created: `AI FANTUI LogicMVP · Editable Workbench v4 Authoring + Hardware Design`.
- JER-204 is Done after PR #186.
- JER-205 is Done after PR #187.
- JER-206 is Done after adding component-library template insert/export/archive
  evidence.
- JER-207 is Done after adding subsystem group/rename/ungroup evidence.
- JER-208 is Done after adding the hardware interface design model foundation.
- JER-209 is Done after adding connector/pin map editor evidence.
- JER-210 is Done after adding Hardware Evidence Inspector v2 selected-owner evidence.
- JER-211 is Done after adding selected graph timeline/debug linkage.
- JER-212 is Done after adding candidate-to-baseline diff review v2 evidence.
- JER-213 is Done after adding structured ChangeRequest handoff packet evidence.
- JER-214 is Done after adding handoff schema and stable serialization evidence.
- JER-215 is Done after adding archive restore/readback validation for embedded
  ChangeRequest handoff packets.
- JER-216 is Done after PR #198.
- JER-217 is Done after PR #199.
- JER-218 is Done after PR #200.
- JER-219 is Done after PR #201.
- JER-220 is Done after the foundation-first roadmap reset.
- JER-221 is Done after PR #203.
- JER-222 is Done after PR #204.
- JER-223 is Done after PR #205.
- JER-224 is Done after PR #206.
- JER-225 is Done after PR #207.
- JER-226 is Done after PR #208.
- JER-227 is Done after PR #209.
- JER-228 is Done after PR #210.
- JER-229 is Done after PR #211.
- JER-230 is In Progress for empty-canvas graph authoring palette v1.

**Runtime v3 closure summary**:

- JER-165 through JER-172 established canonical editable model conversion,
  sandbox validation, scenario selection, port-aware edge inspection, acceptance
  bundle evidence, e2e gate normalization, official mypy gate evidence, and
  archive/export gate fields.
- JER-173 through JER-190 expanded engineering editing freedom: hardware
  interface binding, typed ports, operation catalog, rule parameters, snapshots,
  keyboard duplication, multi-select, lasso/group move, direct port handles,
  canvas pan/zoom, hardware palette, diagnostics, repair actions, and
  ChangeRequest proof packet.
- JER-191 through JER-203 closed acceptance journey, lasso hardening, interface
  matrix export/import/validation/diff/selective apply/review, selected-row
  apply, group-drag flake hardening, and CSV/TSV bridge.

**Workbench v4 target**:

Workbench v4 turns `/workbench` into a higher-freedom single-user authoring,
running, testing, debugging, and archive surface. Engineers should be able to
derive a sandbox draft, edit graph structure, reuse component/subsystem
patterns, wire ports, run sandbox test scenarios, inspect failures, compare
against baseline behavior, and generate controlled review evidence before any
ChangeRequest handoff.

**v4 scope guard**:

The v4 lane is intentionally single-user first. The product priority is the
Simulink/Figma-level control-logic operation panel: high-freedom graph editing,
runner/test execution, debugger feedback, archive/readback, and then
hardware/interface evidence for one engineer working on one draft. Multi-user
collaboration, real-time sync, permissions, comments, and conflict resolution
are deferred until the single-user panel foundation is stable.

**Reference sample guard**:

The existing thrust-reverser and C919 E-TRAS logic chains stay available as
certified/reference samples and regression anchors. They are not the immediate
product expansion path. Once the foundation workbench can create, run, test,
debug, and archive arbitrary sandbox control graphs, those specific panels
should be straightforward to rebuild as examples on top of the generic base.

**JER-223 sandbox scenario test bench slice**:

- The right inspector now exposes a local Scenario Test Bench for editable tick
  inputs and expected-output assertions.
- Running the test bench produces a sandbox-only
  `workbench-sandbox-test-run-report.v1` with pass/fail assertion results,
  trace frames, validation findings, `certification_claim: none`, and
  `truth_effect: none`.
- Draft export/import, browser restore, and evidence archive carry
  `sandbox_test_bench` and `sandbox_test_run_report` with checksum coverage.
- The evaluator uses only the approved sandbox op catalog and does not call
  Python expressions, dynamic imports, network, file writes, adapters, or
  controller truth mutation.

**JER-224 candidate graph debugger slice**:

- The right inspector now exposes a Candidate Debugger panel tied to the
  selected sandbox node or edge.
- The debugger reads the latest sandbox test run report, identifies the first
  failing assertion for the selected target when available, shows the selected
  tick, watched values, and trace availability, and keeps hardware binding
  context as sandbox evidence.
- Draft export/import, browser restore, and evidence archive carry
  `candidate_debugger_view` with `truth_effect: none` and checksum coverage.
- The debugger is evidence-only. It does not call controller truth, mutate
  adapters, write hardware YAML, or make certification claims.

**JER-225 Workbench preflight analyzer slice**:

- The right inspector now exposes a Preflight Analyzer that consumes the
  candidate graph, graph validation findings, hardware/interface diagnostics,
  port compatibility, sandbox test run report, and candidate debugger view.
- The analyzer classifies local candidates as `ready`, `needs_evidence`, or
  `invalid_candidate` and emits required actions before ChangeRequest/archive
  handoff.
- Report freshness is bound to the operational sandbox model hash so imported
  or restored UI metadata does not falsely invalidate unchanged candidate
  behavior, while stale or missing run reports remain explicit findings.
- Draft export/import, browser restore, ChangeRequest proof, and evidence
  archive carry `preflight_analyzer_report` with `truth_effect: none` and
  checksum coverage.
- The analyzer is evidence-only. It does not call controller truth, mutate
  adapters, write hardware YAML, or make certification claims.

**JER-226 hardware/interface designer slice**:

- The right inspector now exposes a Hardware / Interface Design panel for
  sandbox LRUs, cables, connectors, ports, pins, signal bindings, and explicit
  evidence-gap records.
- The browser validates duplicate ids, broken references, evidence-gap
  semantics, and sandbox-only boundary constants before a design can be applied.
- Draft export/import, browser restore, preflight, ChangeRequest proof, and
  evidence archive carry `hardware_interface_designer` and
  `hardware_interface_designer_validation` with checksum coverage.
- The designer is evidence-only. It does not write certified hardware YAML,
  controller truth, adapters, frozen assets, DAL/PSSA status, or truth-level
  claims.

**JER-227 foundation review archive slice**:

- The local evidence archive now includes a `foundation_review_archive` summary
  that names the graph, test bench, run report, debugger, preflight, hardware
  evidence, ChangeRequest handoff, Linear issue body, PR proof, and red-line
  sections required for review.
- The browser emits a `foundation_review_archive_validation` report and checksum
  coverage for the review bundle.
- Archive restore validates the foundation review archive when present and
  rejects certified/truth mutation claims before returning trusted restore
  payloads.
- The archive remains sandbox-only with `truth_effect: none`, no live Linear
  mutation, no controller truth edits, and no frozen asset changes.

**JER-228 validation suite isolation slice**:

- The shared validation gate is now bounded and diagnosable before Workbench
  v5 work begins.
- `tools/run_gsd_validation_suite.py` reports structured timeout failures
  instead of hanging indefinitely when a child validation command stalls.
- The runner exposes check listing and `--only` / `--skip` isolation so Codex
  can separate the full pytest lane from schema/tool validators without editing
  business logic.
- Future issues must use fresh `codex/JER-XXX-*` worktrees created from current
  `origin/main`, not divergent local `main` or stale issue worktrees.
- Linear helper remains `api-read`; live Linear `JER-228` currently resolves to
  an unrelated non-agent issue, so this repo slice must not mutate or close that
  issue until Kogami creates/renumbers the proper validation-suite issue.

**JER-229 Workbench v5 launch slice**:

- Workbench v5 is the deep-water single-user foundation milestone after v4.
- The v5 queue is: empty-canvas authoring palette, canonical graph document v2,
  port drag wiring, scenario test case library, sandbox runner trace kernel,
  debug probe timeline, hardware/interface evidence attachment, editor command
  palette/inspector ergonomics, and review archive restore v3.
- v5 keeps thrust-reverser and C919 E-TRAS as reference/sample packs only.
- v5 excludes multi-user collaboration, product LLM/chat, controller truth
  edits, frozen asset edits, truth-level promotion, DAL, and PSSA claims.
- Coordination doc:
  `docs/coordination/editable-workbench-v5-deep-water.md`.

**JER-206 component-library closure**:

- The left-side editor toolbar exposes three reusable sandbox templates:
  `single_and_gate`, `compare_guard`, and `two_stage_interlock`.
- Template insertion creates draft nodes and internal draft edges only; it does
  not mutate certified baseline nodes or controller truth.
- Draft JSON, import/export, and evidence archive payloads carry
  `component_library` and `component_template` metadata with
  `truth_effect: none`.
- Targeted static and Playwright tests cover template exposure, insert,
  round-trip, and archive checksums.

**JER-207 subsystem-group closure**:

- The editor toolbar and inspector expose group, rename, and ungroup controls
  for selected sandbox draft nodes.
- Subsystem grouping records remain metadata only: nodes keep their original
  ids, typed ports, port handles, and draft edges.
- Draft JSON, import/export, and evidence archive payloads carry
  `subsystem_groups` metadata with `truth_effect: none`.
- Undo/redo covers group, rename, and ungroup operations through the existing
  editable history stack.

**JER-208 hardware-interface-design model closure**:

- Added `editable_hardware_interface_design_v1` as a parallel sandbox evidence
  model, not an extension of the existing thrust-reverser hardware schema.
- The model covers candidate LRUs, cables, connectors, ports, pins, signal
  bindings, and explicit evidence-gap records.
- The validator enforces schema shape, reference integrity, duplicate-id
  rejection, deterministic canonical hashing, and non-certifying boundaries.
- No UI, API, controller truth, adapter, or hardware YAML behavior changes are
  introduced by this slice.

**JER-209 connector/pin map editor closure**:

- The right inspector exposes a Connector / Pin Map section with export and
  apply controls for sandbox rows.
- Rows are derived from existing node/edge hardware bindings and carry owner,
  hardware, cable, connector, port, pin, signal, evidence, source, and
  `truth_effect: none` metadata.
- Draft export/import and evidence archive payloads include
  `connector_pin_map` with checksum coverage.
- Missing connector/pin values remain explicit `evidence_gap` fields; applying
  a map updates only existing sandbox node/edge bindings and skips missing
  owners.
- No backend API, controller truth, adapter, hardware YAML, C919 packet,
  truth-level, DAL, or PSSA behavior changes are introduced by this slice.

**JER-210 hardware evidence inspector v2 closure**:

- The right inspector now has a Hardware Evidence v2 section that tracks the
  selected node or edge owner.
- The selected-owner packet displays LRU/hardware id, cable, connector, local
  and peer ports, local and peer pins, evidence status, source ref, coverage,
  connector/pin row count, and evidence-gap counts.
- Draft export, ChangeRequest proof packet, and local evidence archive carry
  `hardware_evidence_v2` with `truth_effect: none` and checksum coverage.
- Node selection keeps the read-only hardware evidence API signal rows; edge
  selection uses the candidate edge binding only because no certified edge
  truth map exists.
- No controller truth, backend truth, adapter, frozen YAML, C919 packet,
  truth-level, DAL, or PSSA behavior changes are introduced by this slice.

**JER-211 selected debug timeline closure**:

- The bottom workbench area now exposes a Selected Debug Timeline panel tied to
  the current node or edge selection.
- The selected timeline packet records target owner, scenario id, diff verdict,
  trace-link status, graph context, hardware overlay, and latest diff summary.
- Draft export, ChangeRequest proof packet, and local evidence archive carry
  `selected_debug_timeline` with `truth_effect: none` and checksum coverage.
- Running the sandbox updates the selected target's debug verdict without
  changing controller truth or certifying the candidate.
- No controller truth, backend truth, adapter, frozen YAML, C919 packet,
  truth-level, DAL, or PSSA behavior changes are introduced by this slice.

**JER-212 diff review v2 closure**:

- The workbench right inspector now exposes a Diff Review v2 panel next to the
  baseline diff surface.
- The review packet records verdict, review readiness, archive state, selected
  target, scenario, first divergence text, hardware evidence summary, and
  baseline source.
- Draft export, ChangeRequest proof packet, and local evidence archive carry
  `candidate_baseline_diff_review_v2` with `truth_effect: none`, certification
  claim `none`, and checksum coverage.
- Equivalent, divergent, invalid model, and invalid scenario states remain
  review evidence only; no sandbox candidate can be marked certified.
- No controller truth, backend truth, adapter, frozen YAML, C919 packet,
  truth-level, DAL, or PSSA behavior changes are introduced by this slice.

**JER-213 ChangeRequest handoff packet closure**:

- The ChangeRequest Handoff section now emits a structured
  `changerequest_handoff_packet` JSON payload in addition to the Linear issue
  body and PR proof text.
- The handoff packet carries Outcome, Acceptance, Boundaries, Evidence
  Required, Red lines, Test delta placeholders, proof checksums, and the
  embedded ChangeRequest proof packet.
- Draft export and local evidence archive carry the handoff packet with
  checksum coverage.
- The workbench still performs no live Linear mutation; all handoff artifacts
  are copy-ready review evidence.
- No controller truth, backend truth, adapter, frozen YAML, C919 packet,
  truth-level, DAL, or PSSA behavior changes are introduced by this slice.

**JER-214 handoff schema and stable serialization closure**:

- Added `workbench_changerequest_handoff_v1` as the machine-readable schema for
  the browser-generated `changerequest_handoff_packet`.
- Added a Python validator and canonical SHA256 hash helper for the handoff
  packet contract.
- Added a validation-suite check so the handoff packet schema participates in
  the default GSD validation surface.
- Browser-side evidence checksums now use stable key-sorted JSON before hashing,
  so object key insertion order does not change review checksums.
- The handoff packet remains draft-only: no live Linear mutation, no controller
  truth mutation, no frozen asset mutation, and no truth-level, DAL, or PSSA
  impact.

**JER-215 archive restore handoff validation closure**:

- Archive restore/readback now emits `changerequest_handoff_validation` with
  `pass`, `fail`, or `not_present` status.
- Embedded `changerequest_handoff_packet` payloads are validated with the
  repo-owned schema helper before restore payloads are trusted.
- Evidence archive UI checksums are recomputed with the browser-compatible
  `ui_draft_*` FNV checksum contract and mismatches fail restore.
- Archives without a handoff packet remain backward-compatible and report
  `not_present` rather than blocking restore.
- No controller truth, backend truth, adapter, frozen YAML, C919 packet,
  truth-level, DAL, or PSSA behavior changes are introduced by this slice.

**JER-216 subsystem template capture closure**:

- The component library now captures a selected subsystem or multi-selected
  sandbox draft node set as a reusable template.
- Captured templates preserve node ops, labels, typed ports, rules, internal
  edges, subsystem metadata, hardware/interface overlay metadata, and explicit
  sandbox provenance.
- Inserting a captured template creates fresh draft node ids and a new
  sandbox-only subsystem group; it does not mutate certified baseline nodes or
  controller truth.
- Draft export/import and local evidence archives carry captured template
  metadata under `component_library` with checksum coverage and
  `truth_effect: none`.

**JER-217 subsystem interface contract editor closure**:

- The selected subsystem inspector adds a boundary interface editor for
  input/output contract ports.
- Contract ports carry label, signal id, value type, evidence status, source
  ref, candidate state, and `truth_effect: none`.
- Draft export/import, evidence archive checksums, and captured subsystem
  template reinsertion preserve these ports without changing controller truth.

**JER-218 workspace document state kernel closure**:

- The `/workbench` status bar exposes a sandbox-only workspace document
  revision readout with action count, undo depth, and redo depth.
- Draft export/import, browser restore, and local evidence archives carry
  `workspace_document` with `candidate_state: sandbox_candidate` and
  `truth_effect: none`.
- Evidence archive output includes `workspace_document_checksum` for review
  reproducibility.

**JER-219 high-freedom canvas interaction evidence in progress**:

- The `/workbench` status bar exposes selected node count, selected edge count,
  and last canvas action as sandbox-only interaction evidence.
- Draft export/import and local evidence archives carry
  `canvas_interaction_summary` with `candidate_state: sandbox_candidate` and
  `truth_effect: none`.
- Evidence archive output includes `canvas_interaction_summary_checksum` for
  review reproducibility.
- Existing multi-select, duplicate/delete, lasso/group move, undo/redo, and
  workspace document flows remain sandbox-only and do not mutate controller
  truth.

**Hard boundaries**:

- Sandbox edits and hardware/interface design records remain candidate evidence.
- `src/well_harness/controller.py` truth semantics are not changed by this lane.
- Frozen adapters, frozen hardware YAML, and the C919 reference packet remain
  untouched.
- No truth-level, DAL, or PSSA promotion is made by Codex Daily Lane.
- Product LLM/chat behavior remains frozen; OpenAI/Codex/Symphony are execution
  workflow tools, not product truth engines.

**Known gate status**:

- JER-171 defines the official mypy evidence command, but the historical type
  baseline may still report `status: blocked`.
- PR proof packets must not claim e2e 49/49 or mypy clean unless those gates are
  independently restored and verified.

## 2026-04-23 Session — Timeline Simulator (全流程故障率仿真) · 4-PR delivery

**Goal**: User request "增加一个全流程故障率仿真功能模块" — timeline-driven simulation driving both control logic systems (FANTUI demo + C919 E-TRAS) through a "时间-指令/状态" table.

**Architecture (4 PRs, each followed by a Codex review):**

### PR-1 · Timeline engine foundation (ecdd259 + ce7265c)
- `src/well_harness/timeline_engine/` new package: schema / validator / player / Executor protocol
- 7 event kinds: set_input, ramp_input, inject_fault, clear_fault, mark_phase, assert_condition, start_deploy_sequence
- Half-open [start, end) intervals, deterministic tick order
- Codex PR-1 fixes: P1×1 (deployed_successfully requires L4 AND thr_release) + P2×4 (canonical id "c919-etras", fault_schedule FIFO match, validator tuple-type, FaultScheduleEntry invariants) + P3×1 (cascade iteration via executor.logic_node_ids)

### PR-2 · FANTUI Executor + API (0c21236 + 5a1556a)
- `FantuiExecutor` wraps DeployController + LatchedSwitches + SimplifiedDeployPlant
- `/api/timeline-simulate` on `demo_server.py` port 8002
- 2 fixtures: `nominal_landing.json`, `sw1_stuck_at_touchdown.json`
- 13-pair fault whitelist
- Codex PR-2 fixes: MAJOR×4 (logic_stuck_false → blocked mapping, cascade suppression under no-fault runs, API runtime-error → 400, fault-id whitelist) + MINOR×2 (tick/event caps, fixture N1k unit)

### PR-3 · C919 E-TRAS Executor + API (0eae71e + 2e9571b)
- `C919ETRASExecutor` wraps frozen-V1.0 `C919ReverseThrustSystem` (12-step tick) + TR-position plant + lock plant + unlock-engaged latch
- `/api/timeline-simulate` on `c919_etras_panel_server.py` port 9191
- 2 fixtures: `c919_nominal_deploy.json`, `c919_tr_inhibited_blocks_deploy.json`
- 14-pair fault whitelist
- Auto-derive ATLTLA/APWTLA from TRA window membership ([-6.2°,-1.4°] / [-9.8°,-5.0°])
- Codex PR-3 fixes: MAJOR×3 (unlock_engaged now releases at S9_LOCK_CONFIRM so multi-cycle sim reaches S10, ln_fadec_stow_command no longer false-positive blocked in cruise, TimelineOutcome.extra + Executor.summarize_outcome architecture for system-specific outcome)

### PR-4 · Timeline Simulator UI (67af398)
- `src/well_harness/static/timeline-sim.html` served from both port 8002 and 9191
- 4 built-in presets + custom mode
- Client-side router: `system="c919-etras"` → POST :9191, else same-origin
- Outcome cards (system-aware), logic-node timeline bars, assertions list, failure-cascade table
- 4 smoke tests

**Regression**: 765 tests green (+40 vs start of session) · 0 CRITICAL / 0 failing.

**Key files**:
- `src/well_harness/timeline_engine/` (new package, 5 modules)
- `src/well_harness/timeline_engine/executors/{fantui,c919_etras}.py`
- `src/well_harness/timelines/*.json` (4 fixtures)
- `src/well_harness/static/timeline-sim.html`
- `src/well_harness/demo_server.py` (+/api/timeline-simulate)
- `scripts/c919_etras_panel_server.py` (+/api/timeline-simulate + /timeline-sim.html route)
- `tests/test_timeline_*.py` (4 test modules, 40 tests)

**User-visible**: `python3 -m well_harness.demo_server` (:8002) + `python3 scripts/c919_etras_panel_server.py` (:9191) → browser `http://localhost:8002/timeline-sim.html` → pick preset → Run.

## 2026-04-23 Session — demo.html L3 wire clarity (iter-7 → iter-9)

**Goal**: Show L3 independently checks `engine_running` and `aircraft_on_ground` (not inherited from L2) in the SVG chain diagram, without creating visual wire crossings.

**Iterations and Codex verdicts:**
- iter-7 (`f700838`): off-page stub (x=241, y=278/282) — **P2×2** (eec clearance 0.1px, TLS clearance 1.1px at active 1.8px stroke)
- iter-8 (`95973e2`): stubs moved to (x=244, y=281/286) — **P2×1** (aircraft→rev_inh only 2.2px SVG, ~1.6px rendered at 0.73× scale)
- iter-9 (`4189198`): L3 gate height 38→50, rev_inh→L3 branch y=290→304, aircraft stub y=286→290 — **APPROVE × 2** (code review + dual-role)

**Final clearances at active 1.8px stroke:**
- TLS(y=276) → engine(y=281): 3.2px SVG / 2.3px rendered
- engine(y=281) → aircraft(y=290): 7.2px SVG / 5.3px rendered
- aircraft(y=290) → rev_inh(y=304): 12.2px SVG / 8.9px rendered

**Codex dual-role verdict (Role A 商业立项 + Role B 动力控制逻辑):**
- No P0/P1/P2 blockers; single P3 observation (TLS→L3 feedback line ~3.2px from engine stub, not blocking at current browser size)
- L3 engineering semantics preserved: `controller.py:69` independent checks unchanged
- `pytest -q tests/test_controller.py -k 'logic3 or logic4'` 6 passed

### 2026-04-23 — Demo UI bug fixes (user-reported)

**Bug 1: VDT slider silently ignored in auto_scrubber mode**
- Root cause: `auto_scrubber` uses plant-simulated VDT driven by `pdu_motor_cmd`, ignoring `deploy_position_percent` from the request. User dragging VDT to 95% had zero effect on L4, but clicking the "着陆展开全链路" preset first worked because it switched to `manual_feedback_override`.
- Fix (`f007483` → `daca0cf`): disable the VDT slider in `auto_scrubber` + dynamic hint; `renderLeverHud` now uses `data.hud.deploy_position_percent` (backend-authoritative) instead of the request value; preserve slider state across mode toggles.

**Bug 2: L1 red under "着陆展开全链路" preset**
- Root cause: original preset set VDT=95, which flips `reverser_not_deployed_eec` to False and correctly fails L1's `!DEP` interlock — but that contradicts the "full chain active" framing.
- Fix (`f007483`): landing-deploy now VDT=0 (deployment-in-progress: L1+L2+L3 active, L4 pending on VDT90); max-reverse relabeled "展开到位" with TRA=-31.5 (avoids exclusive lower bound) + VDT=100 (post-deploy: L1 correctly blocked, L4 active).

**Codex reviews**: P2 found on `f007483` (hard-reset slider discarded user state + stale readout) → fixed in `daca0cf` → **APPROVE** with no new findings. 725 tests pass.

### 2026-04-23 — L4 reverse_travel boundary bug + L1 post-deploy clarification (`9d18f05`)

**User screenshot report**: TRA=-32°, VDT=100%, manual_override, all inputs green — L1 and L4 both BLOCKED. Two distinct root causes:

**Bug A (real, now fixed)**: L4 `tra_deg` used `between_exclusive(-32, 0)`, so TRA=-32° (mechanical stop, slider's leftmost value) silently failed the strict lower bound. UI told the user "可以在 -32°~0° 自由拖动", controller disagreed at the edge.

Introduced new comparison type `between_lower_inclusive` (lower ≤ val < upper) and applied to L4 `tra_deg`. Upper bound stays strict (TRA=0° is forward detent). Touches 11 files:
- `controller.py` / `system_spec.py` / `reference_thrust_reverser.spec.json` — declarations
- `scenario_playback.py` / `demo.py` / `tools/generate_adapter.py` — four implementation sites kept in sync
- `demo_server.py::_lever_summary` — Bug B explanation
- `static/demo.js` — max-reverse preset TRA restored to -32°
- `tests/test_demo.py`, `tests/fixtures/demo_answer_asset_v1.json` — comparison string rename
- `tools/demo_path_smoke.py::scenario_lever_extreme_clamp` — previously codified the bug; now correctly asserts L4 active + THR_LOCK active at TRA=-32°

**Bug B (semantically correct, now explained)**: At VDT=100%, `reverser_not_deployed_eec = (100 ≤ 0) = False` → L1's `!DEP` interlock correctly fails. L1 is a first-unlock gate; once reverser is deployed, `!DEP` naturally releases — this is design behavior, not a failure. `_lever_summary` now appends a clarifying note on L4-active branches: "L1 此刻阻塞是预期：反推已部署 → !DEP 自然回落，L1 属于首次解锁门，已完成使命。"

**Codex review verdict**: APPROVE on all 5 focus areas (new comparison consistency across 4 impl sites · boundary behavior · old `between_exclusive` untouched · smoke-test flip logically correct · L1 post-deploy heuristic accurate).

**Live verification** on user's exact input (TRA=-32, VDT=100, manual, all toggles on): L2/L3/L4 active, THR_LOCK active, L1 blocked with explanatory note.

---

## Previous Position (P43-03 · 2026-04-21)

**P43-03 COMPLETE · R1-R6 Authority Contract PASS=6 · Workflow State Machine wired · 853 tests green**

### 2026-04-21 Session Summary

**P43-02.5 Completed (全部 Steps A-E committed):**
- Step A: Backend audit confirmed (SYSTEM_REGISTRY c919-etras, lru_cache(5), 17-field asserted_component_values)
- Step B: SVG 22 truth-tracked + 10 annotation nodes, 6-column grid, 41 conn-lines, c919- prefixed defs
- Step C: C919 state dispatcher, C919_SVG_NODE_MAP, asserted_component_values driven
- Step D1: 8 chat.js touchpoints (T1-T8), ALLOWED_SYSTEM_IDS +c919-etras, operate stub
- Step D2: 19 visible controls + debounce 150ms + Advance/Stow latch buttons
- Step E: Hardware tooltips, freeze banner, cache-busting, schema-alignment test (5/5), carry-forward artifacts
- Gate: `GATE-P43-02.5-CLOSURE` submitted to Kogami

**frozen_v1 Migration (branch: claude/c919-etras-frozen-v1-migration, pushed):**
- `src/well_harness/adapters/c919_etras_frozen_v1/` — 14 modules, 12-step tick, frozen spec V1.0
- `scripts/c919_etras_panel_server.py` — standalone MFD panel server (port 9191)
- `src/well_harness/static/c919_etras_panel/index.html` — aviation MFD panel UI
- `tests/test_c919_etras_frozen_v1_{unit,integration}.py` — 40 tests
- `docs/c919_etras/requirements_v0_9.md` — standardised V0.9 requirements
- 845 tests pass, 0 regression

**Governance:**
- DEC-FANTUI-001: frozen_v1 as independent reference engine (Notion synced)
- DEC-FANTUI-002: Subagent priority principle added to CLAUDE.md (Notion synced)
- GATE-P43-02.5-CLOSURE: Submitted (Notion synced)

Phase: P43-02 Batch (P43-02 + P43-03 + P43-04 combined · Q1=D · plan-quality gate CLEARED · execution gate `GATE-P43-02-BATCH-CLOSURE` remains pending all 19 Exit Criteria + 13 Codex `可过-Gate` trailers)

### GATE-P43-02-BATCH-PLAN-QUALITY Approved (2026-04-21 · Kogami Option A)

**Kogami decision**: Approve all 8 §Q Q1 §3d delta entries + `GATE-P43-02-BATCH-PLAN-QUALITY` (plan-quality 前置门 CLEARED).

**Approval act** (single commit):
- `P43-00-PLAN.md` v7 → **v8** · §3d amended (Source Code Whitelist +1 row `pyproject.toml` · Doc Deliverables Whitelist +1 row `docs/<system>/traceability_matrix.md` per-system · Test Whitelist +6 rows 4 tests + 2 fixture dirs) · §8b governance ledger appended
- `P43-02-00-PLAN.md` v3.1 frontmatter → `APPROVED`
- `.planning/STATE.md` + `.planning/ROADMAP.md` updated to reflect execution authorization

**v7 → v8 invariants preserved**: only §3d (3 sub-sections) amended · Q-lock untouched · Blacklist/Schema/Tooling+CI/兼容性 unchanged · §3e R1-R6 mechanical column unchanged · §1/§2/§3a-c/§3e/§4-§11 unchanged.

### P43-02 Batch · Execution authorization

Executor authorized to proceed with §3 execution plan:
- **Next immediate action**: Step 3a/A (workflow automaton contract docs · `docs/P43-workflow-automaton-contract.md` + `.yaml` · doc-only · no source changes · no Codex round required)
- **Subsequent 13 Codex Q7=A rounds** (per plan §8): 10 adapter-boundary + 3 sub-phase closure — triggered at Step 3a/B onwards per touchpoint
- **Source-level work** begins at Step 3a/B (R1-R6 authority-contract tests scaffold + `tools/check_authority_contract.py`) — Codex round #1

**Execution gate pending** (`GATE-P43-02-BATCH-CLOSURE`): submission blocked until all 19 Exit Criteria green + 13 Codex rounds all `可过-Gate` + three-lane regression PASS vs post-P43-01 baseline `61b12b3`.

### P43-02 Batch plan arc (2026-04-21 · 5 revisions · 4 Codex rounds)

| Revision | Commit | Codex round | Verdict |
|----------|--------|-------------|---------|
| v1 (draft) | `03e4acf` | r1 | 需修正·信号强 (6 required + 2 polish) |
| v2 (surgical rewrite) | `1781641` | r2 | 需修正·信号强 (3 required + 1 polish) |
| v3 (surgical addendum) | `ee0d018` | r3 | 需修正·信号弱 (3 text + 1 polish) |
| v3.1 (janitorial) | `ac30621` | r4 pass 1 | 需修正·信号弱 (version drift) |
| v3.1 (scrub 1) | `4aed5fd` | r4 pass 2 | 需修正·信号弱 (§6/§7 lifecycle) |
| **v3.1 (final)** | **`987d723`** | **r4 final** | **`可过-Gate`** |
| v3.1 (+§10 submission) | `b010e36` | — | Kogami submission ready |
| **v3.1 APPROVED · P43-00 v8** | `(this commit)` | — | **GATE-P43-02-BATCH-PLAN-QUALITY Approved (Kogami Option A)** |

### P43-02 Batch · Plan content digest (v3.1 · APPROVED)

- **Scope**: 3 sub-phases combined · ~2100-2700 LOC · 3-4 days wall-time
  - P43-02: Workflow automaton + authority contract R1-R6 + archive compat + API contract lock + multi-tab lock + dual-SHA manifest
  - P43-03: Server-side PDF/DOCX extraction + `/api/document/extract` endpoint + Bug D fix (semantic category binding) + readAsText regression rewrite
  - P43-04: FREEZE event + `workbench freeze` CLI + `docs/<system>/traceability_matrix.md` SKELETON emission
- **Tests**: 16 authority (14 R1-R6 + 2 observability) + ~30 other ≈ **~46 new default-lane tests** · plus e2e opt-in
- **Endpoints**: 8 total (P43-01's 7 + `/api/document/extract`) · `/api/workbench/freeze` dropped (CLI-only)
- **Codex arc planned**: 13 rounds (10 adapter-boundary + 3 sub-phase closure)

### Archive — prior position (P43-01 Contract Proof Spike CLOSED · 2026-04-21)

[P43-01 prior-position history preserved below]

---


### P43-02 Batch plan submission arc (2026-04-21 · same-day path ① · 5 plan revisions · 4 Codex rounds)

| Revision | Commit | Codex round | Verdict | Closure |
|----------|--------|-------------|---------|---------|
| v1 (draft) | `03e4acf` | r1 | 需修正·信号强 (6 required + 2 polish) | path ① → v2 |
| v2 (surgical rewrite) | `1781641` | r2 | 需修正·信号强 (3 required + 1 polish) | path ① → v3 |
| v3 (surgical addendum on v2) | `ee0d018` | r3 | 需修正·信号弱 (3 text + 1 polish) | path ① → v3.1 janitorial |
| v3.1 (janitorial) | `ac30621` | r4 pass 1 | 需修正·信号弱 (version drift) | scrub → `4aed5fd` |
| v3.1 (scrub 1) | `4aed5fd` | r4 pass 2 | 需修正·信号弱 (§6/§7 lifecycle drift) | scrub → `987d723` |
| **v3.1 (final)** | **`987d723`** | **r4 final** | **`可过-Gate`** | **submission-blocker 清除** |
| v3.1 (+§10 submission) | `(this commit)` | — | — | Kogami submission ready |

### P43-02 Batch plan v3.1 · Codex r4 final endorsement (verbatim)

> **可过-Gate — 未发现新的阻断项。§6 顶部 callout 已写明 v3.1 lifecycle 对齐 (r4)，生命周期文案已统一到 v3.1 / Codex r4。§7 stop point #6 已改为 Codex r4。987d723 仅改这一份 plan，diff 只覆盖指出的 §6/§7 生命周期漂移，没有引入新的文案 drift。r1/r2/r3 closure 和当前 r4 提交态仍自洽。**
>
> *边界说明：本次仅是 GATE-P43-02-BATCH-PLAN-QUALITY submission-blocker 复检，不涉及源码或 Exit Criteria #1-#19 证据重审。*

### P43-02 Batch · §3d whitelist delta request (Q1=A · 8 entries)

Gate approval requires amending `P43-00-PLAN.md` v7 §3d with 8 new entries (see plan §10.2 for full table). Rejection fallbacks enumerated in plan §7 stop point #7.

1. `tests/test_p43_document_pipeline.py` (Test Whitelist)
2. `tests/test_p43_clarification_stable_ids.py` (Test Whitelist · 6 regression cases for Bug D semantic category binding)
3. `tests/test_p43_freeze_gate.py` (Test Whitelist)
4. `tests/test_p43_dual_sha_manifest.py` (Test Whitelist · Q12=B+a null-tolerant 4-组合)
5. `tests/fixtures/p43_document_pipeline/` (Test Whitelist · ~5 files PDF/DOCX/TXT/MD corpus)
6. `tests/fixtures/p43_pre_archive/` (Test Whitelist · ~3 files backward-compat)
7. `pyproject.toml` L1 additive `[project.optional-dependencies] document = ["pypdf>=4.0", "python-docx>=1.0"]` (Source Code Whitelist new row · repo-root packaging metadata)
8. `docs/<system>/traceability_matrix.md` per-system freeze-time SKELETON emission (Doc Deliverables Whitelist new row · aligned with P43-00 §2c:190 P34-P42 precedent)

### P43-02 Batch · Plan content digest (v3.1)

- **Scope**: 3 sub-phases combined · ~2100-2700 LOC · 3-4 days wall-time
  - P43-02: Workflow automaton + authority contract R1-R6 + archive compat + API contract lock + multi-tab lock + dual-SHA manifest
  - P43-03: Server-side PDF/DOCX extraction + `/api/document/extract` endpoint + Bug D fix (semantic category binding) + readAsText regression rewrite
  - P43-04: FREEZE event + `workbench freeze` CLI + `docs/<system>/traceability_matrix.md` SKELETON emission
- **Tests**: 16 authority (14 R1-R6 + 2 observability) + ~30 other ≈ **~46 new default-lane tests** · plus e2e opt-in (multi-tab + R3 runtime mutation + R5 Node parity deferred to P43-09)
- **Endpoints**: 8 total (P43-01's 7 + `/api/document/extract`) · `/api/workbench/freeze` dropped (CLI-only)
- **Codex arc**: 13 rounds (10 adapter-boundary + 3 sub-phase closure) planned for execution
- **Key structural decisions across revisions**:
  - v2 `open_questions_<system>.md` 自创分叉 → v3 回归 parent-anchored `docs/<system>/traceability_matrix.md` (r2 #1 closure)
  - v2 source-order positional mapping for Bug D → v3 semantic `Ambiguity.category` L1 additive field + LLM prompt extension + clarify-{i} warning fallback (r2 #3 closure)
  - v2 pyproject.toml pre-emptive → v3 formal §Q Q1 delta entry #7 (r2 #2 closure)
  - Q5-B (harden apply_all_safe to strict bool) deleted as L3 violation (r1 #6 closure · v2) · only Q5-A soften text remains

---

### P43-01 Execution arc

| Step | Commit | Outcome |
|------|--------|---------|
| A partial | `48e4796` | S1 fixture + draft report + Kogami escalation (2 new Counter-F bugs surfaced — B1/B2 beyond plan prediction) |
| B (Kogami Option X) | `5d2d3ec` | Bugs A/B1/B2 surgical fix (~5 LOC at `ai_doc_analyzer.py:840,843,866,867`) + 4 regression tests |
| B Codex | `8d76cf5` | `可过-Gate` + 3 optional doc polish items applied |
| D/E/F | `7fd243d` | Playwright readAsText evidence (pdf=`%PDF-1.7` garbage confirmed) + `docs/P43-api-contract-lock.yaml` (7 endpoints) + R6/R7/R8 inventory |
| G finalize | `4d40aee` | Executive summary + Exit Criteria mechanical verification |
| G scrubs | `6729768` / `e86a8cc` / `9a51183` | Closed Codex r1 (3 fixes) / r2 (7 fixes) / r3 (1 fix) |
| G closure | `e579a16` | Codex r4 `可过-Gate` trailer + Kogami submission |
| Gate approval | (this commit) | Kogami GATE-P43-01-CLOSURE approved |

### Counter F closure (4 bugs · unified root cause)

All four bugs traced to a single pattern: no internal contract lock between producer and consumer **within** `run_pipeline_from_intake()`'s own data path.

| Bug | Anchor | Fix status |
|-----|--------|------------|
| A | `ai_doc_analyzer.py:840` (READ side `blocking_reasons` / EMIT `blockers`) | Fixed in Step B |
| B1 | `ai_doc_analyzer.py:866` (`bundle.playback_report.scenarios` → `1 if .. else 0`) | Fixed in Step B |
| B2 | `ai_doc_analyzer.py:867` (`bundle.fault_diagnosis_report.fault_modes` → `1 if .. else 0`) | Fixed in Step B |
| D | `ai_doc_analyzer.py:799` (`clarify-{i}` vs stable question_id consumer at `document_intake.py:839`) | Deferred to P43-03 per Q12=B+a |

### Three-lane regression (re-run 2026-04-21)

- Default pytest: **800 passed, 1 skipped** (P42 baseline 796 + 4 spike default tests · zero regression)
- E2E pytest: **50 passed** (P42 baseline 49 + 1 Playwright readAsText e2e · includes adversarial wrapper)
- Zero regression vs main baseline `a6521ca`.

### Non-blocking polish (future slice)

- `src/well_harness/demo_server.py:2666` error message says `"apply_all_safe must be true"` but runtime guard is truthiness-based. Codex r4 flagged as explicitly non-blocking; fix candidate for P43-02 or a standalone cleanup slice.

### Next: P43-02 (workflow / orchestrator / panel)

Per plan §3 Step G item 4, Gate approval authorizes P43-02 kickoff. P43-02 should consume `docs/P43-api-contract-lock.yaml` as authoritative endpoint contract for all new frontend consumers, following S3b grep-alignment pattern.

---

## Archive — prior position (P43 plan Gate Approved 2026-04-20)

**P43 milestone plan v7 GATE-Approved (Kogami 2026-04-20) · P43-01 Contract Proof Spike next**

Phase: P43 — Control Logic Workbench end-to-end milestone

- Branch `codex/p43-control-logic-workbench` merged to `main` via non-FF (`99211bd`)
- 7 plan revisions v1→v7 · 6 Codex adversarial rounds · 3 Kogami R4 arbitrations
- v7 closes all Codex r6 residuals (KL-1/2/3) via Kogami strengthen-before-Gate directive
- §3d 12+ file whitelist with L1/L2/L3 ladder · §3e 6 authority contract rules (R1-R6) mechanically verifiable in default lane
- Q answers locked: Q1=D (4 gates) · Q2=A (vanilla JS) · Q4=A (alias approval) · Q7=A (Codex per touchpoint) · Q8=B (spike + contract lock) · Q10=B (md+yaml) · Q12=B+a (server-side pypdf+docx, no OCR)

### Codex adversarial review (P43 · 6 rounds · path ① governance arc)

P43 path ① governance pattern extends P42 precedent. 6 rounds of adversarial review refined plan from v1 needing-block through surgical closure:

| r | v | verdict | action |
|---|---|---------|--------|
| 1 | v1 | 需阻止（6 counters A-F） | Kogami path ① → v2 |
| 2 | v2 | 需修正·信号强（4 cuts） | path ① → v3 |
| 3 | v3 | 需修正·信号强 | path ① → v4 |
| 4 | v4 | 需修正·信号强（3 surgical） | path ① → v5 |
| 5 | v5 | 需修正·信号强（3 precise · "值得 v6 最后一次") | Kogami Option A → v6 |
| 6 | v6 | 需修正·信号强（3 residuals · "不建议 v7") | Kogami Option B + strengthen directive → **v7 Gate Approved** |

### Next after GATE-P43-PLAN (v7) Approved

按 Q1=D gate batching strategy：
1. Draft `P43-01-00-PLAN.md` (Contract Proof Spike · 8 scope items · ~1 day · ~200 LOC fix + docs + asserted-pass harness)
2. Submit independent GATE-P43-01-PLAN
3. After GATE-P43-01-PLAN Approved → execute P43-01 · produce `docs/P43-contract-proof-report.md` + `docs/P43-api-contract-lock.yaml`
4. Kogami re-review post-spike → determine whether P43-02..10 scope holds or v8 needed

---

## Archive — prior position (P42 CLOSED 2026-04-20)

**P42 v2 executed & green — awaiting `GATE-P42-CLOSURE: Approved` (2026-04-20)**

Phase: P42 — truth_level + status schema + machine SoT + generator fix (path ① post-Codex)

- Branch `codex/p42-truth-level-schema` 8 commits on top of `main a05bb6d`:
  · `42acdef` feat(P42-00): plan v1 (230 行 · 4 counter · Q1-Q3)
  · `eaa409a` docs(P42-00-codex): plan v2 (post-Codex · 431 行 · 7 counter · Q1-Q5 · verified-by codex-gpt54-xhigh)
  · `0a13bc2` feat(P42-01): dataclass truth_level/status=None + to_dict 剥 None + JSON schema extend
  · `bc33c95` feat(P42-02): fill 5 metadata instantiations (REF/BLEED/EFDS/LG/C919)
  · `c174734` feat(P42-03): generate_adapter.py 删 shadow class + 模板 demonstrative/Upgrade pending
  · `30cf3be` feat(P42-04): adapter_truth_levels.yaml machine SoT + markdown 注脚
  · `3ad64e6` test(P42-05): 29 new tests (schema+serializer+generator + bidir consistency)
  · closure (本 commit) · ROADMAP + STATE + Notion DECISION
- Three-lane regression (vs P41 head a05bb6d):
  · default: **796 passed** / 1 skipped / 49 deselected in 90.60s (+29 vs P41 767 · 17 schema+serializer+generator + 12 bidir)
  · e2e: **49 passed** (identical · 含 adversarial wrapper)
  · adversarial wrapper: **1 passed** (8/8 inside identical)
- Gates (Kogami 2026-04-20 · 今日累计 **15 个** · 多一层 P42 v1→v2 仲裁):
  · P31-GATE · GATE-P32-CLOSURE · GATE-P34-CLOSURE · GATE-P35-PLAN/CLOSURE · GATE-P36β-PLAN/CLOSURE · GATE-P37-PLAN/CLOSURE · GATE-P38-PLAN/CLOSURE · GATE-P40-PLAN/CLOSURE · GATE-P41-PLAN 隐式/CLOSURE · **GATE-P42-PLAN (v1) · 路径① 仲裁 · GATE-P42-PLAN (v2)** ✅
  · `GATE-P42-CLOSURE: Pending`

### Codex adversarial review (P42 唯一调用点)

P42 是唯一一个在 v1 plan 通过 Gate 后因 Codex 对抗性审查返 **需修正 · 信号强** 而被 Kogami 选"路径①"重走 GATE-PLAN 的 Phase。

- Codex GPT-5.4 xhigh · `/codex-gpt54` · 82,646 tokens · 3 structural counters A/B/C
- Counter A · `**asdict(metadata)` 真实序列化路径抹 provenance 语义边界
- Counter B · 业务语义默认 + `generate_adapter.py:74-79` shadow class 使新 adapter 静默滑过
- Counter C · runtime hardcode + markdown + test hardcode 三源无机器闭合 · CI 可假绿
- Executor 核验两条事实断言均真实 · 停工 + 3 路径升级 Kogami
- Kogami 选 ① · v2 plan 7 counters (C1-C4 + C5/C6/C7 verified-by codex-gpt54-xhigh) · Executor 用自己语言重写，不直接复制

### Registry 2 维状态（P42 落后 · 现 machine-enforced via bidir test）

| system_id | truth_level | status | 与 runtime 绑定 |
|-----------|-------------|--------|-----------------|
| `thrust-reverser` | certified | In use | `controller_adapter.REFERENCE_DEPLOY_CONTROLLER_METADATA` |
| `bleed-air-valve` | demonstrative | Frozen | `adapters.bleed_air_adapter.BLEED_AIR_CONTROLLER_METADATA` |
| `emergency_flare_deployment_system` | demonstrative | Frozen | `adapters.efds_adapter.EFDS_CONTROLLER_METADATA` |
| `minimal_landing_gear_extension` | demonstrative | Frozen | `adapters.landing_gear_adapter.LANDING_GEAR_CONTROLLER_METADATA` |
| `c919-etras` | certified | In use | `adapters.c919_etras_adapter.C919_ETRAS_CONTROLLER_METADATA` |

P42 把三层（runtime / yaml / markdown）一致性从 "人工保" 转为 "CI 保"：yaml SoT 被改但 markdown 忘同步 → 测试红；新 adapter 生成但没登记 yaml → 测试红；registry 某行 level/status 改但 runtime metadata 忘改 → 测试红。

### Next after P42-CLOSURE

按 R4 等 Kogami 明示 —— 候选：
1. P43 adapter freeze/upgrade 模板化（Kogami 2026-04-20 已预定）
2. P44 runtime API surface（暴露 truth_level 到 demo_server · P42 Q3=B 推后项）
3. P45 全量 yaml-ify registry（absorb upstream_source/authority/notes · P42 Q4=A 未做部分）
4. 其他 · R4 不自选

---

## Archive — prior position (P40 pre-close, before P41/P42)

**P40 drafted & green — awaiting `GATE-P40-CLOSURE: Approved` (2026-04-20)**

Phase: P40 — CI-level SHA enforcement（证迹补完第二轮 ε 段 · 基础设施）

- Branch `codex/p40-ci-sha-enforcement` 4 commits on top of `main 74a459a`:
  · `9a589bb` feat(P40-00): plan (379 行 · Tier 1 · 4 counter · Q1-Q3 Executor 预签)
  · `ee72271` feat(P40-01): docs/provenance/sha_registry.yaml (46 行 · SoT · 2 files)
  · `12f7b94` feat(P40-02): scripts/verify_provenance_hashes.py (195 行 · stream-hash · exit 1 on drift)
  · `bf60eb8` test(P40-03): tests/test_provenance_sha_integrity.py (96 行 · 3 tests · default lane)
- Three-lane regression (vs P38 head 74a459a):
  · default: **765 passed** / 1 skipped / 49 deselected in 89.05s (+3 vs P38 · 设计预期)
  · e2e: **49 passed** (identical)
  · adversarial wrapper: **1 passed** (8/8 inside identical)
- Gates (Kogami 2026-04-20, 今日累计 11 个):
  · P31-GATE · GATE-P32-CLOSURE · GATE-P34-CLOSURE · GATE-P35-PLAN/CLOSURE · GATE-P36β-PLAN/CLOSURE · GATE-P37-PLAN/CLOSURE · GATE-P38-PLAN/CLOSURE · GATE-P40-PLAN (Q1-Q3 Executor 预签 Kogami 授权) ✅
  · `GATE-P40-CLOSURE: Pending`

### Registry 5 rows (status after P38)

| system_id | truth_level | status | authority |
|-----------|-------------|--------|-----------|
| `thrust-reverser` | certified | In use | Kogami 内部自签（Appendix A 6/6 ✅ · P37）|
| `bleed-air-valve` | demonstrative | Frozen | 无 |
| `emergency_flare_deployment_system` | demonstrative | Frozen | 无 |
| `minimal_landing_gear_extension` | demonstrative | Frozen | 无 |
| `c919-etras` | certified | In use | 甲方 (TRCU) · Kogami 代明示 (Appendix A 3/3 ✅ · P38) |

### Provenance SHA Registry (P40 · SoT)

`docs/provenance/sha_registry.yaml` registers 2 uploads/* files:
- `uploads/20260409-thrust-reverser-control-logic.docx` · SHA `6e457fe3…276133a5` · 230,930 bytes
- `uploads/20260417-C919反推控制逻辑需求文档.pdf` · SHA `dbe3f76b…276133a5` · 1,013,541 bytes

Enforced by `scripts/verify_provenance_hashes.py` via `tests/test_provenance_sha_integrity.py` in default lane. Any drift → CI 立即红。

### Next after P40-CLOSURE

按 P1-P4 优先级队列（P0 全部 resolved 于今日 7 Phase 链）：
1. Executor non-FF merge P40 → main (Option M, SHAs preserved)
2. Push origin main
3. Notion flip P40 DECISION Pending → Approved
4. Kogami 明示下一方向（候选：P41 thrust-reverser workbench spec · P42 truth_level runtime API · P43 freeze/upgrade template · 其他 · R4 不自选）

### 2026-04-20 全天 Phase 链（8 Phase · 7 已 landed · 1 等 closure sign）

- P31 re-land · P32 provenance backfill · P34 C919 E-TRAS · P35α truth-level registry · P36β thrust-reverser docx 真实化 · P37 thrust-reverser 反向增补 · P38 c919 证迹闭环 · P40 CI SHA enforcement

**证迹补完第二轮全套 (α→β→γ→δ→ε) 完成** · 5 真值链路全部整齐 · 2 certified 链路 Appendix A 全 resolved · CI 层自动防 tamper。

### 上一阶段归档（P30 Closed 2026-04-19）

之前的 `Control Tower Truth Aligned — P30 Closed` 位置信息在本次更新前覆盖 P30；P31/P32/P34 在 2026-04-20 已 landed 到 origin/main。历史 Phase 状态靠 `.planning/ROADMAP.md` + `docs/provenance/adapter_truth_levels.md` + Notion 控制塔页追溯。

### Historical P19 Snapshot (Archived 2026-04-17)

P19.1 Executed: hardware YAML schema + loader for thrust-reverser parameters
- 4 files created: hardware_schema_v1.schema.json, thrust_reverser_hardware_v1.yaml, hardware_schema.py, test_hardware_schema.py
- 17 new tests (all passing)
- Regression: 578 passed (561 original + 17 new), 1 skipped
- controller.py unchanged, freeze-compliant

P19.2 Executed: Monte Carlo reliability simulation engine
- MonteCarloEngine reads P19.1 YAML, simulates N deployment trials with numpy.random
- Deterministic with fixed seed; outputs ReliabilityResult (success_rate, MTBF, failure modes)
- 10 new tests (all passing)
- Regression: 588 passed (578 + 10 new), 1 skipped
- Freeze-compliant: no LLM for probability, no truth engine changes

P19.3 Executed: Reverse diagnosis engine
- ReverseDiagnosisEngine enumerates parameter combos satisfying target outcome
- Supports logic1_active, logic3_active, thr_lock_active, deploy_confirmed, tls/pls_unlocked
- Bounded enumeration (max 1000, 20-step grid captures switch windows)
- 16 new tests (all passing)
- Regression: 604 passed (588 + 16 new), 1 skipped
- Freeze-compliant: pure logic enumeration, no LLM, no truth engine changes
- P19.4 Executed: AI causal chain canvas SVG connectors
- SVG dashed blue lines with arrowheads connect sequentially discussed nodes on Canvas
- getCausalChainLayer() creates persistent SVG overlay; drawCausalChainConnectors() draws connectors
- Connectors drawn on applyAiHighlights(), cleared on clearAiHighlights() (including system switch)
- Regression: 604 passed, 1 skipped (no regression)
- P19.5 Executed: diagnosis report serialization layer
- Added _parameter_snapshot_to_dict() helper + diagnose_and_report() method
- Returns ISO-8601 timestamped dict: outcome, total_combos_found, grid_resolution, results[]
- Existing diagnose() behavior unchanged; 604 tests pass
- P19.6 Executed: POST /api/diagnosis/run API endpoint
- Route validates outcome against VALID_OUTCOMES, returns diagnose_and_report() JSON
- Hardware YAML path resolved dynamically from package root; 604 tests pass
- P19.7 Executed: POST /api/monte-carlo/run API endpoint
- Added _reliability_result_to_dict() to monte_carlo_engine.py; route accepts n_trials (1-10000 cap) + optional seed
- Both diagnosis and Monte Carlo engines now accessible via REST API; 604 tests pass
- P19.8 Executed: GET /api/hardware/schema discovery endpoint
- Added _hardware_to_dict() serializer to hardware_schema.py (recursive dataclasses.asdict); returns full YAML as JSON
- P19 API suite complete: diagnosis + Monte Carlo endpoints + schema discovery; 604 tests pass
- P19.9 Executed: API endpoint tests for P19.6/P19.7/P19.8
- 15 new tests covering all 3 endpoints (diagnosis/monte-carlo/hardware-schema); 619 total passed
- P19.10 Executed: Analysis Tools Panel — Frontend Integration
- Added "📊 分析工具" button to chat-drawer-toolbar; inline diagnosis + Monte Carlo panels after shortcut-strip
- Added openDiagnosisPanel(), openMonteCarloPanel(), runDiagnosis(), runMonteCarlo() to chat.js
- Added .analysis-panel, .analysis-run-btn, .analysis-result CSS to chat.css
- All 619 tests continue to pass (no regression)
- P19.11 Executed: Hardware Schema Browser Panel
- Added "🛠️ 硬件规格" button to chat-drawer-toolbar; inline #hardware-schema-panel with "加载规格" fetch button
- Added openHardwareSchemaPanel() + runHardwareSchema() to chat.js; fetches /api/hardware/schema and renders sensor ranges/logic thresholds/physical limits/timing
- All 619 tests continue to pass (no regression)
- P19.12 Executed: Analysis Results → Chat History
- runDiagnosis() + runMonteCarlo() now post styled results to chat-messages area via postAnalysisToChat()
- Results appear as AI messages with .chat-message-analysis styling (purple/green per type)
- All 619 tests continue to pass (no regression)
- P19.13 Executed: Sensitivity Sweep Panel
- Added "🔍 敏感性分析" button + #sensitivity-panel with 20-call sweep (5 RA × 4 outcomes)
- Added openSensitivityPanel() + runSensitivitySweep() + renderSensitivityTableText() to chat.js
- Results posted to chat history as amber-styled AI message
- All 619 tests continue to pass (no regression)
- P19.14 Executed: Multi-System Analysis Selector
- Added analysis-system-select dropdown to each of 4 panel headers (thrust-reverser/landing-gear/bleed-air)
- Added getSelectedAnalysisSystem() helper + pass system_id in all API calls
- All 619 tests continue to pass (no regression)
- P19.15 Executed: Multi-System Hardware YAML Support
- Created landing_gear_hardware_v1.yaml and bleed_air_hardware_v1.yaml
- Added _SYSTEM_YAML_MAP + _hardware_yaml_path(system_id) to demo_server.py
- Updated DIAGNOSIS_RUN_PATH and MONTE_CARLO_RUN_PATH handlers to read system_id from payload
- Updated do_GET HARDWARE_SCHEMA_PATH to parse system_id from query string
- Updated _handle_hardware_schema() to return system_id in response
- All 619 tests continue to pass (no regression)
- P19.16 Executed: Analysis API Robustness + UI Error Handling
- _hardware_yaml_path() raises FileNotFoundError on unknown system_id (no silent 500)
- DIAGNOSIS_RUN_PATH, MONTE_CARLO_RUN_PATH, _handle_hardware_schema catch FileNotFoundError → HTTP 400
- chat.js: showPanelError() + clearPanelError() helpers; all 4 run functions disable button during fetch
- .analysis-panel-error CSS (red tinted) + .analysis-run-btn:disabled styling added
- All 619 tests continue to pass (no regression)
- P19.17 Executed: Analysis API Multi-System + Error Coverage Tests
- Added tests/test_p19_api_multisystem.py: 15 tests covering system_id routing for all 3 endpoints
- _handle_hardware_schema: moved _hardware_yaml_path() inside try block so FileNotFoundError returns 400
- _SUPPORTED_FOR_ANALYSIS = frozenset({"thrust-reverser"}) guard added to diagnosis/Monte Carlo handlers
- Generic yaml.safe_load() loader for non-thrust-reverser in _handle_hardware_schema
- All 634 tests pass (619 baseline + 15 new, 0 regressions)
- P19.18 Executed: Presentation Deck + 3 哇场景 Scripts
- Created docs/presentations/pitch-ready-demo.md (Notion-ready presentation deck)
- Created docs/presentations/demo-talking-points.md (演示提示卡)
- 3哇瞬间: 因果链高亮 / Monte Carlo可靠性 / 反向诊断
- All 634 tests pass (no regression)
- All P0-P18.5 phases complete. Opus 4.6 final adjudication: Approved, Project Freeze.
- Regression baseline: 561 tests, 24-command suite. GSD automation continues to protect regression.
- P18.5 merged (canvas interaction fix): fault injection UI removed, hover scale disabled, hit-box pointer-events fixed.
- P18.6 PR open: SHA256 integrity checksums for workbench archives (561 tests, 24 validation commands pass).
- 解冻条件：外部用户反馈 / 新产品方向决策 / 新领域需求。

- Notion control tower is live at https://www.notion.so/AI-FANTUI-LogicMVP-33cc68942bed8136b5c9f9ba5b4b44ec.
- GitHub repo is live at https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp.
- P1 is closed as Approved in the Review Gate after GitHub-backed Opus adjudication.
- The two historical `Automation failure: P1-01 ...` gaps are now resolved as superseded by later successful runs.
- 09C now functions as a state-driven current Opus review brief, not a fixed prompt template.
- Local runs, GitHub Actions, and Notion writeback now share a single validation entrypoint via `tools/run_gsd_validation_suite.py`.
- 09C now explicitly distinguishes between “需要 Opus 审查” and “当前无需 Opus 审查”, and a normal refresh no longer overwrites an already approved gate decision.
- Review snapshots now prefer GitHub Action run / QA evidence over local Codex runs, so current Opus briefs stay anchored to the GitHub evidence plane.
- The shared validation suite now emits stable `python3 ...` command labels instead of machine-local Python executable paths.
- The GitHub workflow now runs Node24-compatible action versions and opts into `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`, matching GitHub's current deprecation path for JavaScript actions.
- The shared validation suite now also checks live Notion control-plane accessibility, validating the configured key pages and databases before a drift reaches Opus review time.
- Successful non-gated writebacks now refresh 09C automatically, so the current Opus brief keeps following the latest validated plan without a separate maintenance step.
- The old `P1 自动化目标审查 Gate` and `P1-02 消除手动浏览器 QA 依赖` records are now treated as configured legacy review artifacts and auto-archived once the approved default gate confirms no review is currently required.
- GitHub run `24168293031` proved the same retirement logic works from CI, and 09C now points at `P3-07 自动退场旧审查对象` with `当前无需 Opus 审查`.
- P4 is now closed as Approved after all six presenter-ready plans (`P4-01` through `P4-06`) verified successfully and GitHub run `24170575224` passed.
- P5 is now closed as Approved after the Opus 4.6 phase-closeout review accepted the GitHub-backed P5 evidence chain through `P5-10`.
- P6 is now closed as the active control-plane reconciliation phase; the repo-side baseline and Notion control tower are stable enough to make P7 the active workbench phase.
- P7 is now manually closed after `P7-70`, with the contract/schema convergence accepted as the completed phase outcome and the gate still at `Approved / 0 open gaps`.
- `P8-01 Implement Minimal Landing-Gear Controller Adapter` is now implemented locally, written back to Notion, and accepted by the default gate, so the first real non-reference truth adapter is part of the active evidence chain.
- `P8-02 Add Adapter-Backed Landing-Gear Playback Proof` is now implemented locally and written back to Notion: adapters can publish a spec payload straight into the playback contract, and discrete-state landing-gear playback now stays aligned with adapter truth at sampled checkpoints.
- `P8-03 Add Adapter-Backed Landing-Gear Diagnosis Proof` is now implemented locally: the landing-gear adapter now drives the fault-diagnosis contract directly, and the `hydraulic_pressure_bias_low` proof yields the expected baseline-vs-fault divergence plus blocked logic chain.
- `P8-04 Add Adapter-Backed Landing-Gear Knowledge Proof` is now implemented locally: the landing-gear adapter now drives the knowledge-artifact contract directly, and the resolved artifact preserves the full diagnosis chain plus evidence links.
- `P8-05 Connect Second-System Smoke To The Adapter-Backed Runtime Proof` is now implemented locally: the default `second-system-smoke` CLI/report now follows the landing-gear adapter-backed runtime chain, the schema validator still protects the legacy intake-packet smoke path, and the auto-synced control-plane rule text now matches the latest controller/runner/adapter/FlyByWire guide.
- `P8-06 Add A Two-System Adapter-Backed Runtime Comparison Report` is now implemented locally: the repo can compare the reference thrust-reverser adapter and landing-gear adapter through one machine-readable runtime proof artifact, and the reference workbench spec/playback parser now carry the extra steady-signal / comparison semantics needed to keep that report honest.
- P8 is now CLOSED as Approved via Opus 4.6 review (CFDJerry proxy, 2026-04-13): 6/6 plans pass, 23/23 shared validation, 0 open gaps. P6, P7, P8 all registered as Done in Roadmap DB.
- P9 is now the active phase: Automation Hardening & Evidence Pipeline Maturity. Opus recommended this direction because Roadmap DB had P7/P8 gaps (noted during review), confirming that control-plane automation still has debt. P9 aims to fully close the manual intervention loop.
- The current shared validation baseline is the 23-command suite.
- The Codex project guide is now synced into repo memory through `AGENTS.md` plus refreshed `.planning` summaries, so future sessions inherit the controller-truth, adapter-boundary, FlyByWire-reference, and staged-testing rules directly from the workspace.
- `P7-01`, `P7-02`, and `P7-03` are now landed on `main` as the spec foundation, mixed-doc intake layer, and first playback compiler for the future workbench.
- `P7-04` is now landed on `main`: declared fault modes can be injected into playback traces to produce deterministic diagnosis artifacts with affected signals, blocked logic nodes, and optimization hints.
- `P7-05` is now landed on `main`: diagnosis + repair outcomes can be captured as reusable knowledge artifacts with explicit optimization guidance.
- `P7-06` is now landed locally: intake packets can emit a dedicated clarification follow-up brief that tells engineers exactly which unanswered questions still block spec build and what unlocks after those answers arrive.
- `P5-01 GitHub 可验证 demo smoke suite` is now implemented locally: `tools/demo_path_smoke.py` covers bridge prompt, extreme clamp, mode-switch reset, and expected invalid-input behavior through the HTTP demo surface.
- The shared validation suite now includes 8 checks, with `demo_path_smoke` added as the new GitHub-verifiable presenter-demo confidence layer.
- `P5-02 最新交互胜出 demo 请求仲裁` is now implemented locally: the browser shell ignores stale prompt or lever responses once a newer interaction has started, so rapid edits no longer let an older response repaint the shared result surface.
- `P5-03 可见演示预设 smoke sweep` is now implemented locally: the smoke suite verifies `L3 等待 VDT90`, `RA blocker`, `N1K blocker`, and `VDT90 ready` through the same `POST /api/lever-snapshot` evidence plane used by the live demo.
- `P5-04 快速条件 toggle smoke sweep` is now implemented locally: the smoke suite verifies the visible blocker toggles for `engine_running`, `aircraft_on_ground`, `reverser_inhibited`, and `eec_enable` through the same HTTP evidence plane.
- `P5-05 L4 锁位与紧凑演示舱布局` is now implemented locally: deep reverse requests are capped at `-14°` until the `L4` gate is ready, the UI shows that lock state explicitly, and the demo smoke suite now covers the new lock gate.
- `P5-06 完成锁位语义与同屏观察布局` is now implemented locally: VDT controls sit at the top of the cockpit, the desktop logic board stays visible while the left column scrolls, and the interim lock-state presentation work is in place.
- `P5-07 明确条件深拉区语义并放松桌面舱面密度` is now implemented locally: the slider always shows `-32°..0°`, browser-side free dragging stays inside `-14°..0°` until the `L4` boundary unlock is ready, and the desktop lever/preset/condition areas now breathe more clearly without crowding the right-side logic board.
- `P5-08 修复 VDT live-control wiring 与条件深拉解锁回归` is now implemented locally: the moved VDT mode/percentage controls are again part of live snapshot scheduling, so dragging VDT updates the visible readout and can reopen the deep TRA drag band when the backend `L4` boundary unlock becomes ready.
- `P5-09 纠正 TRA 启动位与拖动方向语义` is now implemented locally: the cockpit no longer boots on a near-threshold preset, the TRA rail now explains that deeper reverse lives to the left, and the default interaction demonstrates the free `-14° .. 0°` band before any `L4` unlock.
- `P5-10 增加 RA-TRA-VDT 受控状态监控时间线` is now implemented locally: the demo exposes a dedicated full-width monitoring panel driven by a backend `GET /api/monitor-timeline` trace, with event markers and multi-row status curves for the user-defined RA / TRA / VDT process.
- `P5-11 压缩监控图并清理链路主板排版` is now implemented locally: the monitor timeline is compressed to 1/10 duration, rendered as a single selectable chart under the logic board, and the explanation rails are collapsed by default to keep the presenter surface readable.
- `P6-01 同步控制塔真值与 freeze packet 基线` now owns the active reconciliation pass: update stale status surfaces, publish a concise freeze/demo packet, and retire manual-browser-QA wording as an active approval rule.
- `P6-02 控制塔首页快照自动同步` is now implemented locally: the Notion dashboard page now gets a repo-managed live snapshot section at the top, so users no longer land first on the stale `P1 / 134 tests / Awaiting Opus` view.
- `P6-03 Freeze Demo Packet 自动快照同步` is now implemented locally: the freeze packet page gets the same kind of repo-managed top snapshot as the dashboard, so the stable evidence summary can keep following the live GitHub-backed baseline instead of drifting behind the latest verified plan, and successful CI runs no longer fail outright just because Notion writeback hits a temporary sharing 404.
- `P6-04 用可自动同步状态页旁路旧 archived status 页面` is now implemented locally: a new MCP-owned status page can be fully rewritten by repo-side sync, so dashboard / 09C / freeze packet links no longer have to point at the stale archived-ancestor status page.
- `P6-05 同步 repo 侧交接文档快照` is now implemented locally: `docs/coordination/plan.md`, `docs/coordination/dev_handoff.md`, `docs/coordination/qa_report.md`, and the repo freeze packet now expose managed current-baseline sections generated from the live control-plane snapshot while preserving older round notes below as history.
- `P6-06 将历史 repo 交接正文移出活跃文档` is now implemented locally: the active repo-side coordination docs and freeze packet keep only the managed current snapshot plus a short usage/archive stub, while the old Round-based long prose now lives in dedicated archive files so stale wording stops crowding live handoff surfaces.
- `P6-07 数据库写回失败时仍推进活动页快照` is now implemented locally: if a successful run cannot finish the shared database writeback, the sync loop now falls back to the active pages, promotes the current plan/run onto dashboard/status/09C/freeze surfaces, and keeps `prepare-opus-review` usable under the same partial-token 404 condition.
- `P6-08 清理活动页重复正文与臃肿运行摘要` is now implemented locally: repo-side handoff docs now show compact evidence summaries instead of raw validation JSON, the dashboard refresh path rewrites the current snapshot cleanly, and `prepare-opus-review` no longer aborts just because the status / 09C / freeze target pages drifted into archived block states under the local integration.
- `P6-09 让 repo 入口感知 archived Notion 活跃页` is now implemented locally: repo-side coordination/freeze docs stop advertising dead Notion subpage links when the local integration sees those pages as archived, and instead explicitly route users through the dashboard plus GitHub evidence plane.
- `P6-10 显式化 dashboard-only degraded mode` is now implemented locally: the Notion health validator and dashboard snapshot treat archived `status / 09C / freeze` pages plus the database surface as an explicit dashboard-only degraded mode instead of reporting a false full-health pass.
- `P6-11 让 repo docs 跟随更新鲜的 dashboard 快照` is now implemented locally: repo-side handoff/freeze docs prefer the fresher dashboard page snapshot when local database queries lag behind the live GitHub-backed dashboard state, so repo docs can keep up with the current P6 baseline.
- `P6-12 去重 dashboard 活动面入口` is now implemented locally: dashboard sync prunes stale `status / 09C / freeze` child-page blocks and treats preserved child pages/databases as non-authoritative for body equality, so the homepage can return to a single active control-plane entry.
- `P6-13 让 default_plan 跟随当前 active phase` is now implemented locally: sync entrypoints derive the default plan from the active roadmap phase plus the newest local plan file, persist it back into `notion_control_plane.json`, and render dashboard snapshots against that live P6 slice instead of the stale `P7-05` fallback.
- `P6-14 给 run 写回增加超时兜底` is now implemented locally: successful `run` commands cap full Notion writeback behind a deadline, then fall back to active-page snapshot + repo-doc sync if the shared database or page write stalls, so the control plane can keep moving forward under slow Notion windows instead of hanging mid-run.
- `P6-15 保留更强的共享验证基线` is now implemented locally: focused control-plane maintenance runs can advance the latest verified plan and latest success run, while repo/notion snapshots keep carrying forward the last richer shared validation baseline instead of collapsing QA confidence down to a narrow `1/1 shared validation checks pass`.
- `P6-16 给 prepare-opus-review 增加有界超时` is now implemented locally: Notion HTTP requests and prepare-opus-review refreshes now have bounded timeouts plus repo-doc fallback, so slow windows no longer require an external kill just to regain control of the automation loop.
- `P6-17 从归档提升更强 QA 基线` is now implemented locally: repo-side snapshot recovery now mines freeze/QA archives for the strongest shared validation baseline and prefers it over weaker maintenance-only summaries when rendering homepage, freeze packet, and handoff text.
- `P6-18 同步活跃页面链接目标漂移` is now implemented locally: active sync pages compare rich-text link targets in addition to visible labels, the fallback active-page defaults now point at the current status / 09C / freeze pages, and the repo-side Notion bootstrap guide now clearly marks old `Round 92` / `129 tests OK` examples as historical setup notes instead of current truth.
- `P6-19 中和 Notion 引导文档中的历史初始化样例` is now implemented locally: the remaining concrete `Round 92` / `129 tests OK` / old validation-title examples inside the bootstrap guide are replaced with neutral templates and “fill with current truth” language, so the document no longer reads like an active status source even deep in the body.
- `P6-20 稳定活跃同步页面 URL` is now implemented locally: writable active sync pages are refreshed in place instead of being replaced on every snapshot change, while missing or archived pages still fall back to creating fresh replacements under the dashboard.
- `P6-21 显式化数据库降级证据模式` is now implemented locally: `ReviewSnapshot` now carries an explicit evidence mode / note, and dashboard / status / freeze / 09C / repo docs all spell out when shared Notion databases are unavailable and the current truth is being recovered from active pages or repo docs.
- A new requirement set now exists for strict engineer-facing acceptance playback, fault injection and diagnosis, knowledge capture, and future-system generalization; this is large enough to require a new phase instead of being folded into demo freeze work.
- `P7-01` has an initial local foundation: `src/well_harness/system_spec.py` now defines a reusable control-system workbench spec and captures the current thrust-reverser chain as the first reference system, including acceptance-scenario, fault-mode, and clarification-question scaffolding.
- `P7-02` is already implemented on `main`: `src/well_harness/document_intake.py` defines a mixed-document intake packet, readiness assessment, and CLI export surface so future systems can arrive as PDF/markdown-heavy packets with explicit system-defined signal semantics.
- `P7-03` through `P7-06` now form a contiguous repo-side workbench chain: ready packets can progress from intake -> playback -> fault diagnosis -> knowledge capture, while incomplete packets can now stop at a structured clarification brief instead of drifting into guesswork.
- `P7-06` extends that onboarding path so incomplete packets no longer fail silently; the CLI can now export an explicit engineer follow-up brief from the same intake evidence packet.
- `P7-07` now bundles that chain into a single engineer-facing artifact, so a ready packet no longer requires separate CLI hops to reconstruct onboarding, playback, diagnosis, and knowledge state.
- `P7-08` now archives that bundle into a timestamped package with `bundle.json`, `README.md`, and component JSON artifacts, so engineers can hand off or revisit a full workbench run without reconstructing it from terminal output.
- `P7-09` is now implemented locally: `well_harness.demo_server` serves `/workbench.html`, `/api/workbench/bootstrap`, and `/api/workbench/bundle`, letting users load a reference or template intake packet, generate ready-or-blocked workbench bundles, and optionally emit archive packages from a browser acceptance surface.
- `P7-10` is now implemented locally: the browser workbench exposes the knowledge-capture optimization fields and renders playback, diagnosis, knowledge, and optimization summaries as structured cards, so engineers can validate the full bundle workflow without reading raw JSON.
- `P7-11` is now implemented locally: the browser workbench now leads with a visual acceptance board, collapses raw JSON into explicit dev-only drawers, surfaces packet source / stage state / pass-or-block verdicts in one glance, and safely de-duplicates same-second archive directory collisions instead of crashing repeated archive runs.
- `P7-12` is now implemented locally: the browser workbench exposes one-click acceptance presets for ready, blocked, quick-preview, and archive-retry flows, and the frontend now treats the last clicked preset as the winning result so rapid multi-clicks do not repaint stale output.
- `P7-13` is now implemented locally: the browser workbench keeps a recent acceptance history board for pass / block / archive / failure outcomes, so users can compare consecutive preset runs without losing the previous visible result context.
- `P7-14` is now implemented locally: recent acceptance history cards can restore their earlier result back into the main visual board, so users can revisit pass, block, and failure snapshots without rerunning the workflow.
- `P7-15` is now implemented locally: the browser workbench now shows whether the main board is displaying the latest result or a replayed historical result, and users can jump back to the latest run with one click.
- `P7-16` is now implemented locally: when users replay a historical result, the browser workbench now shows a direct latest-vs-replay comparison strip for verdict, scenario, fault mode, and archive state.
- `P7-17` is now implemented locally: when users replay a historical result, the browser workbench now shows a side-by-side acceptance comparison board for replay vs latest verdict, blocker, scenario, fault mode, knowledge, and archive state.
- `P7-18` is now implemented locally: the browser workbench now includes a visual second-system onboarding readiness board that surfaces source-document coverage, component/logic/scenario/fault counts, clarification progress, unlocks, and current gaps for a new control-logic packet.
- `P7-19` is now implemented locally: the browser workbench now includes a visual second-system fingerprint board that shows document coverage, control objective, source-of-truth note, and concrete signal semantics before or after bundle generation.
- `P7-20` is now implemented locally: the browser workbench now includes a visual onboarding action board that turns clarification items, schema blockers, and unlocks into explicit next-step cards instead of leaving them buried in text lists.
- `P7-21` is now implemented locally: the browser workbench now includes a clarification refill workspace that turns pending follow-up items into editable answer cards, writes them back into `clarification_answers`, and can rerun the bundle flow from the same acceptance surface.
- `P7-22` is now implemented locally: intake assessment now emits structured schema repair suggestions, the demo server can apply safe backend-approved packet repairs, and the browser workbench can apply those safe schema fixes and rerun from the same page.
- `P7-23` is now implemented locally: the browser workbench now keeps a visible packet revision history for sample loads, local imports, safe schema repairs, clarification writes, and pre-run manual JSON edits, and it can restore an older packet revision back into the current input surface.
- `P7-24` is now implemented locally: when the browser workbench is showing a historical packet revision, it now compares that version against the latest packet revision across system id, document coverage, logic/component shape, scenario/fault coverage, and clarification answers.
- `P7-25` is now implemented locally: the browser workbench now shows packet draft save state, lets engineers manually save the current packet draft, and auto-saves valid unsaved drafts before sample switches, packet restores, local imports, or browser-side writebacks overwrite the editor payload.
- `P7-26` is now implemented locally: the browser workbench now persists the current packet workspace in browser storage, restores packet history and related inputs after refresh, and keeps invalid JSON recoverable without promoting it into a valid saved revision.
- `P7-27` is now implemented locally: the browser workbench now persists recent acceptance result history and replay/latest view state across refresh, and restored browser histories continue with non-colliding IDs when new result or packet history entries are created.
- `P7-28` is now implemented locally: the browser workbench can now export and import full browser workspace snapshots, reusing the same restore path as browser persistence so packet context, result history, and replay/latest state move together across browsers.
- `P7-29` is now implemented locally: `tools/gsd_notion_sync.py` now publishes explicit development architecture and anti-drift execution rules into the auto-synced dashboard/status/repo handoff surfaces, including the requirement that a slice is only complete after live `run` writeback and `prepare-opus-review` re-check succeed.
- `P7-30` is now implemented locally: the browser workbench now renders a workspace handoff summary board, persists a handoff note with the rest of the workspace, and exports that handoff snapshot metadata together with packet/result history so cross-browser handoff is no longer raw JSON only.
- `P7-31` is now implemented locally: the browser workbench can now copy a text handoff brief built from the live handoff board, including packet coverage, current result, archive state, workspace scale, and the current handoff note.
- `P7-32` is now implemented locally: browser requests now send `workspace_handoff` metadata with bundle runs, archive packages can persist that context as `workspace_handoff.json`, archive README files include a browser handoff section, and the UI now surfaces that extra handoff artifact in the archive file list.
- `P7-33` is now implemented locally: browser requests can now send the full `workspace_snapshot`, archive packages can persist it as `workspace_snapshot.json`, and the archive file list now exposes that recoverable browser-state artifact beside the handoff summary.
- `P7-34` is now implemented locally: archive packages now include `archive_manifest.json`, README files point at that manifest as the single machine-readable file map, and the browser/API surfaces expose the manifest path alongside the other archive artifacts.
- `P7-35` is now implemented locally: backend helpers can validate and load `archive_manifest.json`, so later restore, sync, and audit tooling can reject malformed or incomplete workbench archives before trusting their file maps.
- `P7-36` is now implemented locally: the CLI can validate `archive_manifest.json` files in text or JSON mode, returning stable success/failure exit codes for generated archives and missing required files.
- `P7-37` is now implemented locally: the archive manifest CLI accepts an archive directory directly and includes restore targets in text output, making human handoff less dependent on raw JSON inspection.
- `P7-38` is now implemented locally: generated archive README files now include a directory-relative manifest self-check command, so archive consumers can validate the package without discovering the CLI from repo history.
- `P7-39` is now implemented locally: archive manifests now include optional self-check metadata, validator coverage checks malformed self-check objects, and CLI JSON/text output surfaces the same validation command.
- `P7-40` is now implemented locally: regression coverage executes the advertised README self-check command from inside a generated archive directory and verifies the CLI reports `archive_manifest: OK`.
- `P7-41` is now implemented locally: `docs/json_schema/workbench_archive_manifest_v1.schema.json` documents the manifest contract and optional jsonschema coverage validates generated archive manifests against it.
- `P7-42` is now implemented locally: generated `archive_manifest.json` files carry a `$schema` reference, the validator flags wrong schema IDs when present, and CLI output exposes the schema reference.
- `P7-43` is now implemented locally: generated archive README files show the same archive manifest schema reference as the manifest `$schema`, keeping human handoff aligned with the machine-readable contract.
- `P7-44` is now implemented locally: `archive-manifest --format json` includes the manifest `files` map, so automation can consume archive artifact paths directly from validated CLI output.
- `P7-45` is now implemented locally: new archive manifests store `archive_dir` and file references as archive-relative paths, and the loader/validator now resolve those paths from the manifest location so moved archives still validate.
- `P7-46` is now implemented locally: archive helpers can resolve the manifest file map into absolute artifact paths, load archived workspace handoff/snapshot JSON directly from the manifest, and expose the resolved file map through CLI JSON for restore automation.
- `P7-47` is now implemented locally: `well_harness.demo_server` exposes `/api/workbench/archive-restore`, returning archived bundle metadata plus restored workspace handoff/snapshot payloads from a moved `archive_manifest.json`.
- `P7-48` is now implemented locally: the browser workbench now lets users paste an `archive_manifest.json` path or archive directory, call the restore API, and reopen archive-backed packet/result context without leaving the acceptance surface.
- `P7-49` is now implemented locally: workbench bootstrap now lists recent archive packages from the default archive root, and the browser workbench renders one-click restore cards so archive recovery no longer starts with a manual filesystem path hunt.
- `P7-50` is now implemented locally: the demo server now exposes a dedicated recent-archives refresh API, and the browser workbench can refresh the recent archive board in place instead of reloading the entire page to see new archive packages.
- `P7-51` is now implemented locally: `system_spec` now emits a formal `$schema` / `kind` / `version` contract plus JSON-safe arrays, `docs/json_schema/control_system_spec_v1.schema.json` documents the reusable control-system spec shape, and intake / CLI exports now prove generated specs match that schema-aware payload boundary.
- `P7-52` is now implemented locally: a new `controller_adapter` module wraps `DeployController` behind explicit truth metadata and an injectable adapter interface, `SimulationRunner` now accepts adapter injection, and the live demo/runtime paths now route through that boundary instead of importing `controller.py` directly.
- `P7-53` is now implemented locally: a new `fault_taxonomy` module publishes the supported fault-kind contract and schema payload, intake parsing now rejects unknown `fault_kind` values, diagnosis reuses the same taxonomy guard, and the control-system spec schema now constrains `fault_kind` to the published taxonomy.
- `P7-54` is now implemented locally: a new `second_system_smoke` module and CLI command turn the custom reverse-control packet into one reusable smoke-proof report, demonstrating that intake, clarification, playback, diagnosis, and knowledge all complete through a single second-system entrypoint.
- `P7-55` is now implemented locally: `tools/run_gsd_validation_suite.py` now runs the second-system smoke proof as a ninth shared validation check, the suite test expectations now include that new check, and the repo-wide shared suite proves the custom packet alongside the existing demo/schema/control-plane checks.
- `P7-56` is now implemented locally: deterministic playback reports now emit `$schema` / `kind` / `version`, `docs/json_schema/playback_trace_v1.schema.json` documents the reusable trace payload, and regression coverage proves the second-system playback output matches that contract.
- `P7-57` is now implemented locally: `tools/validate_playback_trace_schema.py` validates both fixture and repo reference playback payloads against the published trace schema, and `tools/run_gsd_validation_suite.py` now runs that check as the tenth shared validation command.
- `P7-58` is now implemented locally: fault diagnosis reports now emit `$schema` / `kind` / `version`, `docs/json_schema/fault_diagnosis_v1.schema.json` documents the reusable diagnosis payload, and regression coverage proves generated diagnosis artifacts validate against that formal contract.
- `P7-59` is now implemented locally: `tools/validate_fault_diagnosis_schema.py` validates both fixture and repo reference diagnosis payloads against the published diagnosis schema, and `tools/run_gsd_validation_suite.py` now runs that check as the eleventh shared validation command.
- `P7-60` is now implemented locally: knowledge artifacts now emit `$schema` / `kind` / `version`, `docs/json_schema/knowledge_artifact_v1.schema.json` documents the reusable artifact payload, and regression coverage proves generated knowledge artifacts validate against that formal contract.
- `P7-61` is now implemented locally: `tools/validate_knowledge_artifact_schema.py` validates both fixture and repo reference knowledge artifacts against the published artifact schema, and `tools/run_gsd_validation_suite.py` now runs that check as the twelfth shared validation command.
- `P7-62` is now implemented locally: workbench bundles now emit `$schema` / `kind` / `version`, `docs/json_schema/workbench_bundle_v1.schema.json` documents the combined bundle payload, and regression coverage proves ready and blocked bundles validate against that formal wrapper.
- `P7-63` is now implemented locally: `tools/validate_workbench_bundle_schema.py` validates ready fixture, ready reference, and blocked template workbench bundles against the published bundle schema, and `tools/run_gsd_validation_suite.py` now runs that check as the thirteenth shared validation command.
- `P7-64` is now implemented locally: `tools/validate_control_system_spec_schema.py` validates the CLI reference spec plus fixture/reference intake-generated specs against the published root spec schema, and `tools/run_gsd_validation_suite.py` now runs that check before downstream schema checks.
- `P7-65` is now implemented locally: `tools/validate_fault_taxonomy_schema.py` validates the published taxonomy payload and proves the root control-system spec schema's `faultKindValue.enum` stays aligned with `SUPPORTED_FAULT_KINDS`, and `tools/run_gsd_validation_suite.py` now runs that check before the root spec schema check.
- `P7-66` is now implemented locally: `ControllerTruthMetadata` now emits a schema-aware adapter metadata payload, `docs/json_schema/controller_truth_adapter_metadata_v1.schema.json` documents the adapter identity/source-of-truth boundary, and focused coverage proves the reference adapter metadata validates without changing `controller.py`.
- `P7-67` is now implemented locally: `tools/validate_controller_truth_adapter_metadata_schema.py` validates reference adapter metadata against its published schema, proves the reference spec source-of-truth remains aligned, and `tools/run_gsd_validation_suite.py` now runs that check as part of the shared validation suite.
- `P7-68` is now implemented locally: `tools/validate_workbench_archive_manifest_schema.py` generates ready and blocked workbench archives, validates their manifests through both the internal validator and the published manifest schema, and `tools/run_gsd_validation_suite.py` now runs that check after workbench-bundle schema validation.
- `P7-69` is now implemented locally: second-system smoke reports now emit `$schema` / `kind` / `version`, `docs/json_schema/second_system_smoke_v1.schema.json` documents the generalization proof payload, and regression coverage proves the CLI JSON matches that formal contract.
- `P7-70` is now implemented locally: `tools/validate_second_system_smoke_schema.py` validates the default second-system smoke CLI proof against the published smoke schema, and `tools/run_gsd_validation_suite.py` now runs that check immediately after the default smoke command.
- Notion sync is now healthy again: archived shared databases are automatically restored when possible, default writeback budgets now cover real Notion slow windows, and both `run` and `prepare-opus-review` succeed again under default settings.

## Active Objective

Advance the spec-driven control-analysis workbench from separate primitives into a reusable engineer-facing workflow, while keeping the stabilized demo / freeze / control-plane baseline intact:

- Treat P7 as the completed contract/schema layer and use P8 to prove runtime generalization rather than adding more shell-only polish.
- Prove adapter-only truth admission with a minimal non-thrust-reverser system, starting from a landing-gear extension controller adapter that leaves `controller.py` untouched.
- Keep the user-approved constitution boundary explicit: new system truth may arrive only through published adapter interfaces, and any bypass/hardcoded alternate truth path is out of bounds.
- Keep `controller.py` as the confirmed control truth and avoid introducing a second hidden rule engine.
- Keep the stable cockpit demo, freeze packet, and Notion control plane available as the reference baseline while P7 expands.
- Pivot the current P7 thread from workbench-shell polish toward the Opus-requested architecture-convergence work: formal spec schema, adapter-ready boundaries, and evidence that a second system can plug into the same contract later.
- Make the control-system spec itself an explicit machine-readable contract, so intake output, CLI export, playback input, and future adapter layers all share one schema-aware payload instead of a reference-system-shaped implicit structure.
- Make controller truth injectable without changing the reference logic itself, so future system-specific truth sources can plug into the same runner/demo/workbench edges instead of forking those paths around `DeployController`.
- Make fault semantics explicit too, so `fault_kind` values across intake/spec/diagnosis refer to one reusable taxonomy instead of silently diverging by file, fixture, or engineer memory.
- Prove a second system can traverse the same engineer-facing workflow end to end, so “generalization-ready” stops being just an architectural claim and becomes a repeatable smoke check.
- Keep that second-system proof in the shared regression loop too, so future work cannot silently break generalization while only the reference system continues to pass.
- Turn intake assessment, clarification gating, playback, fault diagnosis, and knowledge capture into a continuous workflow that engineers can run and hand off without manual stitching.
- Preserve the “ask before guessing” onboarding boundary so incomplete packets stop at explicit clarification work instead of drifting into inferred specs.
- Keep workbench artifacts machine-readable and ready for later repo / Notion sync, archive, and review.
- Use the new bundle-archive package as the default handoff shape instead of forcing engineers to preserve raw terminal output.
- Expose the workbench flow through a lightweight browser acceptance surface so ready and blocked packets can be validated without requiring terminal-only workflows.
- Keep the browser acceptance surface aligned with the full bundle contract, including diagnosis and optimization details, so UI validation does not lag behind the backend workbench schema.
- Keep acceptance flows visually scannable for non-technical validation, and treat raw JSON / code-shaped surfaces as optional debug affordances rather than the primary walkthrough.
- Prefer one-click acceptance presets over form-first workflows whenever a common pass/block/archive path can be safely precomposed from existing backend truth.
- Keep consecutive acceptance runs visible in the browser so users can compare “通过 / 阻塞 / 留档 / 失败” outcomes without mentally reconstructing what the previous click did.
- Let users reopen a previous visual acceptance result directly from the browser history strip, instead of forcing a rerun just to get the old state back onto the main board.
- Make replay mode explicit in the UI, so a restored historical result is never mistaken for the current latest run.
- When a historical result is replayed, show its key differences from the latest result directly in the browser instead of making users compare two cards by memory.
- When a historical result is replayed, keep the latest result visible beside it in a side-by-side acceptance board so users can compare replay vs latest without reconstructing context from memory.
- Make second-system onboarding readiness visible in the browser so users can quickly judge whether a new control-logic packet is complete enough to enter spec build, playback, and diagnosis.
- Make the second-system packet's identity visible in the browser before users read bundle detail, so they can confirm document sources, control intent, and signal semantics at a glance.
- Make the second-system packet's next steps visible in the browser, so blocked onboarding runs tell users exactly what to answer, what to repair, and what will unlock next.
- Let blocked onboarding runs be answerable inside the browser workbench itself, so engineers can write clarification answers back into the packet and immediately retry the same workflow.
- Let blocked onboarding runs apply safe backend-approved schema repairs inside the browser workbench too, so common structural gaps can be patched and rerun without falling back to raw JSON editing first.
- Make browser-side packet edits recoverable too, so engineers can restore an earlier intake packet version before rerunning the workflow instead of reconstructing old inputs by memory.
- Make restored packet versions easier to judge too, so engineers can see their high-level differences from the latest packet without manually diffing raw JSON.
- Make in-browser packet drafts safer to iterate too, so a later sample switch or browser-side writeback does not erase valid unsaved packet work before the engineer chooses to rerun.
- Keep the browser packet workspace alive across refresh too, so packet history and in-progress onboarding edits survive ordinary page reloads instead of forcing engineers to reconstruct their state.
- Keep the browser result context alive across refresh too, so replay/latest acceptance history survives together with the packet workspace instead of forcing engineers to rerun just to get visual context back.
- Make the browser workspace portable too, so engineers can hand off or migrate their packet/result context across browsers with an explicit snapshot file instead of depending on one machine's storage.
- Make portable workspace handoff self-describing too, so exported snapshots carry a concise current-state summary and a human-written handoff note instead of forcing the next engineer to infer context from raw JSON.
- Make browser-side handoff immediately shareable too, so engineers can copy the current handoff brief into chat/docs without retyping what the snapshot already knows.
- Make archive artifacts handoff-aware too, so once a bundle is archived the README and file set still preserve the browser-side packet/result/archive/note context that existed at archive time.
- Make archive artifacts fully recoverable too, so a saved archive can preserve the full browser workspace snapshot instead of only a summarized handoff slice.
- Make archive artifacts self-indexing too, so one manifest can tell later restore, sync, or audit tooling exactly which files exist and which ones matter for browser recovery.
- Make archive manifests verifiable too, so later restore, sync, or audit tooling can validate a saved file map before consuming it.
- Make archive manifest validation runnable from the CLI too, so engineers and automation can inspect archive health without writing custom Python.
- Make archive manifest CLI handoff smoother too, so engineers can validate a whole archive directory and see restore targets without opening raw JSON.
- Make archive README files self-checking too, so the archive package itself tells consumers how to validate the manifest before restore or audit.
- Make archive self-checks machine-readable too, so automation can discover the validation command from `archive_manifest.json` instead of parsing README prose.
- Make archive self-check documentation executable too, so the generated README command is proven from the archive directory.
- Make archive manifest contracts portable too, so generic JSON Schema tooling can validate archive manifests without importing Python helpers.
- Make archive manifests self-describing too, so schema-aware tooling can discover the manifest contract directly from `$schema`.
- Make archive README files schema-aware too, so human handoff sees the same manifest contract reference as automation.
- Make archive CLI output restore-ready too, so future automation can read the full file map from validated JSON output without reopening the manifest.
- Make archive manifests location-portable too, so archive validation and restore still work after the saved archive directory moves.
- Make moved archives immediately restorable too, so automation can resolve archive-relative file paths and recover the saved browser workspace metadata without rebuilding archive context by hand.
- Make archive restore available through the workbench API too, so later browser or automation flows can reopen a saved archive package through one stable server entrypoint instead of stitching loaders together client-side.
- Make archive restore usable from the browser workbench too, so engineers can reopen a saved archive package inside the same acceptance surface instead of dropping to manual API calls or Python helpers.
- Make recent archive recovery discoverable too, so engineers can reopen the last few archive packages directly from the workbench without first copying local paths out of the filesystem.
- Make recent archive recovery live-refreshable too, so new externally created archive packages appear in the workbench without forcing a whole-page reset that might disturb current packet/result context.
- Keep the Notion control plane's architecture and execution rules auto-synced too, so any fresh Codex session resumes from the latest anti-drift contract instead of stale local assumptions.
- Continue routing subjective review through Opus 4.6 only, with Notion + GitHub as the evidence boundary.

## Blockers/Concerns

- `NOTION_API_KEY` is visible locally.
- GitHub credentials live in `~/.zshrc`, so non-interactive shells may need explicit sourcing or env injection.
- Opus 4.6 review packets must never rely on local terminal file paths.
- Historical browser hand-check notes in archived coordination docs are not part of the active review contract.
- Shared Notion database access is healthy again after restoring archived databases, but slow Notion windows still exist; writeback paths now use a 60s default budget plus bounded fallback rather than assuming fast responses.
- `tools/gsd_notion_sync.py prepare-opus-review` and `run` are now stable under default settings, but long-tail Notion slowness remains an operational characteristic rather than something to ignore in future control-plane changes.
- The original `01 当前状态` page still exists and remains blocked by archived-ancestor constraints, but the active control-plane `status` pointer now targets a new auto-synced replacement page, so user-visible links no longer need to land on the stale page.
- Repo-side coordination doc sync still keeps fallback recovery paths, but the primary expectation is now live shared-database writeback rather than permanent degraded mode.

## Accumulated Context

### Roadmap Evolution

- Phase P4 added: Elevate Cockpit Demo To Presenter-Ready
- Phase P5 added: Demo Polish And Edge-Case Hardening
- Phase P6 added: Reconcile Control Tower And Freeze Demo Packet
- Phase P7 added: Build A Spec-Driven Control Analysis Workbench
- Phase P14 added: AI Document Analyzer — Import logic circuit docs → AI ambiguity detection → Deep confirmation loop → Claude Code prompt generation
- Phase P15 added: Pipeline Integration — P14 AI Document Analyzer output connects to P7/P8 spec-driven intake pipeline, enabling end-to-end document-to-diagnosis workflow

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260413-jxy | Fix demo UI layout bug: move result-grid to left column, eliminate sticky chain-panel overlap | 2026-04-13 | d6cadad | [260413-jxy-fix-demo-ui-layout-bug-result-grid-is-co](./quick/260413-jxy-fix-demo-ui-layout-bug-result-grid-is-co/) |
| 260413-nq0 | Fix 3 demo UI bugs: SVG viewBox height (320→480), add 9 input conditions to asserted_component_values, remove NotDep SVG node | 2026-04-13 | e3f317c,5b8e9f0,54c950f | [260413-nq0-fix-3-demo-ui-bugs-svg-clip-input-node-l](./quick/260413-nq0-fix-3-demo-ui-bugs-svg-clip-input-node-l/) |
| 260413-p9i | Add headless Playwright smoke test for system switcher: 9 scenarios (page load, 3 options, topology switching, monitor panel/checkboxes, no console errors); wired into validation suite | 2026-04-13 | e2acdd6 | [260413-p9i-add-headless-playwright-smoke-test-for-s](./quick/260413-p9i-add-headless-playwright-smoke-test-for-s/) |
| 260413-pjo | Fix 4 P12 onboarding/schema gaps: README now clearly states 3 templates + 1 reference, added Quick Checklist for component kinds/fault_kind, added GenericControllerTruthAdapter protocol reference; Gap 2 (_snapshot_str) already present in template | 2026-04-13 | 22d3267 | — |
| 260413-qkz | Perf optimization for Notion writeback: parallelize ensure_live_databases (N→1 rounds), ensure_live_active_pages (N GETs in parallel), and write_notion_outcome upserts (plan/run/qa in parallel) — cuts writeback latency up to 3x; uses stdlib concurrent.futures only | 2026-04-13 | 333fa24 | — |
| 260414-uis | 09D UI方向 Phase A+B+C+D 完成：Canvas Shell 重写（909320c）+ Interaction Wiring+thr_lock bug（89fb1ab,d798049）+ MiniMax LLM（d834152）+ Intent Router+多系统AI（16601fc）+ Polish中文UI+视觉打磨+响应式（f215494）；427 tests 无回归 | 2026-04-14 | 909320c,89fb1ab,d834152,d798049,16601fc,f215494 | — |
| 260415-fei | 冻结期安全加固（Project Freeze期间）：P1文件上传50MB→10MB + P2 Content-Type白名单(application/json/text/plain) + P3确认循环UI汉化(Skip→跳过) + P2 Notion sync degraded modes归档；427 tests 无回归 | 2026-04-15 | 19fea92 | — |
| 260415-p16 | P16 AI Canvas Sync — Opus 4.6 A+架构（真值引擎先行+AI标注后到）：truth engine驱动canvas(<100ms) + MiniMax解释+highlighted_nodes叠加层；430 tests无回归 | 2026-04-15 | 8be797d | — |
| 260415-strat | 联邦架构战略规划（Opus 4.6）：联邦模型裁定为正确方向，整合≠合并；三级整合门槛；cross_domain_links.json（含schema）；federation-model.md；当前代码无需改动 | 2026-04-15 | 9a9edd1 | — |
| 260415-hud  | 冻结期Aerospace Dark HUD UI升级（Opus 4.6批准）：6优先级CSS改造（CSS变量重塑+SVG精密仪表节点+连接线状态+终端风格抽屉+微交互+Truth Eval Bar HUD化）；9845c83，430 tests无回归 | 2026-04-15 | 9845c83 | — |
| 260416-hud-polish | HUD Polish Pass：::selection 颜色 + 全局 scrollbar 样式（thin+蓝thumb+暗track）+ html smooth-scroll + body overflow-x；430 tests无回归 | 2026-04-16 | 47f1f83 | — |
| 260416-ctrl | 冻结期控制面整理：P6-02 stale plan（控制塔首页快照自动同步）→ Done；同步 Notion roadmap P16→Done；更新 freeze demo packet 冻结期完成改进项表；c97d95d smoke test URL修复（/ → /demo.html）；430 tests无回归 | 2026-04-16 | c97d95d,0288d14 | — |
| 260416-gov | 治理整改 Notion 控制塔（2026-04-15 Opus 4.6 裁决）：项目重命名AI FANTUI Control Logic Workbench MVP；Milestone 9—Project Freeze；新建项目宪法v2；新建 Freeze Ruling裁决书；重写首页/状态页/09C；补写 P14/P15/P16/P14-01/P15-01 正文；替换旧宪法/09G旧入口 | 2026-04-16 | — | — |
