# /gsd-execute-phase-from-brief

> Closes the last manual gap in the AI FANTUI Workbench loop:
> engineer → reviewer (accept) → **this skill** → truth-engine commit.

## What this skill does

Picks up the next dev-queue brief that the workbench's accept flow
dropped at `<repo>/.planning/dev_queue/PROP-*.md`, plans the
truth-engine change it implies, asks the user to confirm before any
edit, implements it on a feature branch, runs the test suite, and
opens a PR. On success, deletes the brief so the queue advances.

Briefs are produced by `demo_server.write_dev_queue_brief()` in the
ai-fantui-logicmvp repo (P44-05). The schema is contract-locked by
`tests/test_dev_queue_brief_contract_p46_03.py` so this skill can
rely on the field set staying stable.

## When to use

- User says `/gsd-execute-phase-from-brief` with no arguments → pick
  the **oldest** brief in the queue
- User says `/gsd-execute-phase-from-brief PROP-20260426T091528887763-272298`
  → pick that exact brief by id
- User says `/gsd-execute-phase-from-brief --list` → just list the
  queue, don't act on anything

## Required context

Always start by reading these to ground the work:

1. **The brief itself**: `.planning/dev_queue/{ID}.md`
2. **The proposal JSON**: `.planning/proposals/{ID}.json` — carries
   the full audit trail (status, history, original interpretation,
   author, ticket id, system_id)
3. **The truth-engine map**: which file owns the gate / signal the
   brief targets:
   - `src/well_harness/controller.py` — control-logic decisions
     (the L1..L4 chain on thrust-reverser; gate semantics live here)
   - `src/well_harness/runner.py` — runtime orchestration / timing
   - `src/well_harness/models.py` — schema, types, enums
   - `src/well_harness/adapters/*.py` — system-specific intake
     (e.g. `c919_etras_intake_packet.py` for c919-etras)
4. **`docs/coordination/plan.md`** — the project's authoritative
   "what's the current arc + what are the open gates"

## Procedure

### Step 1 — Read the queue, pick a brief

```bash
ls -t .planning/dev_queue/PROP-*.md | head -5
```

If empty: report `dev queue is empty — nothing to execute` and
stop. Otherwise pick the brief per the user's argument (or oldest).

### Step 2 — Parse the brief + proposal JSON

The brief markdown is structured (P44-05 schema v1). Extract:

- `Status` — must be `ACCEPTED`. Anything else → stop, ask why.
- `System` — drives which truth-engine path applies
- `Affected gates`, `Target signals`, `Change kind` — the structured
  intent
- `Engineer's original suggestion` (Chinese block-quote)
- `System interpretation` summary lines (zh + en)

Cross-reference with the proposal JSON to confirm `status=ACCEPTED`,
note the accept history entry's actor + timestamp.

### Step 3 — Plan the change (NO EDITS YET)

Write a 5-bullet plan to the user:

1. **Where**: which file(s), which function(s), which lines
2. **What**: the concrete code change (text or pseudocode)
3. **Why this satisfies the brief**: link the change to the
   structured intent (change_kind + affected_gates)
4. **Test impact**: which existing tests will need updating, which
   new tests this change should add
5. **Risk**: anything irreversible, any ambiguity in the brief, any
   place where the engineer's intent doesn't unambiguously map to
   code

### Step 4 — Hard confirmation gate

**ALWAYS ASK BEFORE ANY EDIT.** Even on what looks like a one-line
change. Quote: "Plan above. Proceed with edits, or revise?"

- "Proceed" / "go" / "yes" → continue to Step 5
- Anything else → revise the plan, re-ask
- "Stop" / "nevermind" → leave the brief untouched in the queue,
  exit cleanly

This gate is the truth-engine red line: the workbench cannot mutate
truth, the engineer's accept doesn't auto-deploy, the skill itself
confirms before each truth-engine touch.

### Step 5 — Branch + implement

