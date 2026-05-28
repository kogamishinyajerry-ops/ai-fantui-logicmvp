# Multi-Agent Review Closure

M30 is the read-only PR review closure packet for the multi-agent delivery lane.
It turns the current GitHub PR state into a local JSON, Markdown, and HTML
handoff that can be validated before owner acceptance or an authorized merge.

## Control Boundary

- Active control plane: `repo_github_local_artifacts_only`
- In scope: PR head SHA, latest Codex clean result, current review-thread
  classification, mergeability, remote check state, and explicit pathspec
  staging.
- Out of scope: Notion control-plane configuration, workflow-level Notion sync,
  artifact cleanup, self-approval, merge execution, and truth-engine changes.

## Artifact Contract

The generator emits:

- `multi_agent_review_closure_v0_1.json`
- `multi_agent_review_closure_v0_1.md`
- `multi_agent_review_closure_v0_1.html`

The verifier requires:

- latest-head Codex review closure is present;
- actionable current review thread count is zero;
- PR mergeability is clean or mergeable;
- remote checks are pass or warning;
- the active agent roster stays capped at five;
- `.planning/notion_control_plane.json` remains excluded from staging.

## Local Entrypoints

Generate:

```sh
make multi-agent-review-closure
```

Verify:

```sh
make verify-multi-agent-review-closure
```

The package is intentionally read-only. If GitHub still displays unresolved
threads after a clean latest-head Codex result, the packet records them as
classification evidence instead of resolving them from automation.
