# Local Production Readiness Runbook

Live Linear issue: `JER-244`

Current maturity refresh: live Linear `JER-258`

## Scope

This runbook is for a clean local checkout of the Workbench release candidate.
It is not a cloud deployment plan, a certification package, or a full
production-ready claim.

The current supported release gate is local:

- boot the standard-library demo/workbench server;
- run the release-candidate smoke command;
- generate and validate the release evidence manifest;
- inspect the manifest's `workbench_maturity_snapshot` for pass,
  rerun-required, blocked, and not-claimed gates;
- rerun unit and opt-in e2e gates before handoff.

## Clean Checkout Setup

```bash
git clone https://github.com/kogamishinyajerry-ops/ai-fantui-logicmvp.git
cd ai-fantui-logicmvp
uv sync --locked --extra dev --extra e2e --extra typecheck
uv run --locked --extra dev --extra e2e python -m playwright install chromium
```

If Chromium is already installed in the local Playwright cache, the last command
should be a no-op or a quick confirmation. It is the only setup step here that
may need network access on a fresh machine.

## Start The Workbench

```bash
uv run --locked --extra dev python -m well_harness.demo_server --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000/workbench`
- `http://127.0.0.1:8000/index.html`

The foreground server stops with `Ctrl-C`. If it was started in the background,
find the listener first and kill only that process:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
kill <PID>
```

## Verify A Release Candidate

Run these from the repo root.

```bash
uv run --locked --extra dev python tools/workbench_release_candidate_smoke.py --format json
uv run --locked --extra dev python tools/workbench_release_manifest.py --format json
uv run --locked --extra dev python tools/workbench_release_manifest.py --validate --format json
uv run --locked --extra dev python tools/run_gsd_validation_suite.py --only unit_tests --format json
uv run --locked --extra dev --extra e2e python -m pytest tests/ -m e2e -q --tb=short
uv run --locked --extra typecheck python tools/run_mypy_gate.py --format json --report-only
```

Expected current interpretation:

- Release-candidate smoke: must pass.
- Release manifest validation: must pass.
- Workbench maturity snapshot: must keep local smoke and manifest validation as
  pass evidence, unit regression as rerun-required on the exact candidate SHA,
  full strict mypy as blocked, and deployment/cloud/certification as
  not-claimed.
- Unit validation-suite gate: must pass on the exact release candidate SHA.
- Full opt-in e2e: must pass before claiming current e2e green.
- Full strict mypy: currently expected to remain blocked until JER-171 is
  closed; do not turn this into a clean gate claim.

## Environment Variables

Required for local release smoke, e2e, unit gate, and manifest validation:

- none.

Optional runtime or control-plane variables:

- `MINIMAX_API_KEY`: optional AI suggestion/planner endpoints only. The release
  smoke and manifest gates do not use it.
- `WORKBENCH_PROPOSALS_DIR`: local proposal storage override.
- `WORKBENCH_DEV_QUEUE_DIR`: local development queue storage override.
- `WORKBENCH_SKILL_EXECUTIONS_DIR`: local skill-execution audit storage
  override.
- `WORKBENCH_AUTO_SPAWN_EXECUTOR`: opt-in executor spawning. Leave unset for
  release-candidate smoke gates.
- `WORKBENCH_SLO_WEBHOOK_URL`: optional outbound webhook. Not part of the local
  release gate.
- `LINEAR_API_KEY` / `NOTION_API_KEY`: control-plane scripts only. The browser
  workbench must not require or write through them.

The manifest records variable names only. It must never record secret values.

## Unsupported External Dependencies

- No browser-initiated Linear or Notion writes.
- No cloud deployment or hosted runtime claim.
- No remote LLM dependency for release smoke, e2e, unit tests, or manifest
  validation.
- No certification claim from sandbox workbench artifacts.

## Current Blockers

- JER-171 full strict mypy remains blocked. Latest recorded wrapper evidence:
  4548 errors in 305 files after live Linear `JER-257` / PR #250.
- Deployment packaging, service ownership, rollback, and hosted observability
  gates are not merged.
- Certification authority is not established for sandbox workbench evidence.
- The current smoke gate is local-only; it proves first operator flows, not
  production hosting.

## Manifest Artifact

Generate a machine-readable release evidence manifest with:

```bash
uv run --locked --extra dev python tools/workbench_release_manifest.py --format json
```

Validate it with:

```bash
uv run --locked --extra dev python tools/workbench_release_manifest.py --validate --format json
```

The manifest includes the current git SHA, verification commands,
`workbench_maturity_snapshot`, pass/rerun-required/blocked/not-claimed gate
evidence, unsupported external dependencies, and explicit not-claimed gates.
