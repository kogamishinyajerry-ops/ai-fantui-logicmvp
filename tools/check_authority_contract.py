#!/usr/bin/env python3
"""P43 Authority Contract Checker — R1-R6 mechanical compliance.

Usage:
    python tools/check_authority_contract.py           # check all rules
    python tools/check_authority_contract.py --rule R3 # check one rule
    python tools/check_authority_contract.py --json    # machine-readable output

Exit codes: 0 = all checked rules pass · 1 = ≥1 rule fails · 2 = file not found
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_WORKBENCH_JS = _REPO / "src" / "well_harness" / "static" / "workbench.js"
_WORKBENCH_PY = _REPO / "src" / "well_harness" / "workbench_bundle.py"
_DEMO_SERVER   = _REPO / "src" / "well_harness" / "demo_server.py"
_GENERATOR_PY  = _REPO / "src" / "well_harness" / "tools" / "generate_adapter.py"


# ──────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────

def _read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"required file missing: {path}")
    return path.read_text(encoding="utf-8")


def _grep_count(text: str, pattern: str, flags: int = 0) -> int:
    return len(re.findall(pattern, text, flags))


def _grep_lines(text: str, pattern: str, flags: int = 0) -> list[int]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(pattern, line, flags):
            out.append(i)
    return out


def _extract_block(text: str, start_pattern: str, max_lines: int = 80) -> str:
    """Return up to max_lines starting from first match of start_pattern."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(start_pattern, line):
            return "\n".join(lines[i : i + max_lines])
    return ""


# ──────────────────────────────────────────────
# rule checkers
# ──────────────────────────────────────────────

def check_r1(js: str, py_demo: str) -> dict:
    """R1: Only UI writes draft_design_state; Python backend never writes.

    Scans demo_server.py AND all *.py under src/well_harness/ (excl. static assets).
    """
    bad_patterns = [r"draft_design_state", r"draftDesignState"]
    backend_hits: list[str] = []

    # demo_server.py (passed in from caller)
    for pat in bad_patterns:
        lines = _grep_lines(py_demo, pat)
        if lines:
            backend_hits.append(f"  demo_server.py:{lines} pattern='{pat}'")

    # All other Python files under src/well_harness/ (wide backend scan)
    well_harness = _REPO / "src" / "well_harness"
    if well_harness.exists():
        for py_file in sorted(well_harness.rglob("*.py")):
            # Skip static asset directories (not Python logic)
            if "static" in py_file.parts:
                continue
            # workbench_bundle.py is separately governed by R6
            if py_file.name == "workbench_bundle.py":
                continue
            # demo_server.py already scanned above
            if py_file.name == "demo_server.py":
                continue
            try:
                text = py_file.read_text(encoding="utf-8")
            except Exception:
                continue
            for pat in bad_patterns:
                hits = _grep_lines(text, pat)
                if hits:
                    rel = py_file.relative_to(_REPO)
                    backend_hits.append(f"  {rel}:{hits} pattern='{pat}'")

    status = "PASS" if not backend_hits else "FAIL"
    return {
        "rule": "R1",
        "title": "Only UI writes draft_design_state; backend never writes",
        "status": status,
        "detail": backend_hits or ["src/well_harness/**/*.py: 0 occurrences of draft_design_state — compliant"],
    }


def check_r2(js: str) -> dict:
    """R2: final_approve handler never READs draft_design_state."""
    # Find final-approve handler block
    block = _extract_block(js, r"final.approve|finalApprove|Final Approval|handleFinalApprove")
    if not block:
        return {
            "rule": "R2",
            "title": "final_approve handler does not read draft_design_state",
            "status": "MISSING",
            "detail": ["final_approve handler not yet implemented (expected: P43-08)"],
        }
    # Only flag actual value-reads, not removeItem (which is R6 compliance, not a violation)
    read_patterns = [
        r"getItem\([^)]*(?:draft_design_state|draftDesignState)",
        r"JSON\.parse[^;]*(?:draft_design_state|draftDesignState)",
    ]
    bad: list[str] = []
    for pat in read_patterns:
        if re.search(pat, block):
            bad.append(f"  READ pattern found in final_approve block: '{pat}'")
    status = "PASS" if not bad else "FAIL"
    return {
        "rule": "R2",
        "title": "final_approve handler does not read draft_design_state",
        "status": status,
        "detail": bad or ["No draft READ patterns in final_approve block — compliant"],
    }


