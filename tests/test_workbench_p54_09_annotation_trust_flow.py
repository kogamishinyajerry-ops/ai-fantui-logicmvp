"""P54-09 — annotation "trust flow" hardening (Phase A).

Three coupled fixes after deep-research on the annotation feature:

  1. **Confidence breakdown + vocabulary hint**: replace the single
     opaque % with three per-component bars (gate / signal /
     change-kind) and reveal "试试这些关键词" when a dimension came
     up empty — so engineers know how to rephrase, not guess.

  2. **localStorage draft restore**: autosave the in-flight typing
     so an accidental tab-close doesn't lose the suggestion. On
     boot, a fresh draft (< 1h) surfaces a banner offering to
     restore.

  3. **Pre-submit conflict warning**: before POST /api/proposals,
     check OPEN proposals on the same system for affected_gates
     overlap. If found, surface a yellow banner with the existing
     PROP ids + summaries; engineer must explicitly choose 继续提交
     or 取消.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from well_harness.demo_server import (
    interpret_suggestion_text,
    _normalize_llm_interpretation,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC = REPO_ROOT / "src" / "well_harness" / "static"
HTML = (STATIC / "workbench.html").read_text(encoding="utf-8")
CSS = (STATIC / "workbench.css").read_text(encoding="utf-8")
JS = (STATIC / "workbench.js").read_text(encoding="utf-8")


# ─── 1. Backend ships confidence_breakdown + vocabulary_hint ───


def test_interpret_returns_confidence_breakdown_when_full_match() -> None:
    """All three components met → all three breakdown values 1.0."""
    result = interpret_suggestion_text(
        "L1 的 SW1 判据应该 tighten 到 ≥ 50ms"
    )
    breakdown = result.get("confidence_breakdown")
    assert isinstance(breakdown, dict), "missing confidence_breakdown"
    assert breakdown.get("gate") == 1.0
    assert breakdown.get("signal") == 1.0
    assert breakdown.get("change_kind") == 1.0
    # When everything matched, vocabulary_hint should be empty —
    # no need to suggest alternatives.
    assert result.get("vocabulary_hint") == {}


def test_interpret_returns_zero_breakdown_with_hints_when_unclassified() -> None:
    """Engineer types a vague comment → no gate / signal /
    change-kind, breakdown all 0, vocabulary_hint surfaces all
    three available lists so the UI can guide them."""
    result = interpret_suggestion_text("这个面板看起来怪怪的")
    breakdown = result["confidence_breakdown"]
    assert breakdown["gate"] == 0.0
    assert breakdown["signal"] == 0.0
    assert breakdown["change_kind"] == 0.0
    hint = result["vocabulary_hint"]
    # All three dimensions empty → all three hints present.
    assert "gate" in hint and len(hint["gate"]) >= 4, "gate hint missing"
    assert "signal" in hint and len(hint["signal"]) >= 3, "signal hint missing"
    assert "change_kind" in hint and len(hint["change_kind"]) >= 3, "change-kind hint missing"
    # The gate hint must list canonical ids (L1..L4 for thrust-reverser),
    # NOT raw synonyms — synonyms are too noisy for a UI hint.
    assert "L1" in hint["gate"]
    assert "L2" in hint["gate"]


def test_interpret_partial_match_only_hints_missing_dimensions() -> None:
    """Gate detected but no signal/verb → hint only for the
    missing dimensions, not all three."""
    result = interpret_suggestion_text("L1 这里有点问题")
    bd = result["confidence_breakdown"]
    assert bd["gate"] == 1.0
    assert bd["signal"] == 0.0
    assert bd["change_kind"] == 0.0
    hint = result["vocabulary_hint"]
    assert "gate" not in hint, "gate dimension was met — no hint expected"
    assert "signal" in hint
    assert "change_kind" in hint


def test_llm_normalizer_synthesizes_breakdown_from_returned_fields() -> None:
    """The LLM doesn't emit its own breakdown — the normalizer
    derives it so the UI gets a uniform shape regardless of
    strategy."""
    raw = {
        "affected_gates": ["L1", "L3"],
        "target_signals": ["SW1"],
        "change_kind": "tighten_condition",
        "change_kind_zh": "收紧条件",
        "change_kind_en": "tighten condition",
        "confidence": 0.9,
        "summary_zh": "",
        "summary_en": "",
    }
    out = _normalize_llm_interpretation(raw, source_text="…")
    bd = out["confidence_breakdown"]
    assert bd == {"gate": 1.0, "signal": 1.0, "change_kind": 1.0}
    assert "vocabulary_hint" in out


def test_llm_normalizer_marks_change_kind_zero_when_propose_change() -> None:
    """When LLM falls through to default 'propose_change', the
    derived change_kind component is 0 — matching the rules
    interpreter's behavior."""
    raw = {
        "affected_gates": ["L1"],
        "target_signals": [],
        "change_kind": "propose_change",
        "confidence": 0.4,
    }
    out = _normalize_llm_interpretation(raw, source_text="…")
    bd = out["confidence_breakdown"]
    assert bd["gate"] == 1.0
    assert bd["signal"] == 0.0
    assert bd["change_kind"] == 0.0


