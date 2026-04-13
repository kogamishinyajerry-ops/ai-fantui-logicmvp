# Roadmap

## Current Milestone

Keep AI FANTUI LogicMVP stable as a GSD-managed, Notion-synced control loop while expanding it from a deterministic cockpit demo into a spec-driven control-analysis workbench with strict acceptance, fault injection, and reusable onboarding patterns.

## Phase P0: Control Tower And GSD Control Plane

Status: Done

Goal: Create the independent Notion control tower and align it with the local GSD model.

Exit Criteria:

- Notion root page exists as `AI FANTUI LogicMVP 控制塔`.
- Roadmap, task, session, decision, QA, asset, risk, plan, execution run, review gate, and UAT gap objects exist.
- The control tower treats GitHub / repo as code truth and Notion as control plane.

## Phase P1: Automate Execution And Evidence Writeback

Status: Done

Goal: Connect the local/GitHub GSD execution loop to Notion so plan runs, QA outcomes, and UAT gaps write back automatically, while keeping GitHub and Notion as the only evidence surfaces used by Opus 4.6.

Exit Criteria:

- A local script can run validation commands and write Execution Run + QA + UAT Gap state to Notion.
- A GitHub Actions workflow reuses the same script.
- The GitHub repo and workflow runs are usable as review evidence from Notion.
- Missing Notion or GitHub credentials degrade safely without leaking secrets.
- Failures become UAT gaps; subjective review is routed through the Opus 4.6 review gate without citing local terminal files.
- P1 was approved in the Review Gate and the two historical same-plan failure gaps were resolved as superseded.

## Phase P2: Harden Opus 4.6 Review Packets

Status: Done

Goal: Standardize the Opus 4.6 review packet so subjective approval happens from Notion pages and the GitHub repo alone.

Exit Criteria:

- A state-driven current Opus 4.6 review brief exists in Notion and can be refreshed from live control-plane state.
- Review Gate instructions explicitly forbid local terminal file references.
- The boundary between automated validation and Opus 4.6 subjective review is explicit.
- The current brief successfully drove an Opus adjudication that approved P1 and resolved legacy gaps.

## Phase P3: Reduce Control-Plane Drift

Status: Done

Goal: Keep the automated loop stable as validation entrypoints, Notion evidence, and Opus review packets evolve.

Exit Criteria:

- Local runs, GitHub Actions, and Notion writeback all reuse a single validation entrypoint.
- Same-plan legacy automation gaps auto-resolve after later successful runs.
- The current Opus 4.6 review brief generator stays aligned with the live Notion control-tower structure and GitHub evidence URLs.
- Superseded legacy review artifacts retire automatically once the default gate is approved and 09C says no review is required.
- The GitHub Actions workflow stays aligned with GitHub-hosted runner runtime deprecations without reintroducing manual review dependence.

## Phase P4: Elevate Cockpit Demo To Presenter-Ready

Status: Done

Goal: Turn the current cockpit demo candidate into a presenter-ready local demo that stays deterministic, explainable, and honest about the simplified plant boundary.

Exit Criteria:

- The first-screen cockpit flow, presenter talk track, and structured answer panel stay aligned around the same live-demo route.
- Presenter-critical prompts and lever interactions are regression-protected without introducing browser-only approval steps or a second control-truth layer.
- Demo copy and UI make the distinction between controller truth and simplified plant feedback explicit wherever a live audience could misread it.
- `POST /api/demo`, `POST /api/lever-snapshot`, `well_harness demo`, and `well_harness demo_server` remain stable unless a later plan explicitly changes their contracts.

## Phase P5: Demo Polish And Edge-Case Hardening

Status: Done

Goal: Harden the presenter demo against edge-case interactions and replace residual browser-only confidence checks with GitHub-verifiable smoke coverage.

Exit Criteria:

- Rapid lever edits, fast condition toggles, and extreme-value inputs are regression-protected by automated tests.
- A demo-path smoke suite runs in GitHub Actions without requiring browser-only approval steps.
- Residual "manual browser QA" expectations are either automated, narrowed into explicit scripts, or retired as no longer needed.
- The controller-truth versus simplified-plant boundary remains explicit, and no second control-truth layer is introduced while polishing the demo.

## Phase P6: Reconcile Control Tower And Freeze Demo Packet

