"""P26 · pitch citation verifier.

Parse立项 materials (pitch_script / faq / preflight / disaster_runbook /
local_model_poc / wow_a_b_c cards / integrated-timing-findings) and verify
every path citation resolves to a real file/directory on disk. Catches
broken evidence links before pitch day.

Non-goals:
  - Do not modify any pitch material
  - Do not validate content semantics (we only verify paths exist)
  - Do not enforce test-count claims ("658 passed") — numeric claims rot
    naturally and failing CI on "658 → 659" is noise

Extraction rules:
  - Match paths with required extension (.py/.md/.json/.yaml/.css/.html/.tar/.gz)
    or directory references ending with `/`
  - Skip placeholders containing `<`, `>`, `*`, `{`, `}` or all-caps N
  - Paths may be wrapped in backticks or appear inline
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Pitch materials to scan (in priority order).
PITCH_DOCS = [
    "docs/demo/pitch_script.md",
    "docs/demo/faq.md",
    "docs/demo/preflight_checklist.md",
    "docs/demo/disaster_runbook.md",
    "docs/demo/local_model_poc.md",
    "docs/demo/wow_a_causal_chain.md",
    "docs/demo/wow_b_monte_carlo.md",
    "docs/demo/wow_c_reverse_diagnose.md",
    "docs/demo/integrated-timing-findings.md",
]

# Allowed path roots — citations must start with one of these
PATH_ROOTS = (
    "src/", "tests/", "scripts/", "runs/", "docs/",
    "config/", "data/", ".planning/", "archive/",
)

# Match: optional backtick + root + path + (optional line/func suffix)
# End on whitespace, backtick, paren close, quote, or common MD punctuation
# Require either an extension (.<ext>) or a trailing slash.
# Valid extensions we see in pitch materials:
EXT_RE = r"(?:\.py|\.md|\.json|\.yaml|\.yml|\.css|\.html|\.tar|\.gz|\.sha256|\.txt|\.log)"

# Anchor: root prefix must not be preceded by another path-like char (prevents
# matching `src/` inside a longer path like `archive/shelved/.../src/foo.py`).
CITATION_RE = re.compile(
    r"(?<![A-Za-z0-9_./\-])"                    # left boundary: no path char
    r"`?"                                       # optional leading backtick
    r"((?:src|tests|scripts|runs|docs|config|data|\.planning|archive)"
    r"/[A-Za-z0-9_./\-]+"                       # body
    rf"(?:{EXT_RE}|/))"                          # extension or trailing slash
    r"(?::\d+)?"                                # optional :line
    r"(?:::[A-Za-z_][\w]*)?"                    # optional ::func
    r"`?"                                       # optional trailing backtick
)


def _has_placeholder(path: str) -> bool:
    """Placeholder markers — not a real path, skip."""
    return any(ch in path for ch in ("<", ">", "*", "{", "}"))


def _extract_citations(text: str) -> set[str]:
    """Return unique path citations from markdown text."""
    cites = set()
    for match in CITATION_RE.finditer(text):
        path = match.group(1)
        if _has_placeholder(path):
            continue
        # Directory-only matches (trailing `/`) whose next char is a placeholder
        # marker belong to a placeholder citation like `config/hardware/<system>.yaml`.
        if path.endswith("/"):
            tail = text[match.end():match.end() + 1]
            if tail in ("<", "{", "*"):
                continue
        # Trim trailing punctuation that regex may have eaten
        path = path.rstrip(").,;:")
        cites.add(path)
    return cites


def _resolve(path: str) -> Path:
    """Resolve a citation against repo root. Strip any :line or ::func."""
    p = path.split("::", 1)[0].split(":", 1)[0] if ":" in path else path
    return REPO_ROOT / p


def test_pitch_materials_exist():
    """All pitch material files must exist (meta-check)."""
    missing = [d for d in PITCH_DOCS if not (REPO_ROOT / d).exists()]
    assert not missing, f"Pitch material files missing from repo: {missing}"


def test_pitch_citations_resolve():
    """Every path citation in pitch materials must resolve on disk.

    If this test fails, inspect the printed FAIL list — each entry shows
    the source doc and the broken citation. Fix by either updating the
    citation or committing the referenced artefact.
    """
    failures: list[tuple[str, str]] = []
    citation_count = 0

    for doc_rel in PITCH_DOCS:
        doc = REPO_ROOT / doc_rel
        if not doc.exists():
            continue  # meta-check covers this
        text = doc.read_text(encoding="utf-8")
        cites = _extract_citations(text)
        for c in sorted(cites):
            citation_count += 1
            target = _resolve(c)
            if not target.exists():
                failures.append((doc_rel, c))

    # Assert with detail
    if failures:
        lines = [f"{src}: {cite}" for src, cite in failures]
        msg = (
            f"\n{len(failures)} broken citation(s) of {citation_count} total:\n  "
            + "\n  ".join(lines)
        )
        raise AssertionError(msg)

    # Positive assertion — at least one citation found (guards against regex
    # regression silently reporting zero references)
    assert citation_count >= 50, (
        f"Too few citations extracted ({citation_count}) — "
        f"regex may have regressed; pitch materials normally contain 50+."
    )


def test_placeholder_skip_works():
    """Regex hygiene — placeholder strings must not register as real citations."""
    sample = (
        "See `runs/<ts>/wow_a_timeline.json` for an example, and "
        "`config/hardware/<system>.yaml` for schema."
    )
    cites = _extract_citations(sample)
    # Both contain placeholder markers — should be skipped
    assert not cites, f"Placeholders should be skipped but got: {cites}"


def test_real_path_extraction_works():
    """Regex hygiene — real paths must be extracted."""
    sample = (
        "See `src/well_harness/controller.py` (line 42) and "
        "runs/dress_rehearsal_20260418T063146Z/wow_a_timeline.json for the artefact."
    )
    cites = _extract_citations(sample)
    assert "src/well_harness/controller.py" in cites
    assert "runs/dress_rehearsal_20260418T063146Z/wow_a_timeline.json" in cites
