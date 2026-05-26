# AI FANTUI LogicMVP Project Takeover Blueprint

Date: 2026-05-27
Worktree: `/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/goal-canvas-panel`
Branch: `codex/goal-canvas-panel`
Mode: cautious continuation, repo-local recovery point

## Current Truth Hierarchy

1. Workspace root is a control root, not the editable Git repo.
   - Use `repo-anchor` to inspect the Git worktree registry.
   - Use selected `worktrees/*` directories for implementation.
2. Current product blueprint is the local single-user control-logic workbench:
   `/workbench` as a Canvas-style sandbox graph editor, runner, debugger,
   archive/readback, and review handoff surface.
3. `src/well_harness/controller.py` remains confirmed controller truth.
   Current UI/canvas work must stay sandbox-only and preserve
   `truth_effect: none`, `candidate_state: sandbox_candidate`, and
   `certification_claim: none`.
4. Older `requirements-intake-webui` / M21 / blueprint authority material
   remains useful as historical evidence and delivery packaging context, but
   should not silently override the current `/workbench` canvas mainline.
5. `WORKTREE_INDEX.md` and `WORKSPACE_ORGANIZATION.md` are useful topology
   records but contain date-specific routing notes. Re-check live worktrees
   before acting on their "current active" statements.

## Progress Snapshot

The active `/workbench` canvas line has already moved through these local
phases in this branch:

- Phase 1: default first screen moved from proof-first to Canvas-first, with
  explicit blank-canvas and reference-load paths.
- Phase 2: inspector split into explicit modes: node detail, run result,
  hardware evidence, and handoff package.
- Phase 3: reference circuit restored as first-screen proof view, with blank
  authoring still available.
- Phase 4: new engineer guide and step highlighting added.
- Phase 5: reference visual wiring and outsider tutorial improved.
- Phase 6: guide collapsed by default so the canvas dominates.
- Phase 7: canvas-dominant pan/zoom and overlay surfaces added.
- Phase 8: reference readability improved with connected endpoints and clearer
  node names.
- Phase 9: Chinese node labels, visible directional wires, and default
  inspector collapse added.
- Phase 10: secondary status labels localized to Chinese while preserving raw
  contract values in data attributes, JSON, archives, and schemas.

Current uncommitted implementation also includes a focused archive semantics
repair: a sandbox diff run and scenario-test run are now distinguished in the
review archive regression bundle, so `run_sandbox` can pass from
`diff_summary` while `run_scenario_tests` can honestly remain `not_run`.

## Product Blueprint

The product should be judged as:

> a local control-logic engineering workbench where an engineer can author a
> sandbox candidate graph, run deterministic scenarios, inspect failure traces,
> attach hardware/interface evidence, and package an honest review archive
> without promoting or mutating certified controller truth.

Near-term blueprint:

1. Canvas first: make the reference graph and empty authoring graph visually
   understandable before adding more panels.
2. Engineer loop: keep the main flow short and direct: create -> wire -> run ->
   inspect -> archive -> handoff.
3. Evidence honesty: every handoff/archive must separate actual run evidence,
   not-run sections, local-only evidence, and non-claimed gates.
4. UI language: visible text should be Chinese-first and domain-facing; raw
   internal enum values should stay available only as contract data.
5. Release maturity: keep local smoke/e2e/manifest evidence explicit; do not
   claim production, certification, cloud readiness, or full mypy clean.

## Next Slice Recommendation

Next narrow slice: close Phase 11 as a "takeover and archive semantics hardening"
slice before broader visual polish.

Why this slice:

- The branch is already dirty with Phase 1-10 work. Packaging the current state
  reduces compaction/resume risk.
- The newest functional change is not purely visual: archive regression steps
  now distinguish sandbox diff evidence from scenario-test evidence.
- A focused contract around that distinction is safer than starting a new UI
  redesign immediately.

Suggested `/goal`:

