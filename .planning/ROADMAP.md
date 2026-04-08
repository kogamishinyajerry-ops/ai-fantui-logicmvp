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

## Phase P1: Automate Execution And Evidence Writeback

Status: Done

Goal: Connect the local/GitHub GSD execution loop to Notion so plan runs, QA outcomes, and UAT gaps write back automatically, while keeping GitHub and Notion as the only evidence surfaces used by Opus 4.6.

Exit Criteria:

- A local script can run validation commands and write Execution Run + QA + UAT Gap state to Notion.
- A GitHub Actions workflow reuses the same script.
- The GitHub repo and workflow runs are usable as review evidence from Notion.
- Missing Notion or GitHub credentials degrade safely without leaking secrets.
- Failures become UAT gaps; subjective review is routed through the Opus 4.6 review gate without citing local terminal files.
- P1 was approved in the Review Gate and the two historical same-plan failure gaps were resolved as superseded.

## Phase P2: Harden Opus 4.6 Review Packets

Status: Done

Goal: Standardize the Opus 4.6 review packet so subjective approval happens from Notion pages and the GitHub repo alone.

Exit Criteria:

- A state-driven current Opus 4.6 review brief exists in Notion and can be refreshed from live control-plane state.
- Review Gate instructions explicitly forbid local terminal file references.
- The boundary between automated validation and Opus 4.6 subjective review is explicit.
- The current brief successfully drove an Opus adjudication that approved P1 and resolved legacy gaps.
