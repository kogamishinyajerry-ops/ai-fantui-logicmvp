# E09 Closure - Prompt Generator, Ticket Publisher, Restricted Auth

## What Shipped

- Verified the 02 task DB schema had the E09-required fields:
  - `Type`
  - `Source Proposal`
  - `Authorized Engineer`
  - `Scope Files`
  - `Generated Prompt`
  - `PR URL`
  - `Verdict`
- Added `templates/claude_code_prompt.md.j2` with the required four sections: anchor, scope, acceptance, non-goals.
- Added `src/well_harness/workbench/prompting.py` for:
  - rendering an AnnotationProposal into a Claude Code prompt
  - building a local ticket payload
  - writing local ticket JSON under `tickets/`
  - emitting paste-ready JSON to stdout for Kogami / Notion
- Added `tickets/` scaffolding with runtime ticket JSON ignored by Git.
- Added `src/well_harness/collab/restricted_auth.py` with ticket-scoped push authorization semantics:
  - actor must match `Authorized Engineer`
  - changed files must match `Scope Files`
- Added focused prompt/ticket/auth tests.

## Verification Numbers

- Fast-lane pytest: `815 passed, 1 skipped, 49 deselected, 1 warning in 62.70s`
- E2E pytest: `49 passed, 816 deselected, 1 warning in 2.96s`
- Adversarial browser/server script: `ALL TESTS PASSED` across 8 adversarial sections
- Diff hygiene: `git diff --check` passed

The non-e2e count increased from E08 by three prompt/ticket/auth tests.

## Open Issues

- No Notion writes were performed; the publisher writes local files and emits stdout JSON only.
- Restricted auth is implemented as deterministic middleware for future hook/CLI integration. It is not installed as a GitHub branch protection rule or remote server hook in this slice.
- The prompt renderer intentionally uses explicit placeholder replacement instead of adding a Jinja dependency.

## Handoff Notes

- E10 can consume ticket payloads from `publish_ticket` and validate candidate PR diffs against `Scope Files`.
- Keep `Authorized Engineer` and `Scope Files` as the source of push authority.
- Continue avoiding direct Notion mutation; paste-ready JSON is the handoff surface.
