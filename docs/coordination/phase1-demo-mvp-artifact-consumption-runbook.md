# Phase 1 Demo MVP Artifact Consumption Runbook

## Purpose

This runbook is the stable external-reader contract for the `phase1-demo-mvp-review-package` CI artifact.

It lets an external review or regression system validate the demo.html reconstruction MVP package from a downloaded artifact directory. The check is machine-readable, exit-code based, and does not rely on in-memory payloads, `/tmp` paths, or the original CI checkout path. It also does not promote any controller truth: `controller truth` remains unchanged and `certification_claim: none`.

## Artifact To Download

Download the GitHub Actions artifact named:

```bash
gh run download <run-id> --name phase1-demo-mvp-review-package --dir /tmp/phase1-demo-mvp-review-package-download
```

Expected directory shape after download:

```text
/tmp/phase1-demo-mvp-review-package-download/
  phase1_demo_mvp_gate_summary.json
  phase1_demo_mvp_release_summary.json
  phase1_demo_mvp_review_package_v0_1.json
  phase1_demo_mvp_review_report.md
  demo_html_reconstruction_mvp_gate.json
  demo_html_reconstruction_browser_acceptance.json
  browser-acceptance/*.png
```

The checker is intentionally tolerant of package JSON paths that still reference the CI-local prefix such as `artifacts/phase1-demo-mvp-review-package/...`; it resolves files from the downloaded artifact directory first. This means it is safe to validate a moved artifact and 不依赖原始 CI 工作目录.

## Verification Command

Run from a repo checkout that contains the verifier scripts and schemas:

```bash
PYTHONPATH=src:. python3 scripts/verify_phase1_demo_mvp_gate_artifact.py --format json --artifact-dir /tmp/phase1-demo-mvp-review-package-download
```

Local Make wrapper for a downloaded or copied artifact directory:

```bash
PHASE1_DEMO_MVP_GATE_ARTIFACT_DIR=/tmp/phase1-demo-mvp-review-package-download make verify-phase1-demo-mvp-gate-artifact
```

The older direct directory-integrity checker remains available:

```bash
PYTHONPATH=src:. python3 scripts/verify_phase1_demo_mvp_ci_artifact.py --format json --artifact-dir /tmp/phase1-demo-mvp-review-package-download
```

Local Make wrapper:

```bash
make verify-phase1-demo-mvp-ci-artifact
```

For CI-uploaded artifacts, prefer the direct script command above with the downloaded artifact directory.

## Passing Output Contract

The preferred external machine entry is now `phase1_demo_mvp_gate_summary.json`. It should include:

```json
{
  "kind": "ai-fantui-phase1-demo-mvp-gate-summary",
  "status": "pass",
  "mismatches": []
}
```

The final downloaded-artifact verifier emits:

```json
{
  "kind": "ai-fantui-phase1-demo-mvp-gate-artifact-verification",
  "status": "pass",
  "mismatches": [],
  "deterministic_gates": {
    "gate_summary": "pass",
    "release_summary": "pass",
    "review_package": "pass",
    "screenshots": "pass",
    "boundary": "pass"
  }
}
```

The gate summary schema is:

```text
docs/json_schema/phase1_demo_mvp_gate_summary_v0_1.schema.json
```

Validate the gate summary directly with:

```bash
PYTHONPATH=src:. python3 scripts/verify_phase1_demo_mvp_gate_summary.py --format json --summary /tmp/phase1-demo-mvp-review-package-download/phase1_demo_mvp_gate_summary.json
```

The lower-level release decision remains available in `phase1_demo_mvp_release_summary.json`. It should include:

```json
{
  "kind": "ai-fantui-phase1-demo-mvp-release-summary",
  "release_status": "pass",
  "status": "pass",
  "mismatches": []
}
```

The CI artifact checker remains the direct directory integrity check.

The release summary schema is:

```text
docs/json_schema/phase1_demo_mvp_release_summary_v0_1.schema.json
```

Validate the release summary directly with:

```bash
PYTHONPATH=src:. python3 scripts/verify_phase1_demo_mvp_release_summary.py --format json --summary /tmp/phase1-demo-mvp-review-package-download/phase1_demo_mvp_release_summary.json
```

A passing verification exits with status code `0` and emits JSON with:

```json
{
  "kind": "ai-fantui-phase1-demo-mvp-ci-artifact-verification",
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

External systems should treat any nonzero exit code, `"status": "fail"`, or non-empty `"mismatches"` list as a regression.

## Required Package Semantics

The package gate checks the main `phase1_demo_mvp_review_package_v0_1.json` for:

- `kind = ai-fantui-phase1-demo-mvp-review-package`
- `package_id = phase1-demo-mvp-review-package-v0.1`
- `/demo-reconstruction` as the demo route
- demo surface contract: 20 nodes, 23 wires, 5 presets, 6 status outputs, 4 output cards
- all package-level deterministic gates set to pass

The Markdown gate checks `phase1_demo_mvp_review_report.md` for the demo title, route, and non-certification statement.

The child JSON gate checks:

- `demo_html_reconstruction_mvp_gate.json`
- `demo_html_reconstruction_browser_acceptance.json`

Both child payloads must parse as JSON and report `status: pass`.

The screenshot gate checks every screenshot listed in the package under `browser_acceptance.screenshots`. The actual files must exist and be non-empty under `browser-acceptance/*.png` or an equivalent path inside the downloaded artifact directory.

The browser acceptance gate checks that:

- first-screen operator guide is visible
- chain SVG pixel check passes with 20 nodes and 23 wires
- `max-reverse` produces `thr_lock = ON`
- `inhibit-block` does not produce `thr_lock = ON`

The boundary gate checks:

- `certification_claim: none`
- `dal_claim: none`
- `production_readiness_claim: none`
- `controller_truth_promotion: none`
- `controller_truth_modified = false`
- `ui_layout_modified = false`

## Failure Triage

Use `deterministic_gates` and `mismatches` to route failures:

```text
package = fail
  Main review package drifted: schema, route, demo surface counts, status, or deterministic gates.

markdown_report = fail
  Human-readable report is missing, empty, or lacks the required route/non-certification content.

child_json = fail
  Demo gate or browser acceptance child payload is missing, empty, invalid JSON, or not passing.

screenshots = fail
  One or more browser acceptance screenshots listed in the package is missing or empty.

browser_acceptance = fail
  Browser-level proof regressed: first screen, node/wire visibility, or preset/HUD/output linkage.

boundary = fail
  Demo-only boundary drifted. Stop review before claiming controller truth, certification status, or production readiness.
```

## Review Boundary

This artifact proves that the old `demo.html` cockpit has a browser-verifiable Phase 1 MVP reconstruction at `/demo-reconstruction`. It does not prove certification readiness, DAL compliance, or production control-law correctness.

External systems may archive this package as evidence for the Phase 1 demo MVP surface only. Any later controller truth, Safety Guardian, or Evidence Agent claim must use its own approved-task shell and deterministic gates.
