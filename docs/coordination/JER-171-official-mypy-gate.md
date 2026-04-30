# JER-171 Official Mypy Strict Gate

Date: 2026-04-30

## Issue

- Linear: JER-171
- Title: `[project] [L9] [none] [DAL-TBD] Official mypy strict gate definition`
- Adapter: project
- Layer: L9
- Truth-level impact: none
- Red lines touched: none

## Official Command

Codex Daily Lane mypy evidence must use:

`PYTHONPATH=src:. python3 tools/run_mypy_gate.py --format json`

Install the optional typecheck dependencies with:

`python3 -m pip install -e '.[typecheck]'`

The wrapper runs the full-scope strict command:

`python3 -m mypy --strict --explicit-package-bases src tests tools`

## Current Baseline Result

The current `origin/main` baseline is not mypy-clean.

Observed direct command result on 2026-04-30:

- Command: `PYTHONPATH=src:. python3 tools/run_mypy_gate.py --format json --report-only`
- Result: fail
- Summary: 4692 errors in 322 files, 379 checked source files

This is a known baseline blocker, not a JER-171 truth or runtime change.

## Gate Semantics

- `status: pass` means the official full-repo strict mypy gate is clean.
- `status: blocked` means the official command ran, but the current repo
  baseline is still not clean.
- `--report-only` may be used to archive JSON evidence without making local
  proof collection fail.
- A `blocked` report must not be described as `mypy --strict clean` in PR
  descriptions.

## Boundaries

- No `controller.py` truth semantics were edited.
- No frozen adapters, frozen hardware YAML, or C919 reference packet were
  edited.
- No truth-level, DAL, or PSSA status was promoted.
- No product LLM/chat behavior was restored.