def check_r3(js: str) -> dict:
    """R3: frozenSpec only via assignFrozenSpec+deepFreeze; no bare writes; no alias-mutate."""
    issues: list[str] = []
    missing: list[str] = []

    # Must exist
    if not re.search(r"function assignFrozenSpec|assignFrozenSpec\s*=", js):
        missing.append("assignFrozenSpec declaration MISSING")
    if not re.search(r"function deepFreeze|const deepFreeze\s*=|var deepFreeze\s*=", js):
        missing.append("deepFreeze declaration MISSING")

    # Must NOT exist bare writes outside assignFrozenSpec body
    # Exclude variable declarations (let/const/var frozenSpec = ...) — those are not writes
    _js_lines = js.splitlines()
    all_bare = [
        ln for ln in _grep_lines(js, r"frozenSpec\s*=(?!=)")
        if not re.search(r"\b(?:let|const|var)\s+frozenSpec\b", _js_lines[ln - 1])
    ]
    if all_bare:
        assign_block = _extract_block(
            js, r"(?:function\s+assignFrozenSpec|\bassignFrozenSpec\s*=\s*(?:function|\())", max_lines=20
        )
        authorized_count = len(re.findall(r"frozenSpec\s*=(?!=)", assign_block)) if assign_block else 0
        unauthorized = len(all_bare) - authorized_count
        if unauthorized > 0:
            issues.append(
                f"  bare frozenSpec= at {len(all_bare)} site(s); "
                f"{authorized_count} inside assignFrozenSpec (authorized); "
                f"{unauthorized} unauthorized"
            )

    # Must NOT exist (alias mutate patterns)
    forbidden = [
        r"frozenSpec\.merge\(",
        r"frozenSpec\.assign\(",
        r"Object\.assign\(frozenSpec",
        r"\{\.\.\.frozenSpec,\s*\.\.\.draft",
        r"\{\.\.\.frozenSpec,\s*\.\.\.draftDesign",
    ]
    for pat in forbidden:
        if re.search(pat, js):
            issues.append(f"  forbidden mutation pattern: '{pat}'")

    if missing:
        return {
            "rule": "R3",
            "title": "frozenSpec controlled via assignFrozenSpec+deepFreeze only",
            "status": "MISSING",
            "detail": missing + issues,
        }
    status = "PASS" if not issues else "FAIL"
    return {
        "rule": "R3",
        "title": "frozenSpec controlled via assignFrozenSpec+deepFreeze only",
        "status": status,
        "detail": issues or ["assignFrozenSpec+deepFreeze present; no bare writes; no alias-mutate — compliant"],
    }


def check_r4(js: str) -> dict:
    """R4: Generator reads frozenSpec only, never draft_design_state (JS handler + Python generator)."""
    issues: list[str] = []
    missing: list[str] = []

    # JS handler check
    gen_block = _extract_block(js, r"start_gen|generatePanel|runGeneration|handleStartGen")
    if not gen_block:
        missing.append("JS generator handler not yet implemented (expected: P43-05/06)")
    else:
        for pat in [r"draft_design_state", r"draftDesignState"]:
            if re.search(pat, gen_block):
                issues.append(f"  JS generator block reads draft pattern: '{pat}'")

    # Python generator check (generate_adapter.py is the authoritative backend generator)
    if _GENERATOR_PY.exists():
        py_gen = _GENERATOR_PY.read_text(encoding="utf-8")
        for pat in [r"draft_design_state", r"draftDesignState"]:
            lines = _grep_lines(py_gen, pat)
            if lines:
                issues.append(f"  generate_adapter.py:{lines} reads draft pattern '{pat}'")

    if issues:
        return {
            "rule": "R4",
            "title": "Generator reads frozenSpec only, never draft",
            "status": "FAIL",
            "detail": issues + missing,
        }
    if missing:
        return {
            "rule": "R4",
            "title": "Generator reads frozenSpec only, never draft",
            "status": "MISSING",
            "detail": missing,
        }
    return {
        "rule": "R4",
        "title": "Generator reads frozenSpec only, never draft",
        "status": "PASS",
        "detail": ["No draft reads in JS generator block or generate_adapter.py — compliant"],
    }


def check_r5(js: str) -> dict:
    """R5: validateDraftAgainstFrozen singleton exists only in workbench.js."""
    count_js = _grep_count(js, r"validateDraftAgainstFrozen")
    if count_js == 0:
        return {
            "rule": "R5",
            "title": "validateDraftAgainstFrozen singleton in workbench.js",
            "status": "MISSING",
            "detail": ["validateDraftAgainstFrozen not yet implemented (expected: P43-07)"],
        }
    # count_js > 0 means at least one reference — but we require exactly one *declaration*
    decl_count = _grep_count(js, r"function validateDraftAgainstFrozen|validateDraftAgainstFrozen\s*=")
    issues: list[str] = []
    if decl_count == 0:
        issues.append(
            f"  validateDraftAgainstFrozen referenced {count_js}× but no declaration found — must be a declared singleton"
        )
    elif decl_count > 1:
        issues.append(f"  validateDraftAgainstFrozen declared {decl_count} times — must be singleton (exactly 1)")
    status = "PASS" if not issues else "FAIL"
    return {
        "rule": "R5",
        "title": "validateDraftAgainstFrozen singleton in workbench.js",
        "status": status,
        "detail": issues or [f"validateDraftAgainstFrozen: 1 declaration, {count_js} reference(s) — compliant"],
    }


