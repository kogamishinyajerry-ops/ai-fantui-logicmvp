# Well Harness

`well-harness` is a lightweight simulation harness for the thrust reverser deploy logic we have confirmed in the discussion.

The first cut focuses on deploy-only behavior:

- control logic 1 through 4
- throttle lever reverse pull-back and return
- SW1 / SW2 latched switch behavior
- a simplified plant model for TLS / PLS / VDT feedback
- a CLI that prints a timeline for debugging

## Architecture

- `src/well_harness/models.py`
  Shared dataclasses for pilot inputs, resolved inputs, plant state, outputs, traces, trace events, and logic explain data.
- `src/well_harness/controller.py`
  Pure deploy-logic evaluation for logic 1 through 4.
- `src/well_harness/switches.py`
  Interval-based SW1 / SW2 latch model driven by TRA.
- `src/well_harness/plant.py`
  Simplified deploy-side plant and sensor feedback model.
- `src/well_harness/scenarios.py`
  Built-in scenarios for nominal deploy and retract/reset checks.
- `src/well_harness/runner.py`
  Simulation loop that combines pilot command, switch model, controller, and plant.
- `src/well_harness/cli.py`
  CLI for running scenarios and printing readable timeline, events, or structured JSON traces.
- `src/well_harness/demo.py`
  Deterministic controlled-intent layer for demo-facing trigger, diagnosis, and dry-run proposal answers.
- `src/well_harness/demo_server.py`
  Standard-library local HTTP server and static UI shell for the demo reasoning layer.

## Commands

Run the built-in nominal deploy scenario:

```bash
PYTHONPATH=src python3 -m well_harness run nominal-deploy
```

Run the built-in retract/reset scenario:

```bash
PYTHONPATH=src python3 -m well_harness run retract-reset
```

Show the full state-transition event list for faster fault isolation:

```bash
PYTHONPATH=src python3 -m well_harness run nominal-deploy --view events --full
```

Show logic transition diagnoses with before / after explain deltas and window context:

```bash
PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --full
```

Filter the diagnosis view to one logic and emit machine-readable JSON:

```bash
PYTHONPATH=src python3 -m well_harness run nominal-deploy --view diagnose --logic logic3 --format json
```

Export the full structured trace as JSON:

```bash
PYTHONPATH=src python3 -m well_harness run nominal-deploy --format json
```

All JSON views include deterministic schema metadata:

```json
{
  "schema": {
    "name": "well_harness.debug",
    "schema_version": "1.0",
    "view": "timeline",
    "scenario_name": "nominal-deploy"
  }
}
```

Explain why one logic is true or false at a specific simulation tick:

```bash
PYTHONPATH=src python3 -m well_harness run nominal-deploy --view explain --logic logic3 --time 1.8
```

The explain view selects the nearest trace row to `--time` and prints each condition with current value, comparison, threshold / target value, and pass state.

Run the deterministic demo intent layer:

```bash
PYTHONPATH=src python3 -m well_harness demo "触发 SW1 会发生什么"
PYTHONPATH=src python3 -m well_harness demo "触发 logic3 会发生什么"
PYTHONPATH=src python3 -m well_harness demo "触发 VDT90 会发生什么"
PYTHONPATH=src python3 -m well_harness demo "触发 THR_LOCK 会发生什么"
PYTHONPATH=src python3 -m well_harness demo "为什么 SW1 还没触发"
PYTHONPATH=src python3 -m well_harness demo "为什么 SW2 还没触发"
PYTHONPATH=src python3 -m well_harness demo "为什么 TLS115 还没触发"
PYTHONPATH=src python3 -m well_harness demo "为什么 logic1 还没满足"
PYTHONPATH=src python3 -m well_harness demo "为什么 logic2 还没满足"
PYTHONPATH=src python3 -m well_harness demo "为什么 logic3 还没满足"
PYTHONPATH=src python3 -m well_harness demo "为什么 logic4 还没满足"
PYTHONPATH=src python3 -m well_harness demo "logic4 和 throttle lock 有什么关系"
PYTHONPATH=src python3 -m well_harness demo --format json "logic4 和 throttle lock 有什么关系"
PYTHONPATH=src python3 -m well_harness demo "为什么 TLS unlocked 还没触发"
PYTHONPATH=src python3 -m well_harness demo "为什么 540V 还没触发"
PYTHONPATH=src python3 -m well_harness demo "为什么 VDT90 还没触发"
PYTHONPATH=src python3 -m well_harness demo "为什么 THR_LOCK 还没释放"
PYTHONPATH=src python3 -m well_harness demo "为什么 throttle lock 没释放"
PYTHONPATH=src python3 -m well_harness demo "如果把 logic3 的 TRA 阈值从 -11.74 改成 -8，会发生什么"
```