Status: Done

Goal: Turn the now-stable P5 demo evidence into a consistent freeze-ready control-tower story, so Notion status pages, repo docs, and final presenter handoff materials all match the latest GitHub-backed truth without adding new product surface.

Exit Criteria:

- `01 当前状态` and related control-tower summaries no longer point at stale `129 tests OK` / manual-browser-QA-only guidance once P5 is approved.
- A concise freeze/demo packet exists that summarizes the latest stable GitHub evidence, current smoke coverage, presenter boundary conditions, and the remaining human signoff step.
- Historical browser hand-check notes are either archived or explicitly reframed as presenter aids rather than active approval requirements.
- No new demo features, controller-truth changes, or API-contract changes are introduced while preparing the freeze packet and documentation closure.
- The control plane can explicitly acknowledge dashboard-only degraded mode when archived Notion subpages block direct writes, without pretending those subpages are still healthy.

## Phase P7: Build A Spec-Driven Control Analysis Workbench

Status: Done

Goal: Add a reusable control-system specification layer that can drive strict scenario playback, fault injection, diagnosis, and knowledge capture without being locked to the current thrust-reverser chain alone.

Exit Criteria:

- A canonical control-system spec can describe components, logic nodes, monitored signals, acceptance scenarios, fault injection targets, and required clarification questions for new systems.
- The current thrust-reverser logic is represented as the first reference system through that spec layer without replacing `controller.py` as code truth.
- The system has a documented path from engineer-supplied process docs to monitor-vs-time traces, even if document adapters are phased in incrementally.
- A fault-analysis workflow is defined that produces reproducible reasoning artifacts, records confirmed fixes, and emits post-repair optimization suggestions.
- The onboarding path for a new control system explicitly blocks on unanswered ambiguity, instead of silently guessing at missing details.

## Phase P8: Runtime Generalization Proof

Status: Done

Goal: Prove the generalized contract layer can host a second real control-system truth adapter without changing `controller.py` or bypassing the adapter boundary.

Exit Criteria:

- P7 is explicitly treated as the completed contract/schema layer, and the runtime proof work starts from that validated baseline.
- At least one non-thrust-reverser control-system adapter publishes valid metadata and a valid control-system spec through the adapter boundary alone.
- A minimal second system can produce deterministic truth evaluations from adapter inputs without introducing a hidden hardcoded rule path outside the adapter interface.
- The constitution/state surfaces explicitly allow new system truth only through adapters and forbid bypassing adapters with new hardcoded truth paths.
- Runtime validation proves the second-system adapter can be exercised safely while the reference thrust-reverser truth remains untouched.

## Phase P9: Automation Hardening & Evidence Pipeline Maturity

Status: Done

Goal: Close the remaining manual intervention gaps in the GSD automation loop so that a plan lands on main and the Notion control plane updates automatically — with no human-initiated Notion or GitHub operations required in the happy path.

Exit Criteria:

- GSD automation loop completes a full cycle (plan → validate → Notion update → CI) without manual intervention.
- Roadmap DB Phase lifecycle (register new phase, close completed phase) is automated into the GSD loop.
- CI/CD pipeline includes three distinct stages: regression → validation → Notion sync.
- Failed Notion sync stage does not fail the overall pipeline (writeback is non-blocking).
- Roadmap DB shows P6=Done, P7=Done, P8=Done, P9=Done (no manual edits needed).
- All resolvable manual touchpoints are eliminated; irreducible human-only steps are explicitly documented with degraded-mode handling.

## Phase P10: Second-System Runtime Pipeline End-to-End

Status: Active

Goal: Prove the generalized contract layer can host a second real control-system truth adapter through the complete intake → playback → diagnosis → knowledge pipeline, with both systems producing deterministic truth evaluations and a side-by-side comparison report.

Exit Criteria:

- Landing-gear adapter → intake → playback trace → diagnosis → knowledge artifact full chain runs end-to-end, each stage output passes its v1 schema validation.
- Side-by-side comparison report shows both thrust-reverser and landing-gear runtime outputs.
- All 23 shared validation commands continue to pass (no regression).
- `/glm-execute` compliance: every plan involving >50 LOC has a `[MODEL-CALL]` audit record.
- Roadmap DB shows P9=Done, P10=Active.