```text
/goal Close the current `/workbench` takeover slice by packaging the Phase 1-10 canvas progress and the archive-regression semantics repair into a recoverable Phase 11 handoff without changing controller truth or starting a new visual redesign.

Scope:
  - Work only in `/Users/Zhuanz/AI-FANTUI-LogicMVP-Workspace/worktrees/goal-canvas-panel`.
  - Allowed implementation files only if required by failing focused tests:
    `src/well_harness/static/workbench.html`,
    `src/well_harness/static/workbench.js`,
    `tests/test_workbench_editable_canvas_shell.py`,
    `tests/e2e/test_workbench_js_boot_smoke.py`.
  - Allowed docs/artifacts:
    `docs/coordination/workbench-phase11-takeover-archive-semantics-handoff.md`,
    optional local visual evidence under `artifacts/workbench-phase11-takeover/`.

Constraints:
  - Do not edit `src/well_harness/controller.py`, adapters, certified YAML,
    public schemas, CLI contracts, or persistent archive formats.
  - Preserve raw enum/contract values in `data-*`, JSON, archive, and schema
    surfaces; localize visible UI labels only.
  - Do not add dependencies, frontend frameworks, databases, cloud sync,
    collaboration, permissions, or certification claims.
  - Do not revert or reformat unrelated dirty files.
  - Keep all candidate/archive claims local-only and sandbox-only.

Done when:
  1. A Phase 11 handoff doc names the current worktree, branch, changed files,
     Phase 1-10 status, current archive semantics repair, and next recommended
     implementation slice.
  2. `node --check src/well_harness/static/workbench.js` exits 0.
  3. `PYTHONPATH=src:. python3 -m pytest -q tests/test_workbench_editable_canvas_shell.py -k "phase10_secondary_status or cockpit_editor"` exits 0.
  4. `PYTHONPATH=src:. python3 -m pytest -q -m e2e tests/e2e/test_workbench_js_boot_smoke.py -k "archive_after_sandbox_run_has_structured_not_run_test_sections or candidate_debugger_view_tracks_failing_assertion_and_archive or preflight_analyzer_classifies_failed_candidate_and_archives"` exits 0.
  5. `git diff --check` exits 0.
  6. Final response reports changed files, implementation summary, verification
     command, test result, risks/unresolved issues, and next recommended step.

Stop if:
  - Any required fix would touch controller truth, adapters, certified YAML,
    schemas, CLI contracts, or persistent archive format.
  - Focused e2e cannot run because the local browser/driver is missing.
  - Existing unrelated dirty work overlaps the files needed for the slice.
  - The work expands into a new UI redesign, cloud/platform capability,
    multi-agent orchestration, or certification claim.
```

## Verification On 2026-05-27

- `node --check src/well_harness/static/workbench.js` -> pass.
- `PYTHONPATH=src:. python3 -m pytest -q tests/test_workbench_editable_canvas_shell.py -k "phase10_secondary_status or cockpit_editor"` -> `3 passed, 57 deselected`.
- `PYTHONPATH=src:. python3 -m pytest -q -m e2e tests/e2e/test_workbench_js_boot_smoke.py -k "archive_after_sandbox_run_has_structured_not_run_test_sections or candidate_debugger_view_tracks_failing_assertion_and_archive or preflight_analyzer_classifies_failed_candidate_and_archives"` -> `3 passed, 60 deselected`.
- `git diff --check` -> pass.

## Risks And Open Questions

- The branch remains intentionally dirty with substantial Phase 1-10 work and
  untracked coordination/artifact files. Do not treat it as PR-ready until the
  changed-file set is reviewed and either committed, split, or intentionally
  archived.
- Workspace routing docs disagree by date: older notes point to
  `requirements-intake-webui`, while newer product blueprint material points to
  the `/workbench` canvas line. Resolve routing from live worktree state and
  latest repo-local blueprint docs, not from a single stale "current" sentence.
- Full validation suite was not rerun in this takeover pass. Earlier phase docs
  record successful suite runs with a recurring Notion `opus_brief` degraded
  payload; rerun the full suite before claiming branch closure.
- The current visual/product question remains: reference graph must be honest
  about whether it is a source-backed full C919 E-TRAS graph or a thrust-reverser
  reference/control fragment.