The demo layer is a controlled reasoning surface, not a full natural-language AI system. It maps supported short prompts to deterministic `trigger_node`, `blocked_state`, `diagnose_problem`, `logic4_thr_lock_bridge`, or `propose_logic_change` answers using the built-in scenarios and simplified first-cut plant. The controlled trigger-node catalog covers the current chain nodes `SW1`, `logic1`, `TLS115`, `TLS unlocked`, `SW2`, `logic2`, `540V`, `logic3`, `EEC deploy`, `PLS power`, `PDU motor`, `VDT90`, `logic4`, and `THR_LOCK`; non-logic trigger answers include upstream dependency hints and a small `upstream_status` table that point back to existing `events`, `explain`, `diagnose`, and trace evidence, but they are not complete root-cause proofs. For `SW1` / `SW2`, the table reports observed TRA / switch-event trace evidence from the interval-triggered latch model, not a unique hardware contact point. Threshold-change prompts return a dry-run proposal report and do not modify `controller.py`.
The controlled demo layer also supports a narrow blocked-state / pre-trigger comparison for prompts such as `为什么 SW1 还没触发`, `为什么 SW2 还没触发`, `为什么 TLS115 还没触发`, `为什么 logic1 还没满足`, `为什么 logic2 还没满足`, `为什么 logic3 还没满足`, `为什么 logic4 还没满足`, `为什么 TLS unlocked 还没触发`, `为什么 540V 还没触发`, `为什么 VDT90 还没触发`, and `为什么 THR_LOCK 还没释放`. Those answers are based on the built-in `nominal-deploy` checkpoint just before the node's first observed trigger, so they are deterministic evidence comparisons rather than full anomaly simulations or physical root-cause proofs. For `SW1` / `SW2`, the comparison still uses interval-triggered latch-model trace evidence rather than a unique hardware contact-point claim; for logic gates, the blocker table comes directly from the checkpoint row's `DeployController.explain(...)` conditions rather than a second copied rule set; for `logic4`, this means the answer stays tied to the checkpoint row's `deploy_90_percent_vdt` gate instead of inventing a separate throttle-lock truth; for `TLS unlocked`, it still uses simplified timer / sensor evidence.
For `logic4` and `THR_LOCK`, the demo also has a small bridge summary such as `logic4 和 throttle lock 有什么关系`. It links the logic4 blocked-state checkpoint, the downstream `throttle_lock_release_cmd`, and the `5.0s` event window in one deterministic answer without replacing the separate blocked-state or diagnose views.
Use `well_harness demo --format json "..."` when automation needs the same `DemoAnswer` fields as arrays; default `demo "..."` output remains the human-readable text format.
Key demo answers are regression-protected by the lightweight fixture `tests/fixtures/demo_answer_asset_v1.json`; this is an executable test asset for stable prompt / intent / evidence fragments, not a formal JSON Schema.
The demo JSON output is separately regression-protected by `tests/fixtures/demo_json_output_asset_v1.json`; this is also a lightweight executable fixture contract, not a formal JSON Schema.
The demo JSON output structure is documented by `docs/json_schema/demo_answer_v1.schema.json`; that schema is the machine-readable field/type reference, while `tests/fixtures/demo_json_output_asset_v1.json` is the executable prompt/fragments regression contract.
If `jsonschema` is installed locally, run `PYTHONPATH=src python3 -m unittest tests.test_demo.DemoIntentLayerTests.test_optional_jsonschema_validates_demo_json_payloads_when_installed` to validate real demo JSON payloads against `docs/json_schema/demo_answer_v1.schema.json`; without that optional package, the test explicitly skips and normal commands do not depend on it.
For a non-unittest entrypoint to the same demo answer schema check, run `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py`; it reuses `tests/fixtures/demo_json_output_asset_v1.json` and real `well_harness demo --format json` payloads, and prints a clear `SKIP` with a successful exit if `jsonschema` is unavailable.
That validator defaults to human-readable text; for automation, run `PYTHONPATH=src python3 tools/validate_demo_answer_schema.py --format json` to emit top-level `status`, `schema_path`, `asset_path`, and per-prompt `results`.

