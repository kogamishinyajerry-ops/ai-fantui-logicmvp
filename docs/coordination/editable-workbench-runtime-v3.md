# Editable Workbench Runtime v3

Editable Workbench Runtime v3 moves the completed UI interaction layer into
canonical sandbox runtime artifacts. The goal is not to make a candidate graph
certified; it is to make every workbench edit executable, validateable, diffable,
and archivable as controlled engineering evidence.

## Linear Project

`AI FANTUI LogicMVP · Editable Workbench Runtime v3`

## Issue Chain

- JER-165: Canonicalize workbench UI draft into `editable_control_model_v1` (Done, PR #148)
- JER-166: Sandbox graph validation report v1 (Done, PR #149)
- JER-167: Scenario selector and custom snapshot sandbox UI (Done, PR #150)
- JER-168: Port-aware edge inspector v1 (Done, PR #151)
- JER-169: Runtime v3 acceptance bundle and regression proof (Done, PR #152)
- JER-170: Workbench e2e networkidle gate normalization (Done, PR #153)
- JER-171: Official mypy strict gate definition (Done as evidence wrapper, not mypy-clean claim, PR #154)
- JER-172: Workbench acceptance bundle UI archive/export regression (Done, PR #155)
- JER-173: Hardware interface binding editor v1 (Done, PR #156)
- JER-174: Interface binding validation badges v1 (Done, PR #157)
- JER-175: Typed port editor v1 (Done, PR #158)
- JER-176: Port compatibility diagnostics v1 (Done, PR #159)
- JER-177: Port compatibility badges v1 (Done, PR #160)
- JER-178: Operation catalog palette v1 (Done, PR #161)
- JER-179: Sandbox rule parameter editor v1 (Done, PR #162)
- JER-180: Named draft snapshots v1 (Done, PR #163)
- JER-181: Duplicate and keyboard editing v1 (Done, PR #164)
- JER-182: Multi-select batch editing v1 (Done)
- JER-183: Lasso selection and group move v1 (Done)
- JER-184: Direct port-handle wiring v1 (Done)
- JER-185: Canvas pan zoom and fit selection v1 (Done)
- JER-186: Hardware interface palette v1 (Done)
- JER-187: Hardware binding diagnostics map v1 (Done)
- JER-188: Diagnostics focus and repair affordances v1 (Done)
- JER-189: Diagnostic repair actions v1 (Done)
- JER-190: ChangeRequest proof packet object v1 (Done)
- JER-191: End-to-end acceptance bundle v1 (Done)
- JER-192: Workbench acceptance journey regression (Done, PR #174)
- JER-193: Workbench lasso drag stabilization (Done, PR #175)
- JER-194: WOW-A early beat fixture rebaseline (Done)
- JER-195: Interface matrix export v1 (Done)
- JER-196: Interface matrix import/apply v1 (Done)
- JER-197: Interface matrix validation preview v1 (Done)
- JER-198: Interface matrix row diff preview v1 (Done)
- JER-199: Interface matrix selective apply v1 (Done)
- JER-200: Interface matrix review table v1 (Done)
- JER-201: Interface matrix selected-row apply v1 (Done)
- JER-202: Lasso group-drag flake hardening v1 (Done)
- JER-203: Interface matrix CSV bridge v1 (Done)

## Closure Summary

Runtime v3 is closed as the bridge from editable UI gestures to canonical,
executable, reviewable sandbox artifacts. Its completion evidence is the Linear
issue chain and `origin/main` history through JER-203.

The closure is intentionally evidence-scoped:

- JER-165 through JER-172 delivered canonical model conversion, graph
  validation, scenario/snapshot input, port-aware edge inspection, acceptance
  bundle evidence, e2e readiness normalization, honest mypy gate reporting, and
  archive/export gate fields.
- JER-173 through JER-185 delivered the first high-freedom editing layer:
  hardware/interface binding, typed ports, compatibility diagnostics, operation
  catalog, rule parameter editing, named snapshots, keyboard duplication,
  multi-select, lasso/group movement, direct port handles, and canvas viewport
  controls.
- JER-186 through JER-203 delivered hardware palette and diagnostics, repair
  affordances/actions, ChangeRequest proof packet, acceptance journey coverage,
  interface matrix export/import/validation/diff/review/selective apply, lasso
  hardening, and CSV/TSV bridge.

JER-171 remains a gate-honesty boundary: the official command exists and may
return `status: blocked`. Runtime v3 closure does not certify a clean mypy
baseline.

## Successor

Successor Linear project:
`AI FANTUI LogicMVP · Editable Workbench v4 Authoring + Hardware Design`

Successor issue bridge:

- JER-204: Roadmap and Linear narrative refresh after Runtime v3 closure
- JER-205 through JER-213: initial v4 backlog for authoring freedom, reusable
  subsystems, hardware/interface design model, connector/pin map editing,
  evidence inspector v2, scenario/debug linkage, diff review v2, and
  ChangeRequest handoff.

## Successor Bridge Note

JER-205 treats this Runtime v3 closure record as execution context only. The
JER-165 through JER-203 evidence chain proves that editable workbench candidates
can be modeled, validated, diffed, archived, and restored as sandbox evidence.
It is not a certification entry point and does not authorize candidate graphs,
hardware/interface records, bundle kinds, or archive manifests to become
certified truth.

## JER-165 Rule

JER-165 converts `/workbench` UI draft snapshots into canonical
`editable_control_model_v1` payloads before sandbox runtime/diff.

The conversion is sandbox-only:

- UI draft nodes become editable sandbox nodes with approved op catalog values.
- UI edges become evidence-only canonical model edges.
- Edges to existing logic nodes may create synthetic UI target ports so graph
  structure can be preserved without changing baseline rules.
- Invalid UI graph references return `invalid_model` evidence.
- `controller_truth_modified`, `truth_level_impact`, and `dal_pssa_impact`
  remain false/none.

## JER-166 Rule

JER-166 makes graph validation evidence structured enough for the API and UI to
consume directly.

The validation report remains sandbox-only:

- Every sandbox run response carries `validation_report`.
- Valid graphs return a pass report with zero issues.
- Invalid graphs return `invalid_model` plus categorized issues for
  `invalid_edge`, `dangling_port`, `duplicate_edge`, `unsafe_op`, and
  `missing_node`.
- `/workbench` renders the issue summary inside the sandbox diff panel.
- The report is evidence for a draft candidate only; it does not certify,
  approve, or mutate truth.

## JER-167 Rule

JER-167 lets engineers choose a supported sandbox scenario and optionally add a
custom initial-input snapshot before running the candidate.

The scenario/snapshot surface is truth-neutral:

- The default scenario remains `nominal_landing`.
- Supported alternatives are explicit UI/API choices.
- Custom snapshot JSON may only override supported timeline initial inputs.
- Invalid scenario or snapshot input returns sandbox validation evidence, not a
  truth decision.
- Evidence archives include the selected scenario metadata.

## JER-168 Rule

JER-168 makes draft edges inspectable as evidence-only port/signal bindings.

The edge inspector is non-authoritative:

- Selecting an edge shows source node, target node, source port, target port,
  signal id, and validation status.
- UI edge metadata is exported with draft JSON for review evidence.
- Missing endpoint metadata is rendered as `evidence_gap`.
- Edge inspection never changes control truth or hardware truth.

## JER-169 Rule

JER-169 closes Runtime v3 with a single acceptance bundle that can be archived
and reviewed without upgrading the candidate to certified truth.

The acceptance bundle must include:

- Canonical `editable_control_model_v1` JSON derived from the UI draft.
- Graph `validation_report` from the sandbox run.
- Sandbox run payload and baseline diff report.
- Draft-only ChangeRequest packet and Codex PR proof packet.
- Known gate blockers for opt-in e2e and mypy when they are not clean.
- Archive manifest checksums for every evidence file.

The bundle is evidence-only:

- It records `truth_level_impact: none` and `dal_pssa_impact: none`.
- It does not mutate Linear from the workbench.
- It does not edit controller truth, frozen adapters, C919 reference packets, or
  product LLM/chat behavior.

## JER-170 Rule

JER-170 normalizes the opt-in Playwright gate so `/workbench` readiness is
measured by required DOM and JS affordances, not global network quiet.

The gate remains strict:

- The shell smoke waits for `#workbench-identity` and
  `window.setWorkbenchIdentity`.
- The bundle smoke waits for `#workbench-packet-json` and a workbench preset.
- JS error capture and DOM assertions stay intact.
- Passing this gate does not change truth, DAL/PSSA, adapter, or product LLM
  behavior.

## JER-171 Rule

JER-171 defines a repo-owned mypy strict evidence command without pretending the
current baseline is clean.

The official evidence command is:

`PYTHONPATH=src:. python3 tools/run_mypy_gate.py --format json`

The command emits a machine-readable `well-harness-mypy-gate-report` with
`status: pass` or `status: blocked`. On the current baseline, `blocked` is the
expected honest result and points back to the JER-148/JER-171 typing blocker
record. PR proof packets may cite that JSON, but must not claim `mypy --strict
clean` until the wrapper reports `pass`.

## JER-172 Rule

JER-172 keeps the `/workbench` local evidence archive aligned with the Runtime
v3 proof packet rules.

The browser archive must include:

- `gate_claims` with `e2e_49_49: not_claimed` and
  `mypy_strict_clean: not_claimed`.
- `known_blockers` that cite the official JER-171 mypy evidence command.
- `red_line_metadata` proving no controller truth, frozen asset, live Linear,
  truth-level, DAL, or PSSA mutation.
- Checksums for both `gate_claims` and `known_blockers` so the local JSON export
  has integrity coverage for gate evidence.

## Boundaries

- Do not edit `src/well_harness/controller.py` truth semantics.
- Do not edit frozen adapters, frozen hardware YAML, or the C919 reference
  packet.
- Do not promote truth level or make DAL/PSSA claims.
- Do not restore product LLM/chat behavior.
- Do not let UI drafts, canonical sandbox models, validation reports, or archive
  manifests become certified truth.
