# Multi-Agent Owner Decision Request

Status: M33 read-only owner decision request bridge

M33 consumes the M32 owner acceptance handoff and produces an explicit
project-owner decision request packet. It does not record acceptance, merge a
PR, self-approve, resolve review threads, delete artifacts, or change
Notion/control-plane configuration.

## Entrypoints

- `make multi-agent-owner-decision-request`
- `make verify-multi-agent-owner-decision-request`

The generator writes JSON, Markdown, HTML, and a non-authoritative owner
decision input template under:

`/tmp/ai-fantui-multi-agent-owner-decision-request`

## Inputs

- M32 owner acceptance handoff:
  `/tmp/ai-fantui-multi-agent-owner-acceptance-handoff/multi_agent_owner_acceptance_handoff_v0_1.json`

## Acceptance Boundary

The request packet is valid only when:

- M32 is ready for owner acceptance.
- M32 has no active blockers.
- The packet records that explicit owner input is still required.
- No owner decision has been recorded by the packet itself.
- The decision template remains in `template_mode`.
- The control plane remains `repo_github_local_artifacts_only`.

Remote checks can remain a warning when GitHub reports no checks. The owner can
choose to wait for remote checks, request review follow-up, return the lane to
development, or provide a separate explicit acceptance decision when authorized.

## Explicit Non-Authority

M33 is not a final decision gate. It only prepares the request surface and a
copyable input template. A real decision must come from a separate explicit
project-owner input, and Notion/external planning surfaces stay out of scope.

## Browser Gate

The verifier opens the generated owner-decision request HTML in desktop/mobile
browser viewports, captures screenshots, and fails on missing request/template
labels or page-level horizontal overflow. Unit tests can disable this browser
path with `--skip-browser`; the Makefile gate keeps it enabled.

The generated HTML must show `Multi-Agent Owner Decision Request`,
`Decision Input Template`, `five_agent_context_cap`,
`PackagingPRReadinessAgent`, `repo_github_local_artifacts_only`, and
`external_manual_input_only` with desktop/mobile screenshots and no horizontal
layout overflow.