Start the local UI demo shell:

```bash
PYTHONPATH=src python3 -m well_harness.demo_server
```

Open the printed local URL to use the first-screen demo UI. The UI posts prompts to `POST /api/demo`, reuses the same deterministic `DemoAnswer` payload as `well_harness demo --format json`, highlights the fixed control chain, and keeps a raw JSON debug panel visible. It is a local UI shell for the controlled demo layer, not a full natural-language AI product or complete physical simulation.
If you want the server to ask the standard-library browser launcher to open the URL after startup, run `PYTHONPATH=src python3 -m well_harness.demo_server --open`; this is only a launch convenience, not browser E2E automation.
The current browser surface is tuned for a Chinese live demo: the first screen presents a compact `反推逻辑演示舱`, an interactive reverse-lever cockpit, a game-like `逻辑主板`, Chinese result labels, and a folded `原始 JSON 调试` inspector while preserving the existing `POST /api/demo` and `DemoAnswer` payload.
The browser surface is arranged as a lever cockpit showcase: throttle lever, HUD, control chain, and current-result summary share the first-screen demo flow, while raw JSON is kept as a lower-priority debug inspector. The lever cockpit uses `POST /api/lever-snapshot` for a controlled pullback scrubber, supports a `manual_feedback_override` mode for `deploy_position_percent`, and keeps the original diagnosis Q&A in a frozen secondary drawer.
The lever cockpit also includes a compact 条件面板 for `radio_altitude_ft`, `engine_running`, `aircraft_on_ground`, `reverser_inhibited`, `eec_enable`, `n1k`, `max_n1k_deploy_limit`, `feedback_mode`, and `deploy_position_percent`; `SW1 / SW2` still come from the existing switch model, and deploy / VDT feedback remains a folded simplified-plant diagnostic override rather than a new control truth.
The UI includes a small loading / empty-prompt / API-error state and highlights logic / command subnodes such as `logic4`, `THR_LOCK`, `TLS115`, `540V`, `EEC`, `PLS`, and `PDU`; highlights show answer association, not a complete causal proof.
Example prompt buttons expose a selected state, the control chain uses a narrow-screen scroll rail, and the raw JSON debug payload lives in an expandable panel.
Example prompts are grouped by bridge / diagnose / trigger / proposal use, the prompt box supports `Cmd/Ctrl+Enter` without stealing normal Enter newlines, and the UI includes a compact help note about the controlled demo boundary.
The UI also includes a small highlight explanation that names the `matched_node` / `target_logic` fields and the highlighted chain nodes; this explanation is answer association only, not a causal proof.
The structured answer panel includes an `Answer sections` summary that counts the existing `DemoAnswer` arrays, marks empty sections, and lets each chip focus its matching answer section; arrow keys move between section chips without changing the demo JSON payload.

For a lightweight presenter checklist before a demo, run:

```bash
PYTHONPATH=src python3 tools/demo_ui_handcheck.py
```