# ─── 2. HTML markup carries the new surfaces ───


@pytest.mark.parametrize(
    "fragment",
    [
        # Confidence breakdown row container + 3 components
        'id="workbench-suggestion-confidence-breakdown"',
        'data-component="gate"',
        'data-component="signal"',
        'data-component="change_kind"',
        'workbench-suggestion-confidence-bar-fill',
        'id="workbench-suggestion-confidence-hint"',
        # Draft-restore banner skeleton
        'id="workbench-suggestion-draft-banner"',
        'id="workbench-suggestion-draft-restore"',
        'id="workbench-suggestion-draft-dismiss"',
        # Pre-submit conflict banner skeleton
        'id="workbench-suggestion-conflict-banner"',
        'id="workbench-suggestion-conflict-list"',
        'id="workbench-suggestion-conflict-proceed"',
        'id="workbench-suggestion-conflict-cancel"',
    ],
)
def test_workbench_html_contains_p54_09_surfaces(fragment: str) -> None:
    assert fragment in HTML, f"missing P54-09 markup: {fragment}"


def test_draft_banner_starts_hidden() -> None:
    """The banner must boot hidden — JS un-hides it only when
    a fresh draft is found in localStorage."""
    block = re.search(
        r'id="workbench-suggestion-draft-banner"[^>]*>',
        HTML,
    )
    assert block is not None
    assert "hidden" in block.group(0), "draft banner must boot hidden"


def test_conflict_banner_starts_hidden() -> None:
    block = re.search(
        r'id="workbench-suggestion-conflict-banner"[^>]*>',
        HTML,
    )
    assert block is not None
    assert "hidden" in block.group(0), "conflict banner must boot hidden"


# ─── 3. CSS styles the new components ───


@pytest.mark.parametrize(
    "selector",
    [
        ".workbench-suggestion-confidence-breakdown",
        ".workbench-suggestion-confidence-bar",
        ".workbench-suggestion-confidence-bar-fill",
        ".workbench-suggestion-confidence-hint",
        ".workbench-suggestion-draft-banner",
        ".workbench-suggestion-conflict-banner",
        ".workbench-suggestion-conflict-list",
    ],
)
def test_css_carries_p54_09_rules(selector: str) -> None:
    assert selector in CSS, f"missing CSS rule: {selector}"


