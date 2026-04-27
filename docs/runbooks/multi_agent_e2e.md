# Multi-agent E2E runbook (P47-03b · 2026-04-27)

This is the **manual** companion to the deterministic HTTP integration
test in `tests/test_workbench_p47_03_e2e_loop.py`. Both check the same
flow; the integration test runs in CI, this runbook runs occasionally
when you want to confirm real Claude subagents — driving the workbench
through the natural-language UI — produce the same outcome.

The test costs nothing per run. This runbook costs LLM budget per run,
so don't loop it.

## When to run

- Before a release-tagged commit (sanity check the LLM-driven path
  still parses freeform engineer text the way you expect)
- After material changes to the suggestion-form surface or the
  interpret-suggestion endpoint
- After bumping the LLM model or adjusting the rules vocabulary
  in `_GATE_SYNONYMS_BY_SYSTEM`

## What it exercises

A real engineer / reviewer / executor split — three subagents
collaborating through the workbench HTTP API + the static UI:

```
┌────────────┐ submits suggestion → POST /interpret + /proposals
│ engineer   │
│ subagent   │ refines until interpretation matches intent
└────────────┘
       │
       ▼
┌────────────┐ reviews open inbox → POST /accept
│ reviewer   │
│ subagent   │
└────────────┘
       │
       ▼
┌────────────┐ /gsd-execute-phase-from-brief PROP-XXX
│ executor   │ → branch → edit → tests → PR → user merge
│ subagent   │ → POST /landed
└────────────┘
       │
       ▼
   inbox lights up the "↩ 提议回退此修改" button
       │
       ▼
   reviewer or another engineer can run the same loop in revert mode
```

## Setup

```bash
make dev   # starts dev server on http://localhost:8770
```

Confirm `state-of-world` reports the expected three namespaces:

```bash
curl -s http://localhost:8770/api/workbench/state-of-world | \
  jq '.panel_namespaces[].namespace'
# → "logic_truth"
# → "requirements"
# → "simulation_workbench"
```

## Step 1 — Engineer subagent

Spawn a Claude subagent with this brief (paste into a fresh /agents
session or use the Agent tool):

> You are an engineer using the AI fan-tui control logic workbench.
> Your task: report a perceived issue with the L2 SW2 condition in
> the thrust-reverser system. You believe SW2 should "tighten" or
> "shrink" — currently you're seeing too many false-OK signals.
>
> Drive the workbench HTTP API directly (no browser):
> 1. POST `http://localhost:8770/api/workbench/interpret-suggestion`
>    with body `{"text": "<your free-form text>", "system_id": "thrust-reverser", "strategy": "llm"}`
> 2. Inspect the returned interpretation. If `affected_gates` doesn't
>    include "L2" and `target_signals` doesn't include "SW2", refine
>    the text and re-call. (The rules path may pick up "L2 SW2"
>    explicitly; the LLM path may need clearer hints.)
> 3. When the interpretation matches your intent, POST
>    `http://localhost:8770/api/proposals` with body
>    `{"source_text": "<your text>", "interpretation": <the dict>, "author_name": "engineer-bot", "author_role": "ENGINEER", "system_id": "thrust-reverser"}`
> 4. Report the returned proposal id back to the operator.

Expect: a proposal id like `PROP-20260427T120000123456-abc123`.

## Step 2 — Reviewer subagent

Spawn a separate Claude subagent:

> You are the technical reviewer for the workbench. Open
> `http://localhost:8770/api/proposals?status=OPEN` and report the
> open tickets. For the ticket with author "engineer-bot", evaluate
> whether the interpretation is sensible (change_kind, affected_gates,
> target_signals coherent with the source_text). If yes, accept it:
> POST `http://localhost:8770/api/proposals/<id>/accept` with body
> `{"actor": "reviewer-bot", "note": "<one-sentence rationale>"}`.
>
> Confirm the response has `status: "ACCEPTED"`. Then list
> `.planning/dev_queue/` to confirm the brief landed and report its
> path.

Expect: `.planning/dev_queue/PROP-XXX.md` exists and contains the
engineer's source_text + interpretation summary.

## Step 3 — Executor subagent

Run **in the same Claude session you'd use for real work** (this is
where the truth-engine writes happen). Use the slash command:

```
/gsd-execute-phase-from-brief PROP-XXX
```

The skill will:

1. Read the brief
2. Plan the change
3. Ask you (the operator, not the subagent) to confirm the plan
4. Edit `controller.py` / `models.py` / etc. on a feature branch
5. Run tests
6. Open a PR

After you merge the PR, the executor subagent should call
`/landed`:

```bash
git pull
SHA=$(git log -1 --format=%H --grep="PROP-XXX")
curl -X POST http://localhost:8770/api/proposals/PROP-XXX/landed \
     -H 'Content-Type: application/json' \
     -d "{\"sha\": \"$SHA\", \"actor\": \"claude-code-executor\"}"
```

Expect: response contains `landed_truth_sha: <SHA>`.

## Step 4 — Verify the inbox surfaces the revert affordance

Open `http://localhost:8770/workbench` in a browser. Find the proposal
card. Confirm:

- `landed_truth_sha` chip is visible (mono short SHA)
- `↩ 提议回退此修改` button is visible
- `🔁 回滚指引 · Rollback hints` expander still works
- Panel-version chip's `logic_truth` row shows the new SHA

## Step 5 — Revert flow (optional but recommended)

Click `↩ 提议回退此修改`. Confirm dialog. Accept.

Expect a new proposal card at the top with:
- `🔄 REVERT` kind badge
- `↩ 回退目标 · Reverts: PROP-XXX commit <sha>` banner
- Amber left-border styling

Spawn a reviewer subagent to accept the revert; then run the executor
flow again on the revert brief. Verify the resulting PR is a `revert(`
PR (not a `feat(`) and that the changes are the inverse of the
original.

## Pass criteria

| Gate | Pass condition |
|---|---|
| Engineer can submit | proposal id returned with `kind=modify`, `status=OPEN` |
| Reviewer can accept | status flips to ACCEPTED, brief written |
| Executor merges PR | tests pass, PR description references `PROP-XXX` |
| `/landed` records SHA | `landed_truth_sha` set on proposal |
| Inbox shows revert button | rendered when `kind=modify` + ACCEPTED + landed |
| Revert proposal created | `kind=revert`, `revert_target_sha` matches |
| Revert brief instructs plan/ask/edit | brief body contains "DO NOT just run git revert" |

If any row fails, file a defect referencing the proposal id and the
specific HTTP response or screenshot. Don't fix in this runbook —
the integration test in `tests/test_workbench_p47_03_e2e_loop.py`
is the regression net; this runbook is just the manual smoke check.

## Cleanup

Each manual run leaves real artifacts in `.planning/proposals/` and
`.planning/dev_queue/`. They're gitignored, but locally they
accumulate. Periodically:

```bash
rm -rf .planning/proposals/PROP-*-engineer-bot* \
       .planning/dev_queue/PROP-*-engineer-bot*
```

Or wipe everything (only if you're sure no real work is in flight):

```bash
rm -rf .planning/proposals/* .planning/dev_queue/*
```
