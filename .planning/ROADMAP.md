# Roadmap

## Current Milestone

Make AI FANTUI LogicMVP run as a GSD-managed, Notion-synced development loop where routine execution is automated and the only planned human checkpoint is Opus 4.6 review.

## Phase P0: Control Tower And GSD Control Plane

Status: Done

Goal: Create the independent Notion control tower and align it with the local GSD model.

Exit Criteria:

- Notion root page exists as `AI FANTUI LogicMVP 控制塔`.
- Roadmap, task, session, decision, QA, asset, risk, plan, execution run, review gate, and UAT gap objects exist.
- The control tower treats GitHub / repo as code truth and Notion as control plane.

## Phase P1: Automate Execution And QA Writeback

Status: Active

Goal: Connect the local/GitHub GSD execution loop to Notion so plan runs, QA outcomes, and UAT gaps write back automatically.

Exit Criteria:

- A local script can run validation commands and write Execution Run + QA + UAT Gap state to Notion.
- A GitHub Actions workflow reuses the same script.
- Missing Notion or GitHub credentials degrade safely without leaking secrets.
- Failures become UAT gaps; subjective review is routed through the Opus 4.6 review gate.

## Phase P2: Remove Remaining Browser Hand-Check Dependency

Status: Planned

Goal: Replace the remaining manual browser hand-check with a reproducible automated or semi-automated validation asset.

Exit Criteria:

- The cockpit demo validation path can be replayed without manual mouse/trackpad work.
- The boundary between automated checks and Opus 4.6 subjective review is explicit.
- Results write back to Notion through the same GSD automation bridge.