def test_breakdown_bar_uses_accent_token() -> None:
    """The fill of a met dimension must derive from the accent
    token (cohesive with the rest of the workbench palette)."""
    rule = re.search(
        r'\.workbench-suggestion-confidence-bar-fill\s*\{[^}]+\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "var(--accent" in body, "fill must use --accent token"


def test_unmet_dimension_styled_distinctly_from_met() -> None:
    """When a dimension is unmet (data-met='false'), the bar
    fill must show a different color (red-ish) so the engineer
    instantly sees which dimension dragged the score down."""
    rule = re.search(
        r'\.workbench-suggestion-confidence-row\[data-met="false"\][^{]*'
        r'\.workbench-suggestion-confidence-bar-fill\s*\{[^}]+\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None, "missing :unmet rule for the bar fill"


# ─── 4. JS wires the three flows ───


def test_js_renders_breakdown_from_response() -> None:
    """The render fn must read interpretation.confidence_breakdown
    + vocabulary_hint and update the DOM."""
    assert "renderConfidenceBreakdown" in JS
    assert "confidence_breakdown" in JS
    assert "vocabulary_hint" in JS


def test_js_implements_draft_autosave_with_localstorage() -> None:
    """Draft persistence must use localStorage (NOT sessionStorage)
    so the draft survives a tab close — and must be debounced so
    every keystroke doesn't trigger a write."""
    assert "installSuggestionDraftRestore" in JS
    assert "localStorage" in JS
    assert "SUGGESTION_DRAFT_KEY" in JS
    assert "SUGGESTION_DRAFT_TTL_MS" in JS
    assert "SUGGESTION_DRAFT_DEBOUNCE_MS" in JS
    # Draft is cleared on successful submit so the next session
    # starts clean.
    assert "clearSuggestionDraft" in JS


def test_js_clears_draft_on_successful_submit() -> None:
    """submitSuggestionTicket's success branch must clear the
    autosaved draft — otherwise the next page load surfaces a
    stale banner offering to 'restore' something already shipped."""
    submit_fn = re.search(
        r'async function submitSuggestionTicket\([^)]*\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert submit_fn is not None
    body = submit_fn.group(1)
    assert "clearSuggestionDraft" in body, (
        "submit-success branch must clear the autosaved draft"
    )


# ─── 5. Codex round-1 fixes (P2-1 / P2-2 / P3) ──────────────────────


def test_drafts_are_scoped_by_system_id() -> None:
    """Codex P2-1: drafts must be keyed by system_id so a draft
    typed on thrust-reverser cannot be restored under C919 (which
    would mis-route the resulting proposal). The v2 storage shape
    is a map keyed by system_id; each entry carries its own ts."""
    # Storage key bumped from v1 → v2 to invalidate any pre-fix
    # global drafts (otherwise a returning user with a stale v1
    # draft would still see the unsafe behavior once).
    assert "workbench/suggestion-drafts/v2" in JS, (
        "draft storage must be the v2 (per-system) layout"
    )
    # The read path must consult the active system select.
    assert "_currentDraftSystemId" in JS
    # Save + clear paths must operate on the system-keyed map.
    assert "_readDraftMap" in JS and "_writeDraftMap" in JS


def test_clear_draft_only_clears_active_systems_entry() -> None:
    """clearSuggestionDraft must NOT wipe drafts belonging to
    other systems — submitting a thrust-reverser ticket should
    leave the engineer's in-flight C919 draft alone."""
    fn = re.search(
        r'function clearSuggestionDraft\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "_readDraftMap" in body
    assert "_writeDraftMap" in body
    # Must NOT just removeItem the whole key.
    assert "removeItem(SUGGESTION_DRAFT_KEY)" not in body, (
        "clearSuggestionDraft must not nuke the entire draft map"
    )


def test_draft_banner_re_evaluates_on_system_switch() -> None:
    """Switching the system mid-session must hide any stale banner
    and re-check whether the new system has its own draft."""
    install_fn = re.search(
        r'function installSuggestionDraftRestore\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert install_fn is not None
    body = install_fn.group(1)
    assert "workbench-system-select" in body, (
        "draft installer must listen to the system-select change event"
    )
    assert "hideDraftBanner" in body


def test_llm_normalizer_synthesizes_vocabulary_hint_when_dimension_empty() -> None:
    """Codex P2-2: AI-mode users must also get the rephrasing
    guidance when the LLM misses a dimension — previously
    _normalize_llm_interpretation hardcoded an empty hint object."""
    raw = {
        "affected_gates": [],
        "target_signals": [],
        "change_kind": "propose_change",
        "confidence": 0.2,
    }
    out = _normalize_llm_interpretation(
        raw, source_text="vague", system_id="thrust-reverser"
    )
    hint = out["vocabulary_hint"]
    # All three dimensions empty → hints for all three.
    assert "gate" in hint and "L1" in hint["gate"]
    assert "signal" in hint and len(hint["signal"]) >= 3
    assert "change_kind" in hint and len(hint["change_kind"]) >= 3
    # Sanity: the breakdown is also correctly synthesized.
    assert out["confidence_breakdown"]["gate"] == 0.0


def test_llm_normalizer_uses_per_system_vocab() -> None:
    """The synthesized hint must respect the active system_id —
    asking for a C919 hint mustn't return thrust-reverser's
    L1..L4 list (different vocab)."""
    raw = {
        "affected_gates": [],
        "target_signals": [],
        "change_kind": "propose_change",
        "confidence": 0.0,
    }
    out_tr = _normalize_llm_interpretation(
        raw, source_text="x", system_id="thrust-reverser"
    )
    out_c919 = _normalize_llm_interpretation(
        raw, source_text="x", system_id="c919-etras"
    )
    # The two systems' gate vocabs differ — the synthesized hints
    # must reflect that.
    assert out_tr["vocabulary_hint"]["gate"] != out_c919["vocabulary_hint"]["gate"]


def test_draft_debounce_captures_system_at_input_time() -> None:
    """Codex round-2 P2-1: the debounce callback must write under
    the system_id snapshotted when the user was typing, not
    whatever system is active when the timer fires. Otherwise
    typing on system A then switching to B inside 500ms commits
    A's text under B."""
    # The fix is a saveSuggestionDraftFor(sysId, text) helper +
    # capturing the snapshot in the input listener.
    assert "saveSuggestionDraftFor" in JS, (
        "explicit-system save helper must exist"
    )
    install_fn = re.search(
        r'function installSuggestionDraftRestore\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert install_fn is not None
    body = install_fn.group(1)
    # Snapshot vars captured outside the timer.
    assert "sysSnapshot" in body
    assert "textSnapshot" in body
    # The setTimeout body must use the snapshot, not re-read.
    assert "saveSuggestionDraftFor(sysSnapshot, textSnapshot)" in body
    # System change must also cancel the pending debounce so the
    # old text can't land under the new system after the fact.
    assert "_suggestionDraftTimer = null" in body


def test_clearSuggestionDraft_cancels_pending_debounce() -> None:
    """Codex round-3 P2-1: a pending autosave debounce must be
    canceled before clearSuggestionDraft removes the entry —
    otherwise typing→submit within 500ms lets the timer fire after
    the delete and resurrect the just-submitted text."""
    fn = re.search(
        r'function clearSuggestionDraft\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "clearTimeout(_suggestionDraftTimer)" in body, (
        "clearSuggestionDraft must cancel any pending debounce"
    )


def test_onConfirmClicked_discards_stale_conflict_responses() -> None:
    """Codex round-3 P2-2: the conflict-check fetch is async; if
    the user re-interprets while it's in flight, the stale response
    must be dropped (snapshot identity check). Otherwise the banner
    would describe the OLD gates while 继续提交 would POST the NEW
    interpretation."""
    fn = re.search(
        r'async function onConfirmClicked\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    # Snapshot variable captured at request-start.
    assert "const snapshot = _lastInterpretation" in body, (
        "must snapshot _lastInterpretation at request-start"
    )
    # Identity check after each await — drop stale results.
    # We expect at least one explicit guard.
    assert "_lastInterpretation !== snapshot" in body


def test_runSuggestionInterpret_clears_stale_conflict_banner() -> None:
    """Codex round-2 P2-2: re-interpreting must hide any banner
    from a prior conflict check. Otherwise the banner's 继续提交
    would submit the NEW interpretation against the OLD displayed
    conflict list — misleading the user."""
    fn = re.search(
        r'async function runSuggestionInterpret\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "hideConflictBanner" in body, (
        "runSuggestionInterpret must tear down any stale conflict banner"
    )


def test_llm_normalizer_drops_hallucinated_gate_ids() -> None:
    """Codex round-4 P2-1: LLM may hallucinate non-canonical gate
    ids (e.g. L99). They must be filtered before scoring — otherwise
    breakdown scores 100% on a value the SVG has no anchor for."""
    raw = {
        "affected_gates": ["L1", "L99", "BOGUS"],
        "target_signals": ["SW1", "TOTALLY_FAKE"],
        "change_kind": "tighten_condition",
        "confidence": 0.9,
    }
    out = _normalize_llm_interpretation(
        raw, source_text="x", system_id="thrust-reverser"
    )
    assert out["affected_gates"] == ["L1"], (
        "non-canonical gate ids must be dropped"
    )
    assert "TOTALLY_FAKE" not in out["target_signals"]
    assert "BOGUS" not in out["affected_gates"]


def test_llm_normalizer_falls_back_unknown_change_kind() -> None:
    """If LLM returns a change_kind outside our taxonomy, treat
    it as the propose_change fallback so breakdown reflects
    'no recognized verb' rather than 100% on a phantom code."""
    raw = {
        "affected_gates": ["L1"],
        "target_signals": [],
        "change_kind": "totally_made_up_verb",
        "confidence": 0.5,
    }
    out = _normalize_llm_interpretation(
        raw, source_text="x", system_id="thrust-reverser"
    )
    assert out["change_kind"] == "propose_change"
    assert out["confidence_breakdown"]["change_kind"] == 0.0
    # And the fallback now triggers the change_kind hint.
    assert "change_kind" in out["vocabulary_hint"]


def test_onConfirmClicked_snapshots_system_id() -> None:
    """Codex round-4 P2-2: must snapshot system_id in addition to
    interpretation, AND pass the snapshot into submitSuggestionTicket
    so a system toggle between confirm and POST can't reroute the
    proposal."""
    fn = re.search(
        r'async function onConfirmClicked\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "_currentSystemFromSelect()" in body, (
        "must use a system snapshot helper"
    )
    # The snapshot is passed downstream.
    assert "submitSuggestionTicket(systemId)" in body


def test_submitSuggestionTicket_accepts_system_override() -> None:
    """The submit fn must take an optional system_id arg and
    prefer it over the live dropdown when provided."""
    fn = re.search(
        r'async function submitSuggestionTicket\((.*?)\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    args = fn.group(1).strip()
    body = fn.group(2)
    assert args, "submitSuggestionTicket must accept an arg"
    assert "systemIdOverride" in args
    assert "systemIdOverride" in body


def test_conflict_banner_proceed_uses_snapshot_system() -> None:
    """The 继续提交 button must read the system snapshot stashed on
    the banner and pass it to submitSuggestionTicket — so the user
    can't sneak a different system_id between confirmation and
    final submit."""
    assert "data-system-snapshot" in JS, (
        "banner must persist the snapshot system_id"
    )
    install_fn = re.search(
        r'function installSuggestionFlow\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert install_fn is not None
    body = install_fn.group(1)
    assert "data-system-snapshot" in body
    assert "submitSuggestionTicket(sysId" in body


def test_input_listener_hides_stale_draft_banner() -> None:
    """Codex round-4 P3: once the textarea becomes dirty, the
    restore banner must hide — its preview no longer matches the
    saved draft, and pressing 恢复 / 忽略 in the stale banner would
    overwrite or delete the wrong content."""
    install_fn = re.search(
        r'function installSuggestionDraftRestore\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert install_fn is not None
    body = install_fn.group(1)
    # Find the input listener.
    listener = re.search(
        r'input\.addEventListener\("input", \(\) => \{(.*?)\}\);',
        body,
        re.DOTALL,
    )
    assert listener is not None
    listener_body = listener.group(1)
    assert "hideDraftBanner" in listener_body, (
        "input listener must hide draft banner once input is dirty"
    )


def test_change_kind_hint_excludes_propose_change_fallback() -> None:
    """Codex P3: the verb hint must NOT advertise "propose change"
    as a remedy — that's the very fallback that triggered the hint
    (zero-confidence dimension). The earlier comprehension filtered
    on the Chinese label by mistake; the fix uses the code field."""
    result = interpret_suggestion_text("这个面板看起来怪怪的")
    verbs = result["vocabulary_hint"]["change_kind"]
    # Codex's P3 finding: the previous list contained "propose change".
    assert "propose change" not in [v.lower() for v in verbs], (
        f"vocabulary_hint must not suggest the fallback verb; got {verbs!r}"
    )
    # Sanity: real verbs are still in the list.
    lowered = [v.lower() for v in verbs]
    assert any("tighten" in v for v in lowered) or any("loosen" in v for v in lowered)


def test_js_runs_conflict_check_before_post() -> None:
    """The confirm-button handler must be onConfirmClicked, and it
    must fetch /api/proposals?status=OPEN&system=... before
    POSTing — only call submitSuggestionTicket when 0 overlaps."""
    assert "onConfirmClicked" in JS
    # The check only runs when affected_gates is non-empty.
    assert (
        "affected_gates" in JS and "showConflictBanner" in JS
    )
    # Network failure or empty conflict list → fall through to
    # submitSuggestionTicket (best-effort, never block).
    confirm_fn = re.search(
        r'async function onConfirmClicked\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert confirm_fn is not None
    body = confirm_fn.group(1)
    assert "submitSuggestionTicket" in body
    assert "PROPOSALS_PATH" in body
    assert "status=OPEN" in body


def test_js_conflict_banner_lists_overlapping_proposals() -> None:
    """The banner UI must render id + summary + gates per
    conflicting proposal so the engineer knows what's competing."""
    assert "showConflictBanner" in JS
    assert "hideConflictBanner" in JS
    # Banner closes on Cancel + on full clearSuggestionInterpretation.
    clear_fn = re.search(
        r'function clearSuggestionInterpretation\(\) \{(.*?)^}',
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert clear_fn is not None
    assert "hideConflictBanner" in clear_fn.group(1), (
        "clearSuggestionInterpretation must also tear down the conflict banner"
    )