This helper prints the local UI start command, core prompts with guided expected observations, UI checkpoints, and boundary reminders; it is only a presenter aid, not browser E2E automation and not part of the formal GSD approval flow.
For a shorter presenter script, run `PYTHONPATH=src python3 tools/demo_ui_handcheck.py --walkthrough`; it prints concise callouts for the bridge / diagnose / trigger / proposal flow and remains a presenter aid, not browser automation or a new control-truth source.
The one-page presenter talk track lives at `docs/demo_presenter_talk_track.md` and keeps the same presenter-only boundary.
The UI section headers include matching presenter callout labels (`[Input]`, `[Chain]`, `[Highlight]`, `[Structured answer]`, `[Raw JSON]`) so the talk track maps directly to visible page regions.
The UI also includes a screenshot-free presenter route strip (`[Input] -> [Chain] -> [Highlight] -> [Structured answer] -> [Raw JSON]`) as a visual guide for the talk track; it is not browser automation or a screenshot annotation tool.
The structured answer area also has a compact audience answer-field legend for explaining `intent`, `matched_node`, `evidence`, `risks`, and raw JSON as reading aids rather than a new schema or second answer payload.
The legend is grouped with `Answer sections` as a compact answer guide so field meanings and section counts stay together without changing the `DemoAnswer` payload.
On narrow screens, that compact answer guide stacks the legend and section chips with touch-friendly spacing while keeping the same payload and field semantics.
That talk track also includes a small presenter readiness run card; it is not browser automation or an automatic readiness detector.
Formal subjective review now happens through Notion AI Opus 4.6 using the Notion control tower plus the GitHub repo, not by citing local terminal file paths.
Older repo notes about browser hand-checks remain historical presenter/archive material, not the current approval contract.

