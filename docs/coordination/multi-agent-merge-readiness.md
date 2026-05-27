# Multi-Agent Merge Readiness

Date: 2026-05-27
Status: M29 read-only PR review and merge-readiness handoff

## Purpose

This package turns the current PR evidence into a single local review entry. It
does not stage, commit, push, merge, self-approve, or write to Notion.

The packet answers four questions:

1. Did the 19 validation commands pass?
2. Did the status-surface browser geometry gate pass on desktop and mobile?
3. Is PR #269 mergeable, and are there reviews/comments/checks to address?
4. Is the Notion 404 still classified as an external control-plane blocker?

The packet also carries the five-agent active team cap so PR review does not
inflate historical task labels into extra live agents.

## Local Entry

```sh
make multi-agent-merge-readiness
```

Default output:

```text
/tmp/ai-fantui-multi-agent-merge-readiness/multi_agent_merge_readiness_v0_1.html
```

Verifier:

```sh
make verify-multi-agent-merge-readiness
```

## Pathspec Package

Stage this slice only with explicit pathspecs:

```sh
git add -- \
  Makefile \
  docs/coordination/multi-agent-control-logic-engineering-system-mvp.md \
  docs/coordination/multi-agent-merge-readiness.md \
  docs/json_schema/multi_agent_merge_readiness_v0_1.schema.json \
  scripts/run_multi_agent_merge_readiness.py \
  scripts/verify_multi_agent_merge_readiness.py \
  src/well_harness/multi_agent_team.py \
  src/well_harness/multi_agent_merge_readiness.py \
  tests/test_multi_agent_merge_readiness.py
```

## Excluded Dirty Context

Do not stage these paths from this readiness package:

```text
.github/workflows/gsd-automation.yml
artifacts/**
src/well_harness/controller.py
src/well_harness/runner.py
src/well_harness/demo_server.py
src/well_harness/requirements_intake/**
src/well_harness/static/**
tests/test_demo.py
tests/test_requirements_intake_webui.py
tests/test_validation_suite.py
tools/run_gsd_validation_suite.py
.planning/**
```

## Notion Blocker

`notion-control-plane-404` remains an external control-plane blocker. This
readiness package must not change Notion configuration, Notion sync scripts, or
Notion page permissions.

## Verification

```sh
python3 -m py_compile \
  src/well_harness/multi_agent_team.py \
  src/well_harness/multi_agent_merge_readiness.py \
  scripts/run_multi_agent_merge_readiness.py \
  scripts/verify_multi_agent_merge_readiness.py

PYTHONPATH=src:. python3 -m pytest -q tests/test_multi_agent_merge_readiness.py

make multi-agent-merge-readiness

make verify-multi-agent-merge-readiness
```

Browser gate: open the generated HTML and verify it shows `Multi-Agent Merge
Readiness`, `five_agent_context_cap`, `PackagingPRReadinessAgent`,
`RUN-QUEUE-011`, `19 validation commands passed`, `notion-control-plane-404`,
and `MERGEABLE` without desktop or mobile layout overflow.