```bash
git checkout main && git pull
git checkout -b feat/exec-{PROP-ID}-{short-desc}
```

Branch name pattern keeps the proposal id discoverable via
`git log --grep="{PROP-ID}"` — that's the same recipe P44-06 puts
in the rollback hints, so the loop closes.

Edit truth-engine files. Add tests. Keep the change minimal — one
proposal = one focused commit, no surrounding cleanup.

### Step 6 — Run tests

```bash
make test
```

If anything red: fix the issue and re-run. If multiple iterations
fail (>3 attempts), pause and report — the brief may be ambiguous
or the change broader than expected.

### Step 7 — Commit + PR

Commit message format:

```
feat({system}): {change_kind} per {PROP-ID}

Engineer suggestion: {first sentence of source_text}
System interpretation: {summary_zh}

Truth-engine touch:
- {file}:{lines} — {what changed}

Implements proposal {PROP-ID} accepted by {actor} at {timestamp}.
Brief: .planning/dev_queue/{PROP-ID}.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

PR title: `feat({system}): {change_kind} per {PROP-ID}` (lift the
commit subject; keep <70 chars).

PR body: the commit body verbatim + a "Verification" checklist
(test count delta, manual smoke steps the user should run).

### Step 8 — On merge, delete the brief

```bash
rm .planning/dev_queue/{PROP-ID}.md
git add .planning/dev_queue/
git commit -m "chore: clear dev_queue/{PROP-ID}.md (PR #N merged)"
```

The proposal JSON remains in `.planning/proposals/` as the audit
truth (status, history, original interpretation). The brief was
just the handoff signal; once executed it has no further use.

## Truth-engine red line — critical

This skill is the ONLY surface authorized to mutate
`controller.py` / `runner.py` / `models.py` / `adapters/` from a
proposal. The workbench (demo_server, workbench static) never does.
Two enforced safeguards:

1. **Always ask** before any edit (Step 4)
2. **Always go through PR review** — even auto-confirmed plans
   commit to a feature branch, never directly to `main`

If the user invokes the skill with `--auto-merge` or similar
bypass, refuse. The PR review by the user is the constitutional
gate; bypassing it would let an engineer's casual ticket
(low-confidence interpretation, ambiguous wording) silently
become production code.

## Common pitfalls

- **Brief targets a placeholder system** (landing-gear /
  bleed-air-valve / c919-etras): those systems' real circuits
  aren't drafted yet. The proposal can still describe a real
  truth-engine change (e.g. add a sensor signal in `models.py`),
  but the SVG-side work is out of scope until the circuit lands.
  Note this in the plan.
- **Brief says `change_kind=propose_change`**: the rules
  interpreter fell back to the generic class because no specific
  verb matched. Read the source_text carefully — the engineer
  might mean something specific the rules missed.
- **Brief affects gates the truth engine doesn't model**: e.g. an
  E1/E2/E3 c919-etras gate doesn't appear in `controller.py` yet.
  This is a "feature work" proposal, not a "fix" — the plan
  should call this out explicitly and likely propose a multi-PR
  arc rather than try to land it in one commit.
- **Brief contradicts existing tests**: if the change would break
  a passing test that asserts the OLD behavior, the test almost
  always needs updating too. Show both the code edit and the test
  update in the plan; a test failing because the spec changed is
  fine, a test failing because the implementation broke is not.

## Output format

When summarizing back to the user after a successful run:

```
✅ {PROP-ID} executed
   System:        {system_id}
   Change:        {change_kind} on {affected_gates}
   Branch:        {branch}
   PR:            {url}
   Tests:         {N}/{N} passing ({delta} new)
   Brief deleted: .planning/dev_queue/{PROP-ID}.md
```

## Why a skill, not a script

A bash script could mechanically do steps 5-8. The skill exists for
steps 2-4: parsing the engineer's intent from natural-language
suggestion + interpretation, mapping it to the right file, and
asking the right confirmation question. Those need a model, not a
shell.