Run the unit tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```

Optionally run offline JSON Schema validation for all four JSON views if `jsonschema` is installed locally:

```bash
PYTHONPATH=src python3 -m unittest tests.test_cli.CliDebugOutputTests.test_optional_jsonschema_validates_contract_payloads_when_installed
```

Or run the standalone validation script:

```bash
PYTHONPATH=src python3 tools/validate_debug_json_schema.py
```

Or emit the validation result as machine-readable JSON for automation:

```bash
PYTHONPATH=src python3 tools/validate_debug_json_schema.py --format json
```

Run the standalone validation-report schema check:

```bash
PYTHONPATH=src python3 tools/validate_validation_report_schema.py
```

Emit the validation-report schema check result as machine-readable JSON:

```bash
PYTHONPATH=src python3 tools/validate_validation_report_schema.py --format json
```

If `jsonschema` is not installed, the optional unittest is skipped and the standalone script prints a `SKIP` message plus an install hint; normal harness commands and the default unit-test flow do not require either entrypoint.
The standalone script is also covered by an automated smoke test so entrypoint / stdout regressions are caught without relying only on manual runs.
For test/debug only, `WELL_HARNESS_FORCE_JSONSCHEMA_MISSING=1` forces the standalone script down the same `SKIP` path without changing normal default behavior.
For test/debug only, `WELL_HARNESS_FORCE_SCHEMA_PATH=/path/to/schema.json` can point the standalone script at an alternate schema path, including a missing file to force a stable `FAIL` path.
For test/debug only, `WELL_HARNESS_FORCE_CONTRACT_PATH=/path/to/contract.json` can point the standalone script at a single alternate contract, including contracts that intentionally trigger CLI or schema-validation failure paths.
When the standalone validator hits a CLI failure, it emits a compact script-level summary with a small set of stable `detail:` tokens instead of forwarding raw argparse `usage:` noise.
Unknown CLI parser failures that are not mapped to one of the small stable tokens fall back to `detail: cli_error.unclassified`.
The default text mode is for humans; `--format json` emits a structured summary with top-level `status`, `schema_path`, and per-contract `results` entries for automation.
The standalone validator JSON contract is documented by `docs/json_schema/validation_report_v1.schema.json` and regression-protected by `tests/fixtures/validation_report_asset_v1.json`; the schema is the formal machine-readable structure reference, while the asset fixture is the executable regression contract used by tests.
The validation report contract covers `PASS`, `SKIP`, and the known `FAIL` kinds `cli_exit`, `schema_unavailable`, and `schema_validation`.
If `jsonschema` is installed locally, you can also run `PYTHONPATH=src python3 -m unittest tests.test_cli.CliDebugOutputTests.test_optional_jsonschema_validates_validation_report_payloads_when_installed` to validate real validation-report `PASS` / `SKIP` / `FAIL` payloads against `docs/json_schema/validation_report_v1.schema.json`.
For a non-unittest entrypoint to that same validation-report schema check, run `PYTHONPATH=src python3 tools/validate_validation_report_schema.py`. It reads `tests/fixtures/validation_report_asset_v1.json`, reuses `tools/validate_debug_json_schema.py --format json` to generate real report payloads, and validates them against `docs/json_schema/validation_report_v1.schema.json`; if `jsonschema` is unavailable it prints the same optional-dependency `SKIP` message and exits successfully. Its default text mode is for humans, while `--format json` emits top-level `status`, `schema_path`, `asset_path`, and per-scenario `results` for automation.
The independent validation-report schema checker's own JSON output is documented by `docs/json_schema/validation_schema_runner_report_v1.schema.json` and regression-protected by `tests/fixtures/validation_schema_runner_report_asset_v1.json`, which covers `PASS`, forced `SKIP`, and controlled `FAIL` output shapes without matching the debug payload contract glob. The schema is the machine-readable structure reference; the asset is the executable regression contract.
If `jsonschema` is installed locally, run `PYTHONPATH=src python3 -m unittest tests.test_cli.CliDebugOutputTests.test_optional_jsonschema_validates_validation_schema_runner_report_payloads_when_installed` to validate the independent checker's real `PASS` / `SKIP` / `FAIL` JSON payloads against `docs/json_schema/validation_schema_runner_report_v1.schema.json`; without that optional package, the test explicitly skips and normal commands do not depend on it.
For a non-unittest entrypoint to that same independent-checker schema validation, run `PYTHONPATH=src python3 tools/validate_validation_schema_runner_report_schema.py`. It reuses `tests/fixtures/validation_schema_runner_report_asset_v1.json` and real `tools/validate_validation_report_schema.py --format json` output; if `jsonschema` is unavailable, it prints an optional-dependency `SKIP` message and exits successfully.
That schema-checker entrypoint defaults to human-readable text; for automation, run `PYTHONPATH=src python3 tools/validate_validation_schema_runner_report_schema.py --format json` to emit top-level `status`, `schema_path`, `asset_path`, and per-scenario `results`.
The schema-checker entrypoint JSON output is documented by `docs/json_schema/validation_schema_checker_report_v1.schema.json` and regression-protected by the lightweight fixture `tests/fixtures/validation_schema_checker_report_asset_v1.json`, which covers default `PASS`, forced `SKIP`, and controlled `FAIL` output fields. The schema is the machine-readable structure reference; the asset is the executable fixture contract.
If `jsonschema` is installed locally, run `PYTHONPATH=src python3 -m unittest tests.test_cli.CliDebugOutputTests.test_optional_jsonschema_validates_validation_schema_checker_report_payloads_when_installed` to validate the schema-checker entrypoint's real `PASS` / `SKIP` / `FAIL` JSON payloads against `docs/json_schema/validation_schema_checker_report_v1.schema.json`; without that optional package, the test explicitly skips and normal commands do not depend on it.
For a non-unittest entrypoint to that same schema-checker report validation, run `PYTHONPATH=src python3 tools/validate_validation_schema_checker_report_schema.py`; it reuses `tests/fixtures/validation_schema_checker_report_asset_v1.json` and real `tools/validate_validation_schema_runner_report_schema.py --format json` output, and prints an optional-dependency `SKIP` message with a successful exit if `jsonschema` is unavailable.

## Modeling Notes

- The confirmed control truth lives in `controller.py`.
- The exact physical actuation point of SW1 / SW2 inside their allowed trigger windows is not hardcoded as a single hardware truth.
- The harness models them as interval-triggered latches:
  once TRA passes through the switch window during reverse pull-back, the switch stays on until TRA is returned above the window's near-zero boundary.
- The plant is intentionally simplified so we can start debugging control sequencing immediately. It can be replaced later with a more faithful actuator / lock model.
- In the current first-cut plant, deploy-position movement is simplified so it starts only after all PLS unlock indications are true. This is a plant feedback / motion simplification, not an added controller gate for `logic3`; the controller truth remains in `controller.py`.
- In the current first-cut plant, `reverser_not_deployed_eec` is simplified to `deploy_position_percent <= 0.0`. This is a placeholder sensor / feedback simplification, not a confirmed real EEC signal model.

## GSD / Notion Automation

This repo is wired for a GSD loop where GitHub / the local checkout is the code truth plane and Notion is the control plane.

Run the local automation bridge:

```bash
python3 tools/run_gsd_validation_suite.py --format json

