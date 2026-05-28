# Multi-Agent Release Decision Input

M31 turns the M30 review-closure packet into a reusable owner-facing release
decision input. It does not decide, approve, merge, resolve GitHub threads, or
change external planning surfaces.

## Control Boundary

- Active control plane: `repo_github_local_artifacts_only`
- Input: `multi_agent_review_closure_v0_1.json`
- Output: read-only JSON, Markdown, and HTML decision input artifacts
- Out of scope: Notion control-plane changes, self-approval, auto-merge,
  review-thread resolution, artifact cleanup, and truth-engine changes

## Decision Shape

The packet exposes four explicit options:

- `owner_acceptance`
- `wait_for_remote_checks`
- `fix_actionable_reviews`
- `merge_when_authorized`

`merge_when_authorized` is intentionally disabled in the packet. The artifact
is only an input to a human/project-owner decision.

## Local Entrypoints

Generate:

```sh
make multi-agent-release-decision-input
```

Verify:

```sh
make verify-multi-agent-release-decision-input
```

The verifier requires a ready M30 closure, zero actionable review threads, a
clean/mergeable PR state, the five-agent roster cap, and the explicit boundary
that automation must not merge or self-approve.
