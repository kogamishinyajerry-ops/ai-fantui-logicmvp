# Multi-Agent Operator Cockpit

Date: 2026-05-27
Status: M22 read-only operator package

## Purpose

This package gives the multi-agent construction lane one local operator cockpit. It combines:

- Project Manager Status Summary;
- UltraWork Monitor;
- the five-agent active team cap;
- queue/cursor health;
- repo/GitHub/local-artifact boundary state;
- explicit dependency and pathspec boundaries.

It is a read-only package. It does not activate M21 streamed-authoring implementation, edit controller truth, alter external planning configuration, or add a live server route.

## Local Entry

```sh
make multi-agent-operator-cockpit
```

Default output:

```text
/tmp/ai-fantui-multi-agent-operator-cockpit/multi_agent_operator_cockpit_v0_1.html
```

Verifier:

```sh
make verify-multi-agent-operator-cockpit
```

## M22 Boundary

M22 is a cockpit packaging milestone, not a controller milestone.

Allowed:

- Generate JSON, Markdown, and static HTML cockpit artifacts.
- Reuse existing project-manager status and UltraWork dashboard artifacts.
- Keep the control boundary on repo, GitHub, and local artifacts.
- Keep M21 implementation explicitly owner-gated.

Not allowed:

- Edit `src/well_harness/controller.py`.
- Edit `src/well_harness/runner.py`.
- Edit `src/well_harness/demo_server.py`.
- Edit `src/well_harness/requirements_intake/**`.
- Edit `src/well_harness/static/**`.
- Edit `.planning/**`.
- Stage `artifacts/**`.
- Change external planning-control configuration.

## Pathspec Package

Stage this M22 package only with explicit pathspecs:

```sh
git add -- \
  Makefile \
  docs/coordination/multi-agent-control-logic-engineering-system-mvp.md \
  docs/coordination/multi-agent-operator-cockpit.md \
  docs/json_schema/multi_agent_operator_cockpit_v0_1.schema.json \
  scripts/run_multi_agent_operator_cockpit.py \
  scripts/verify_multi_agent_operator_cockpit.py \
  src/well_harness/multi_agent_team.py \
  src/well_harness/multi_agent_operator_cockpit.py \
  tests/test_multi_agent_operator_cockpit.py
```

This package depends on the earlier Project Manager Status and UltraWork Monitor packages. If those files are not committed in the target branch, stage them as earlier packages first rather than silently bundling unrelated dirty work.

## Verification

```sh
python3 -m py_compile \
  src/well_harness/multi_agent_team.py \
  src/well_harness/multi_agent_operator_cockpit.py \
  scripts/run_multi_agent_operator_cockpit.py \
  scripts/verify_multi_agent_operator_cockpit.py

PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_operator_cockpit.py

make multi-agent-operator-cockpit

make verify-multi-agent-operator-cockpit
```

Browser gate: open the generated HTML and verify it shows `Multi-Agent Operator Cockpit`, `Project Manager Status`, `UltraWork Monitor`, `five_agent_context_cap`, `PackagingPRReadinessAgent`, `RUN-QUEUE-011`, and `repo_github_local_artifacts` without desktop or mobile layout overflow.
