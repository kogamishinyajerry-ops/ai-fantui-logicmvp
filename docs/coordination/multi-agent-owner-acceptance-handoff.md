# Multi-Agent Owner Acceptance Handoff

Status: M32 read-only owner acceptance handoff

M32 consumes the M31 release decision input and the current GitHub PR state to
produce a project-owner-facing handoff package. It is evidence and checklist
only. It does not merge, self-approve, resolve review threads, delete artifacts,
or change Notion/control-plane configuration.

## Entrypoints

- `make multi-agent-owner-acceptance-handoff`
- `make verify-multi-agent-owner-acceptance-handoff`

The generator writes JSON, Markdown, and HTML artifacts under:

`/tmp/ai-fantui-multi-agent-owner-acceptance-handoff`

## Inputs

- M31 release decision input:
  `/tmp/ai-fantui-multi-agent-release-decision-input/multi_agent_release_decision_input_v0_1.json`
- GitHub PR metadata for the handoff PR.
- GitHub review-thread state.

## Acceptance Boundary

The package is ready only when:

- M31 is ready for owner decision.
- M31 PR URL and head SHA match the handoff PR URL and head SHA.
- M31 has no active blockers.
- GitHub review-thread state is fetched successfully.
- The handoff PR is mergeable.
- No current non-outdated actionable review thread remains.
- Remote checks are pass or warning-only.
- The control plane remains `repo_github_local_artifacts_only`.

Remote checks can remain a warning when GitHub reports no checks. Outdated
unresolved review threads are recorded as a warning, not treated as current
actionable blockers.

## Explicit Non-Authority

M32 does not grant final acceptance. If the project owner accepts, that decision
must be provided through a separate explicit owner decision. This packet also
keeps Notion and external planning surfaces out of scope.

## Browser Gate

The verifier opens the generated owner-acceptance HTML in desktop/mobile browser
viewports, captures screenshots, and fails on missing handoff labels or
page-level horizontal overflow. Unit tests can disable this browser path with
`--skip-browser`; the Makefile gate keeps it enabled.

The generated HTML must show `Multi-Agent Owner Acceptance Handoff`,
`five_agent_context_cap`, `PackagingPRReadinessAgent`,
`repo_github_local_artifacts_only`, and `external_manual_only` with
desktop/mobile screenshots and no horizontal layout overflow.