python3 tools/gsd_notion_sync.py run \
  --title "Local GSD automation smoke" \
  --command "python3 tools/run_gsd_validation_suite.py --format json"
```

When `NOTION_API_KEY` is set, the bridge writes Execution Run, QA, Plan status, and failure UAT Gap records into the `AI FANTUI LogicMVP 控制塔`. Use `--opus-gate` only when the run should pause for a Notion AI Opus 4.6 intervention that references Notion pages and the GitHub repo only.

GitHub Actions uses the same bridge in `.github/workflows/gsd-automation.yml`; configure the repository secret `NOTION_API_KEY` before expecting CI-to-Notion writeback.

`tools/run_gsd_validation_suite.py` is now the single validation entrypoint for local runs and GitHub Actions. It executes the unit-test suite plus the schema validators in a stable order, stops on the first failure, and emits either text or machine-readable JSON.

The active automation plan is no longer hardcoded in the GitHub workflow. `tools/gsd_notion_sync.py run` reads the current default plan from `.planning/notion_control_plane.json`, so phase routing now changes in one place instead of drifting between YAML and Notion.

The workflow also stays on GitHub's current JavaScript action runtime path: it now uses `actions/checkout@v5`, `actions/setup-python@v6`, and opts into `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` so Node24 compatibility is exercised before the platform-wide default switch.

Current Opus brief refreshes now prefer GitHub Action runs and matching GitHub QA rows when selecting the latest evidence. That keeps future review packets anchored to the GitHub evidence plane even if newer local Codex runs also wrote diagnostic records into Notion.

GitHub-backed Execution Run rows now store the exact Actions run URL, and the shared validation suite emits stable `python3 ...` command labels instead of machine-local Python executable paths.

Historical browser hand-check docs in `docs/coordination/` remain as archival round records only. The active review sources are the Notion control tower, the GitHub repo, and GitHub Actions evidence.

To refresh the current Opus 4.6 intervention brief from live Notion state, run:

```bash
python3 tools/gsd_notion_sync.py prepare-opus-review --activate-gate
```

This does not generate a fixed template library. It reads the current phase, latest runs, QA, gate, and open gaps, then rewrites `09C 当前 Opus 4.6 审查简报` with the specific review intervention Opus should perform now.

If there is no open gap, no `Awaiting Opus 4.6` gate, and no pending Opus task, the refreshed 09C page now says so explicitly and tells you to keep developing automatically instead of triggering a redundant review. A normal refresh also preserves existing approved gate decision notes.

When a later successful run arrives for the same plan, the bridge now resolves open `Automation failure: <plan>` gaps automatically and marks duplicate sibling records accordingly. That keeps the control tower aligned with the latest passing evidence instead of leaving stale blockers open.

## Debugging Notes

- Text timeline output now includes the key state bits plus `deploy_90_percent_vdt`, TLS / PLS power timers, and deploy commands.
- `--view events` renders only the tracked state flips, which is the quickest way to answer "which tick changed what".
- `--view diagnose` links logic flips to the before / after `controller_explain` rows, showing failed conditions, changed condition pass states, and key command / sensor / plant debug changes in that same trace-row window.
- `--view diagnose` compares adjacent real trace rows, so a logic already active on the first row is not reported as a synthetic transition.
- `--view explain --logic logic3 --time 1.8` shows why a specific logic was active or blocked on that tick.
- `--full` prints the entire text timeline or event list instead of the default tail window.
- `--format json` emits a stable structured trace with nested `pilot`, `resolved_inputs`, `plant_sensors`, `plant_state`, `controller_outputs`, and `controller_explain` sections for every tick.

## JSON Contract

- All `--format json` payloads include a top-level `schema` object with `name`, `schema_version`, `view`, and `scenario_name`.
- JSON output is deterministic for the same scenario and code version; it does not include current timestamps, random IDs, or machine-local paths.
- `schema.schema_version` is the compatibility marker for external scripts. Bump it when supported top-level fields are renamed, removed, or semantically changed.
- A formal JSON Schema reference lives at `docs/json_schema/well_harness_debug_v1.schema.json`. It documents the shared `well_harness.debug` v1 envelope, the top-level `timeline`, `events`, `explain`, and `diagnose` payload shapes, and key nested trace / explain / diagnosis objects for external integration.
- The JSON Schema is a structural contract for stable JSON field names and basic JSON types. It is not a complete physical model, threshold-range proof, or replacement for the controller logic in `controller.py`.
- Lightweight automated contract assets live in `tests/fixtures/`:
  `timeline_contract_v1.json`, `events_contract_v1.json`, `explain_contract_v1.json`, and `diagnose_contract_v1.json`.
- The JSON Schema is the broad machine-readable structure guide; the fixture contracts are the executable regression assets that tests use against deterministic CLI output and representative nested fields.
- The `timeline` fixture intentionally stays small: it checks schema metadata, top-level `rows`, `row_count`, and representative row sections / fields instead of freezing the full trace.
- The `events`, `explain`, and `diagnose` fixtures cover schema metadata, stable top-level fields, and their view-specific nested fields. `diagnostics[].context_changes` is part of the supported `diagnose` contract.
- Supported `diagnostics[].context_changes` fields are:
  `controller_outputs`: `tls_115vac_cmd`, `etrac_540vdc_cmd`, `eec_deploy_cmd`, `pls_power_cmd`, `pdu_motor_cmd`, `throttle_lock_release_cmd`;
  `plant_sensors`: `tls_unlocked_ls`, `all_pls_unlocked_ls`, `deploy_90_percent_vdt`, `deploy_position_percent`;
  `plant_state`: `tls_powered_s`, `pls_powered_s`.
- The `context_changes` field set is the supported diagnose window-context contract. It does not mean every trace field is eligible for diagnose context output, and it does not mean every supported context field appears in every diagnosis; only changed values in the compared trace-row window are emitted.
- Optional offline JSON Schema validation is available through both `tests.test_cli.CliDebugOutputTests.test_optional_jsonschema_validates_contract_payloads_when_installed` and `tools/validate_debug_json_schema.py`. Both entrypoints validate the same `timeline`, `events`, `explain`, and `diagnose` fixture commands against `docs/json_schema/well_harness_debug_v1.schema.json`. The optional `jsonschema` package is only needed when you explicitly run these validation entrypoints.
- When changing `schema.schema_version`, update `docs/json_schema/well_harness_debug_v1.schema.json`, all affected `tests/fixtures/*_contract_v1.json` files, and the contract helper in `tests/test_cli.py` in the same change so schema drift is caught by CI.
- Supported top-level fields by view:
  `timeline`: `schema`, `scenario_name`, `row_count`, `rows`;
  `events`: `schema`, `scenario_name`, `event_count`, `events`;
  `explain`: `schema`, `scenario_name`, `time_s`, `logic`;
  `diagnose`: `schema`, `scenario_name`, `diagnostic_count`, `diagnostics`.
- For regression checks, consume `schema.view` to confirm the payload type and compare the view-specific contract fields.