def check_r6(js: str, py_bundle: str) -> dict:
    """R6: final_approve deletes draft immediately; archive never contains draft."""
    issues: list[str] = []
    missing: list[str] = []

    # Approval handler must removeItem draft
    approve_block = _extract_block(js, r"final.approve|finalApprove|Final Approval|handleFinalApprove")
    if not approve_block:
        missing.append("final_approve handler MISSING — removeItem(draft) unverifiable (expected: P43-08)")
    else:
        # Accept either the inline removeItem call or the clearDraftDesignState() wrapper (both are compliant)
        if not re.search(
            r"(?:localStorage\.removeItem\([^)]*(?:draft_design_state|draftDesignState)[^)]*\)"
            r"|clearDraftDesignState\(\))",
            approve_block,
        ):
            issues.append("  final_approve block: neither localStorage.removeItem(draft_design_state) nor clearDraftDesignState() found")

    # Archive bundle must not contain draft keys
    for pat in [r"draft_design_state", r"draftDesignState"]:
        lines = _grep_lines(py_bundle, pat)
        if lines:
            issues.append(f"  workbench_bundle.py:{lines} contains draft pattern '{pat}'")

    if missing and not issues:
        return {
            "rule": "R6",
            "title": "final_approve deletes draft; archive excludes draft",
            "status": "MISSING",
            "detail": missing,
        }
    if issues:
        return {
            "rule": "R6",
            "title": "final_approve deletes draft; archive excludes draft",
            "status": "FAIL",
            "detail": issues + missing,
        }
    return {
        "rule": "R6",
        "title": "final_approve deletes draft; archive excludes draft",
        "status": "PASS",
        "detail": ["archive bundle: 0 draft references — compliant"] + missing,
    }


# ──────────────────────────────────────────────
# main
# ──────────────────────────────────────────────

_CHECKERS = {
    "R1": lambda js, py_b, py_d: check_r1(js, py_d),
    "R2": lambda js, py_b, py_d: check_r2(js),
    "R3": lambda js, py_b, py_d: check_r3(js),
    "R4": lambda js, py_b, py_d: check_r4(js),
    "R5": lambda js, py_b, py_d: check_r5(js),
    "R6": lambda js, py_b, py_d: check_r6(js, py_b),
}

_STATUS_ICON = {"PASS": "✓", "FAIL": "✗", "MISSING": "?"}


def run(rules: list[str], as_json: bool = False) -> int:
    try:
        js = _read(_WORKBENCH_JS)
        py_b = _read(_WORKBENCH_PY)
        py_d = _read(_DEMO_SERVER)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    results = []
    for rule in rules:
        checker = _CHECKERS[rule]
        results.append(checker(js, py_b, py_d))

    if as_json:
        print(json.dumps(results, indent=2))
    else:
        print("P43 Authority Contract Check")
        print("=" * 50)
        for r in results:
            icon = _STATUS_ICON.get(r["status"], "?")
            print(f"\n[{r['status']:7s}] {icon} {r['rule']}: {r['title']}")
            for line in r["detail"]:
                print(f"         {line}")
        print("\n" + "=" * 50)
        statuses = [r["status"] for r in results]
        n_pass = statuses.count("PASS")
        n_fail = statuses.count("FAIL")
        n_missing = statuses.count("MISSING")
        print(f"PASS={n_pass}  FAIL={n_fail}  MISSING={n_missing} (not-yet-implemented)")
        if n_fail:
            print("VERDICT: ✗ FAIL — authority contract violated")
        elif n_missing:
            print("VERDICT: ? PARTIAL — no violations found; some rules not yet implemented")
        else:
            print("VERDICT: ✓ PASS — all rules satisfied")

    return 1 if any(r["status"] == "FAIL" for r in results) else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="P43 authority contract checker")
    parser.add_argument("--rule", choices=list(_CHECKERS), help="check one rule only")
    parser.add_argument("--json", action="store_true", dest="as_json", help="JSON output")
    args = parser.parse_args()
    rules = [args.rule] if args.rule else list(_CHECKERS)
    sys.exit(run(rules, as_json=args.as_json))


if __name__ == "__main__":
    main()
