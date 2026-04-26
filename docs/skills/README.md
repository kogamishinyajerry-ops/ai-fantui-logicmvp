# Workbench-adjacent Claude Code skills

This directory documents Claude Code slash-commands that are part
of the AI FANTUI Workbench loop but live OUTSIDE this repo (in the
user's `~/.claude/commands/` config tree). The skills themselves
are user-level — they're personal Claude Code config — but they
read contracts (file formats, paths) defined here, so we want
discoverability + a contract test in this repo.

## /gsd-execute-phase-from-brief

**File**: `~/.claude/commands/gsd-execute-phase-from-brief.md`
**Purpose**: closes the last manual step in the workbench loop.
After the reviewer accepts a proposal in `/workbench`, P44-05
drops a markdown brief at `.planning/dev_queue/PROP-*.md`. This
skill picks the next brief, plans the truth-engine change,
**asks for confirmation before any edit**, implements it on a
feature branch, runs `make test`, and opens a PR.

### Why a skill, not a script

A bash script could mechanically branch / commit / push. The
skill exists for the parts that need a model: parsing the
engineer's natural-language suggestion + the system
interpretation, mapping the `change_kind` + `affected_gates`
to specific files and lines, asking the right confirmation
question, and writing a commit message that future engineers
(or the rollback hint expander in P44-06) can find.

### Truth-engine red line

This is the **only** automated path that mutates
`controller.py` / `runner.py` / `models.py` / `adapters/` from
a workbench proposal. Two enforced safeguards:

1. The skill **always asks** before any edit (Step 4 in the
   spec). Even on what looks like a one-line change.
2. The skill **always opens a PR** — never commits straight to
   `main`. Your normal PR review is the constitutional gate.

### Installing

The skill spec ships with this repo at
`docs/skills/gsd-execute-phase-from-brief.md` (a snapshot for
reference). The active copy lives at
`~/.claude/commands/gsd-execute-phase-from-brief.md` and is
registered automatically by the Claude Code skill loader.

To re-install / refresh:

```bash
cp docs/skills/gsd-execute-phase-from-brief.md \
   ~/.claude/commands/gsd-execute-phase-from-brief.md
```

To verify it's loaded, ask Claude Code: `/gsd-execute-phase-from-brief --list`.
The skill should respond with the current dev-queue contents.

### Contract test

`tests/test_dev_queue_brief_contract_p46_03.py` locks the
markdown schema the skill parses against the schema
`demo_server.write_dev_queue_brief()` produces. If a future
refactor removes a field from the brief without updating the
skill, this test fails loudly so the loop doesn't break
silently.
