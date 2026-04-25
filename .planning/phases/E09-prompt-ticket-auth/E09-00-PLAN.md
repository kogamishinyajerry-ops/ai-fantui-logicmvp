# E09 Plan - Prompt Generator, Ticket Publisher, Restricted Auth

## Objective

Convert approved AnnotationProposal payloads into Claude Code prompts and local ticket JSON that Kogami can paste into Notion, then enforce ticket-scoped commit authority through restricted-auth middleware.

## Schema Check

The 02 task DB schema check passed before implementation. Required fields were present:

- `Type`
- `Source Proposal`
- `Authorized Engineer`
- `Scope Files`
- `Generated Prompt`
- `PR URL`
- `Verdict`

No `BLOCKED` condition is active for E09.

## Scope

- Add `templates/claude_code_prompt.md.j2` with four sections:
  - anchor
  - scope
  - acceptance
  - non-goals
- Add Workbench prompt and ticket publisher code under `src/well_harness/workbench/`.
- Add `tickets/` scaffolding with runtime ticket JSON ignored by Git.
- Add `src/well_harness/collab/restricted_auth.py`.
- Add focused tests for prompt rendering, ticket stdout JSON, local file publishing, and restricted-auth decisions.

## Counterarguments And Mitigations

1. Counterargument: direct Notion writes would be more convenient.
   Mitigation: the prompt explicitly forbids direct Notion writes; the publisher emits structured JSON to stdout and writes only local ticket files.

2. Counterargument: a `.j2` template implies a Jinja dependency.
   Mitigation: use a tiny explicit replacement renderer for known placeholders to avoid adding dependencies and keep output deterministic.

3. Counterargument: restricted auth is easy to over-claim without a Git server hook.
   Mitigation: implement deterministic middleware semantics that can be invoked by future hooks or CLIs; do not claim server-side enforcement is installed.

4. Counterargument: scope-file matching can become too permissive.
   Mitigation: match exact file paths, directory prefixes, or shell-style glob patterns only; unknown paths fail closed.

## Success Criteria

- A proposal renders a Claude Code prompt containing the four required sections.
- Publishing writes a local `tickets/*.json` payload and emits paste-ready JSON to stdout.
- The ticket payload includes the required Notion field names.
- Restricted-auth accepts only the authorized engineer and only changed files within `Scope Files`.
- Existing fast-lane, e2e, and adversarial checks remain green at closure.
