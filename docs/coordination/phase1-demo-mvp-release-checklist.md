# Phase 1 Demo MVP Release Checklist

## Single Entry

Run this gate before presenting or archiving the Phase 1 demo MVP:

```bash
make phase1-demo-mvp-gate
```

This is the local/CI single entry. It writes `phase1_demo_mvp_gate_summary.json`, runs the release checklist, verifies `phase1_demo_mvp_release_summary.json`, verifies the CI artifact directory shape, and preserves the same browser/HUD/output-card acceptance evidence.

The final gate summary validates against:

```text
docs/json_schema/phase1_demo_mvp_gate_summary_v0_1.schema.json
```

Independent gate-summary verifier:

```bash
PYTHONPATH=src:. python3 scripts/verify_phase1_demo_mvp_gate_summary.py --format json --summary "$PHASE1_DEMO_MVP_GATE_ARTIFACT_DIR/phase1_demo_mvp_gate_summary.json"
```

Downloaded artifact verifier:

```bash
make verify-phase1-demo-mvp-gate-artifact
```

The release checklist remains available as the lower-level release evidence runner:

```bash
make phase1-demo-mvp-release-checklist
```

The target is the single local entry point for the current release evidence bundle. It calls `scripts/run_phase1_demo_mvp_release_checklist.py`, which runs the browser-level demo gate, generates the review package, verifies the package, verifies the downloaded-artifact shape, checks that the external consumption runbook exists, and writes `phase1_demo_mvp_release_summary.json`.

The CI validation job runs the same gate and writes the uploaded artifact directory through:

```bash
PHASE1_DEMO_MVP_GATE_ARTIFACT_DIR=artifacts/phase1-demo-mvp-review-package make phase1-demo-mvp-gate
```

## Release Scope

This checklist covers the old `demo.html` cockpit reconstruction MVP at `/demo-reconstruction`.

Acceptance is limited to:

- browser-visible console reconstruction
- 20 nodes
- 23 wires
- preset interaction proof
- HUD/output-card linkage
- machine-readable review package
- CI artifact reader compatibility
- external consumption instructions

It does not change or approve `controller truth`, does not claim production readiness, and does not prove certification-level control-law correctness. The required boundary declaration remains `certification_claim: none`.

## Gate Sequence

`make phase1-demo-mvp-release-checklist` executes the release runner:

```text
PYTHONPATH=src:. python3 scripts/run_phase1_demo_mvp_release_checklist.py --format json --artifact-dir "$PHASE1_DEMO_MVP_RELEASE_ARTIFACT_DIR"
```

The runner executes these checks in order:

```text
1. demo-html-reconstruction-browser-acceptance
   Command: PYTHONPATH=src:. python3 scripts/verify_demo_html_reconstruction_browser_acceptance.py --format json --artifact-dir "$PHASE1_DEMO_MVP_RELEASE_ARTIFACT_DIR/standalone-browser-acceptance"
   Purpose: prove browser screenshots, node/wire pixels, presets, HUD, and output cards.

2. phase1-demo-mvp-review-package
   Command: PYTHONPATH=src:. python3 scripts/run_phase1_demo_mvp_review_package.py --format json --artifact-dir "$PHASE1_DEMO_MVP_RELEASE_ARTIFACT_DIR"
   Purpose: generate phase1_demo_mvp_review_package_v0_1.json and phase1_demo_mvp_review_report.md.

3. review package verifier
   Command: PYTHONPATH=src:. python3 scripts/verify_phase1_demo_mvp_review_package.py --format json --package "$PHASE1_DEMO_MVP_RELEASE_ARTIFACT_DIR/phase1_demo_mvp_review_package_v0_1.json"
   Purpose: validate schema, demo gate, browser acceptance, screenshots, Markdown, and boundary.

4. verify-phase1-demo-mvp-ci-artifact
   Command: PYTHONPATH=src:. python3 scripts/verify_phase1_demo_mvp_ci_artifact.py --format json --artifact-dir "$PHASE1_DEMO_MVP_RELEASE_ARTIFACT_DIR"
   Purpose: validate that an external system can read the review artifact directory after it is moved or downloaded.

5. documentation presence checks
   Required: docs/coordination/phase1-demo-mvp-artifact-consumption-runbook.md
   Required: docs/coordination/phase1-demo-mvp-release-checklist.md
```

## Passing Release Contract

The release gate is acceptable only when every command exits `0` and all emitted JSON payloads report pass.

The final release summary must include:

```json
{
  "kind": "ai-fantui-phase1-demo-mvp-release-summary",
  "release_status": "pass",
  "status": "pass",
  "mismatches": [],
  "deterministic_gates": {
    "package": "pass",
    "markdown_report": "pass",
    "child_json": "pass",
    "screenshots": "pass",
    "browser_acceptance": "pass",
    "boundary": "pass"
  }
}
```

The `release_status` field is the stable machine-readable release decision for external review systems.

The outer gate summary must include:

```json
{
  "kind": "ai-fantui-phase1-demo-mvp-gate-summary",
  "status": "pass",
  "mismatches": [],
  "deterministic_gates": {
    "release_checklist": "pass",
    "release_summary_verification": "pass",
    "ci_artifact": "pass",
    "browser_acceptance": "pass",
    "boundary": "pass"
  }
}
```

The summary must validate against:

```text
docs/json_schema/phase1_demo_mvp_release_summary_v0_1.schema.json
```

Independent verifier:

```bash
PYTHONPATH=src:. python3 scripts/verify_phase1_demo_mvp_release_summary.py --format json --summary "$PHASE1_DEMO_MVP_RELEASE_ARTIFACT_DIR/phase1_demo_mvp_release_summary.json"
```

## Artifact Bundle

The release target writes to:

```text
$PHASE1_DEMO_MVP_RELEASE_ARTIFACT_DIR
```

Default:

```text
/tmp/ai-fantui-phase1-demo-mvp-release-checklist
```

Expected files:

```text
phase1_demo_mvp_gate_summary.json
phase1_demo_mvp_release_summary.json
phase1_demo_mvp_review_package_v0_1.json
phase1_demo_mvp_review_report.md
demo_html_reconstruction_mvp_gate.json
demo_html_reconstruction_browser_acceptance.json
browser-acceptance/*.png
```

External systems should use `phase1-demo-mvp-artifact-consumption-runbook.md` for GitHub artifact download and verification details.

## Stop Conditions

Stop the release if any of these occur:

- browser acceptance does not return `status: pass`
- review package verifier returns nonzero
- CI artifact checker returns nonzero
- any required screenshot is missing or empty
- `mismatches` is non-empty
- boundary values drift from `certification_claim: none`
- any output implies controller truth promotion or 不证明认证级控制律正确性 is no longer stated

## Human Review Note

This checklist is release evidence for the Phase 1 demo MVP surface. It is not a sign-off for Safety Guardian findings, Evidence Agent findings, production control logic, or certification readiness. Those still require approved-task shell execution, deterministic gates, and separate review evidence.
