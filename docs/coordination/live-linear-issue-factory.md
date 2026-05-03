# Live Linear Issue Factory

Status: active for live Linear `JER-232`

## Purpose

Post-v5 work now dispatches from live Linear issues. The helper at
`tools/linear_live_issue_factory.py` makes issue creation repeatable without
turning it into an orchestration platform.

## Contract

The helper can:

- render a dry-run issue body with `Outcome`, `Acceptance`, `Boundaries`,
  `Evidence Required`, and `Metadata`;
- create one live Linear issue only when `--confirm-write` is provided;
- read Linear credentials from environment variables at write time.

The helper cannot:

- move Linear issue states;
- create comments or proof updates;
- spawn agents;
- persist API keys, OAuth tokens, environment dumps, or raw terminal logs;
- mutate browser state or workbench runtime state.

## Identifier Guard

Every generated issue body includes an `Identifier Collision Guard` section.
Reports must use `live Linear <identifier>` for Linear-created issues when a
repo-local historical JER label could collide with the same number.

Example:

```bash
source ~/.zshrc
python tools/linear_live_issue_factory.py \
  --title "[project] [L9] [none] [DAL-TBD] Example live issue" \
  --outcome "Create a bounded live issue from the repo-local template." \
  --acceptance "Dry-run output includes required AWCP sections." \
  --boundary "Do not mutate controller truth." \
  --evidence-required "Factory dry-run output." \
  --repo-local-label "JER-233"
```

Add `--confirm-write` only after inspecting the dry-run output.
