# DeepSeek V4 Pro UI Workbench Routing

Date: 2026-05-13
Status: active routing rule

## Decision

The active UI workbench mainline is the DeepSeek V4 Pro driven requirements
intake workflow:

1. `/requirements-intake`
2. `/logic-builder`
3. `/fault-injection-prepare`
4. `/fault-injection-sandbox`

This flow owns the default demo and implementation route. It starts from model
assisted requirements understanding, produces a candidate first logic drawing,
supports annotation-driven revision, then prepares fault-injection and sandbox
dry-run review artifacts.

## Canvas Demotion

The Canvas/workbench branch is frozen and downgraded to a backup feature module.
The `/workbench` editable canvas follows the same downgraded status.

Default rule: do not use, continue, launch, or expand the Canvas branch unless the user explicitly asks for the canvas branch/module by name.

## Scope Boundary

- Keep `src/well_harness/controller.py` read-only unless a separate
  truth-level task explicitly authorizes controller changes.
- DeepSeek V4 Pro outputs remain concept/sandbox-only candidate artifacts.
- The UI may render model outputs and review gates, but must not claim
  certification, controller truth promotion, or production execution.
- The old Canvas work can be referenced only as historical context or as a
  deliberately selected backup module.

## Verification Hooks

- Landing page must carry `data-primary-flow="deepseek-v4-pro-ui-workbench"`.
- Landing page must mark `/requirements-intake` as
  `data-primary-entry="deepseek-v4-pro"`.
- Primary DeepSeek subproject pages must not expose `/workbench` in their
  first-line navigation.
- Focused test: `tests/test_requirements_intake_webui.py`.
