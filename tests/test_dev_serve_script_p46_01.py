"""P46-01 — dev-server startup script contract.

Locks scripts/dev-serve.sh + Makefile so a future "cleanup" PR
can't silently break the muscle-memory `make dev` workflow.

These tests do NOT actually start the server (port flap risk +
slow); they verify the script's surface contract:
  - file exists, executable bit set
  - resolves MiniMax key from env / ~/.zshrc / ~/.minimax_key
  - exports MINIMAX_API_KEY, WORKBENCH_PROPOSALS_DIR,
    WORKBENCH_DEV_QUEUE_DIR
  - Makefile `dev` target delegates to the script
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "dev-serve.sh"
MAKEFILE_PATH = REPO_ROOT / "Makefile"


# ─── 1. File exists and is executable ──────────────────────────────


def test_dev_serve_script_exists():
    assert SCRIPT_PATH.is_file(), "scripts/dev-serve.sh missing"


def test_dev_serve_script_is_executable():
    mode = SCRIPT_PATH.stat().st_mode
    assert mode & stat.S_IXUSR, "scripts/dev-serve.sh missing user execute bit"


def test_dev_serve_script_uses_strict_mode():
    """`set -euo pipefail` is the bash safety harness — without it the
    script silently continues past failures (e.g. a mistyped command
    would still exec the server with stale env)."""
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "set -euo pipefail" in text


# ─── 2. Key resolver covers all 4 sources in order ──────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # Order matches _resolve_minimax_api_key in demo_server.py
        '${MINIMAX_API_KEY:-}',
        '${Minimax_API_key:-}',
        # The user's actual var name in ~/.zshrc carries the unusual
        # mixed-case spelling; the regex must catch it.
        'export[[:space:]]+Minimax_API_key=',
        # File fallback path
        '$HOME/.minimax_key',
    ],
)
def test_dev_serve_script_resolves_key_from_all_four_sources(needle):
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert needle in text, f"dev-serve.sh missing key-resolver source: {needle}"


def test_dev_serve_script_does_not_fail_when_key_missing():
    """Server must still boot when no MiniMax key is available — the
    LLM strategy will just fall back to rules. This test verifies
    the script doesn't `exit 1` on missing key."""
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "LLM interpreter will fall back to rules" in text


# ─── 3. Required env vars are exported ──────────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        "export MINIMAX_API_KEY=",
        "export WORKBENCH_PROPOSALS_DIR=",
        "export WORKBENCH_DEV_QUEUE_DIR=",
        # PYTHONPATH must reach the src/ tree.
        "PYTHONPATH=src",
        # The actual server module being launched.
        "well_harness.demo_server",
    ],
)
def test_dev_serve_script_exports_required_env(needle):
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert needle in text, f"dev-serve.sh missing env wiring: {needle}"


def test_dev_serve_script_creates_state_dirs():
    """The two state dirs must exist before the server starts —
    otherwise the first POST /api/proposals would 500 when
    proposals_dir() tries to write into a non-existent override
    path. Verify the mkdir -p call is present."""
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "mkdir -p" in text
    assert "$WORKBENCH_PROPOSALS_DIR" in text
    assert "$WORKBENCH_DEV_QUEUE_DIR" in text


def test_dev_serve_script_kills_existing_port_holder():
    """Re-running `make dev` is the most common workflow — must
    free the port (don't error with "address in use")."""
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "lsof -ti" in text
    assert "kill" in text


# ─── 4. PORT override ──────────────────────────────────────────────


def test_dev_serve_script_honors_port_override():
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    assert 'PORT="${PORT:-8780}"' in text
    assert "--port \"$PORT\"" in text


# ─── 5. Makefile dev target delegates to the script ─────────────────


def test_makefile_exists():
    assert MAKEFILE_PATH.is_file()


def test_makefile_dev_target_delegates_to_script():
    text = MAKEFILE_PATH.read_text(encoding="utf-8")
    assert "dev:" in text
    assert "./scripts/dev-serve.sh" in text


def test_makefile_test_target_uses_pythonpath_src():
    """Lock the test invocation so a contributor can't accidentally
    drop PYTHONPATH=src and break test imports."""
    text = MAKEFILE_PATH.read_text(encoding="utf-8")
    assert "PYTHONPATH=src python3 -m pytest tests/" in text


# ─── 6. Bash syntax validity (last-line guard) ─────────────────────


def test_dev_serve_script_passes_bash_syntax_check():
    """`bash -n` is bash's parse-only mode — catches dropped quotes,
    unmatched if/fi, etc., without executing anything."""
    result = subprocess.run(
        ["bash", "-n", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, (
        f"dev-serve.sh has a bash syntax error:\n{result.stderr}"
    )
