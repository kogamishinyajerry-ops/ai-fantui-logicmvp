"""P28 · pitch symbol verifier.

Extends P26 from path-existence to symbol-existence. Every load-bearing
structural claim the立项 FAQ makes about code (e.g. "_BACKENDS dict",
"VALID_ACTION_TYPES whitelist", "LLMClient Protocol") must correspond to
a symbol that actually exists in the file the FAQ points at.

Non-goals:
  - Do not verify numeric claims (line counts, test counts, latency) —
    those rot naturally and CI-failing on numeric drift is noise (P26's
    rationale carries over).
  - Do not verify semantic content (whether the code actually does what
    the FAQ says). Only structural presence: the symbol is defined.
  - Do not modify any pitch material or source file.

Why a hand-curated list instead of dynamic extraction:
  - FAQ prose doesn't use a single citation syntax; trying to auto-extract
    "file.py::symbol" would either miss claims (prose says "`LLMClient`
    Protocol" not "llm_client.py::LLMClient") or over-match.
  - Hand-curating the load-bearing claims gives false-negative surface but
    zero false-positive risk. Each entry cites source doc + Q# so the
    verifier is self-documenting.

Curation policy: add an entry when a pitch material makes a specific
structural claim a reviewer could falsify. Remove an entry only when
the pitch material itself no longer makes the claim.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Each claim: (id, source_doc, claim_summary, target_file, symbol_pattern)
# symbol_pattern must match once in the target file's content.
CLAIMS = [
    # Q1 · controller exposes a DeployController class
    (
        "Q1-controller-class",
        "docs/demo/faq.md",
        "Q1: controller.py defines the main controller class",
        "src/well_harness/controller.py",
        r"^class\s+DeployController\b",
    ),
    # Q4/Q13 · three chat handlers in demo_server
    (
        "Q4-chat-explain-handler",
        "docs/demo/faq.md",
        "Q4/Q13: /api/chat/explain is implemented",
        "src/well_harness/demo_server.py",
        r"^def\s+_handle_chat_explain\b",
    ),
    (
        "Q4-chat-operate-handler",
        "docs/demo/faq.md",
        "Q4/Q13: /api/chat/operate is implemented",
        "src/well_harness/demo_server.py",
        r"^def\s+_handle_chat_operate\b",
    ),
    (
        "Q13-chat-reason-handler",
        "docs/demo/faq.md",
        "Q13: /api/chat/reason is implemented",
        "src/well_harness/demo_server.py",
        r"^def\s+_handle_chat_reason\b",
    ),
    # Q8/Q15 · llm_client adapter exposes Protocol + factory + two backends
    (
        "Q8-LLMClient-protocol",
        "docs/demo/faq.md",
        "Q8/Q15: LLMClient Protocol declared",
        "src/well_harness/llm_client.py",
        r"^class\s+LLMClient\b.*Protocol",
    ),
    (
        "Q8-MiniMaxClient",
        "docs/demo/faq.md",
        "Q8: MiniMaxClient class",
        "src/well_harness/llm_client.py",
        r"^class\s+MiniMaxClient\b",
    ),
    (
        "Q8-OllamaClient",
        "docs/demo/faq.md",
        "Q8: OllamaClient class",
        "src/well_harness/llm_client.py",
        r"^class\s+OllamaClient\b",
    ),
    (
        "Q8-BACKENDS-dict",
        "docs/demo/faq.md",
        "Q8/Q15: _BACKENDS factory dict",
        "src/well_harness/llm_client.py",
        r"^_BACKENDS\s*:",
    ),
    (
        "Q15-get-llm-client-factory",
        "docs/demo/faq.md",
        "Q15: factory function selects backend",
        "src/well_harness/llm_client.py",
        r"^def\s+get_llm_client\b",
    ),
    # Q11 · operate handler whitelist
    (
        "Q11-VALID-ACTION-TYPES",
        "docs/demo/faq.md",
        "Q11: VALID_ACTION_TYPES whitelist in operate handler",
        "src/well_harness/demo_server.py",
        r"\bVALID_ACTION_TYPES\s*=\s*\{",
    ),
    (
        "Q11-VALID-RESPONSE-TYPES",
        "docs/demo/faq.md",
        "Q11: VALID_RESPONSE_TYPES whitelist in reason handler",
        "src/well_harness/demo_server.py",
        r"\bVALID_RESPONSE_TYPES\s*=\s*\{",
    ),
    # local_model_poc / pitch_script also cite adapter structure — covered
    # transitively by Q8 entries above since it's the same file.
]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_all_claim_targets_exist():
    """Meta-check: every claim's target file must be in-tree."""
    missing = [
        (cid, target) for cid, _doc, _s, target, _pat in CLAIMS
        if not (REPO_ROOT / target).exists()
    ]
    assert not missing, f"Claim target files missing: {missing}"


def test_pitch_symbol_claims_resolve():
    """Every structural symbol claim in pitch materials must resolve in code.

    When this fails, the printed list shows (claim_id, source_doc, target_file,
    pattern). Fix by either updating the pitch material (if the symbol was
    renamed) or restoring the symbol in code (if removed by refactor).
    """
    failures: list[tuple[str, str, str, str]] = []
    for cid, doc, _summary, target, pattern in CLAIMS:
        content = _read(target)
        if not re.search(pattern, content, re.MULTILINE):
            failures.append((cid, doc, target, pattern))
    if failures:
        lines = [
            f"  [{cid}] {doc} → {target} · pattern `{pat}`"
            for cid, doc, target, pat in failures
        ]
        raise AssertionError(
            f"\n{len(failures)} broken structural claim(s):\n"
            + "\n".join(lines)
        )


def test_no_anthropic_runtime_dependency():
    """FAQ Q9 claim: runtime deps don't include `anthropic`.

    The FAQ explicitly tells甲方 '交付到甲方后没有 Claude 依赖'. This test
    validates the substantive claim against the real manifest
    (pyproject.toml). See docs/demo/pitch-citations-audit.md for the
    separate note about Q9 literally citing `requirements.txt`, which does
    not exist in this repo — the substance of Q9 is correct but the
    citation needs editing.
    """
    pyproj = REPO_ROOT / "pyproject.toml"
    assert pyproj.exists(), "pyproject.toml missing — no manifest to verify Q9 against"
    content = pyproj.read_text(encoding="utf-8").lower()
    assert "anthropic" not in content, (
        "pyproject.toml references `anthropic` — this invalidates FAQ Q9 "
        "'交付到甲方后没有 Claude 依赖'. Remove the dep or update Q9."
    )


def test_claim_registry_nonempty():
    """Hygiene: registry must contain entries; empty registry would silently
    pass the main test and give false confidence."""
    assert len(CLAIMS) >= 10, (
        f"Too few curated claims ({len(CLAIMS)}). If pitch materials have "
        "shrunk this dramatically, confirm intentional; otherwise restore."
    )
