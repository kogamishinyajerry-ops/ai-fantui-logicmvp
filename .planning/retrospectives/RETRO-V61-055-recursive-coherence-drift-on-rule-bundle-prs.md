# RETRO-V61-055 · Recursive coherence drift on rule-bundle PRs

> **Date:** 2026-04-25
> **Trigger:** governance bundle #2 (PR #14) ran 6 Codex rounds — well past v6.1 Hard Stop (≥4 rounds = governance failure).
> **Same arc as:** v2.3 UI-COPY-PROBE legislation PR (PR #11, 5 rounds), captured upstream in RETRO-V61-054 §5b/§6.5 as a candidate methodology lesson.
> **Status:** Methodology rule. Adopt for ALL future governance/rule-bundle PRs in this repo.

---

## 1. Pattern recognition

Rule-bundle PRs (governance changes that touch constitution.md + RETRO + at-least-1 phase plan) consistently exhibit a recursive coherence drift loop:

1. R1 catches structural finding (BLOCKER or IMPORTANT)
2. Author rewrites the rule in N spots to fix the structural issue
3. R2 catches that the N rewrites produced N slightly-different paraphrases
4. Author "converges" by editing N spots to be more similar
5. R3 catches that "more similar" still has fragments diverging
6. ... repeat until R5–R6, by which point Codex is finding rule fragments in changelog narratives, RETRO history sections, and README operational mechanisms — places that are NOT structural rule-body but contain rule-shaped sentences

**Two confirmed instances:**
- PR #11 (v2.3 UI-COPY-PROBE birth): 5 rounds. Captured in RETRO-V61-054.
- PR #14 (governance bundle #2): 6 rounds. Captured here.

The actual *legislative output* of both PRs was correct from R1. All 6 (and 5) rounds re-litigated *cross-doc references* to that output, not the output itself.

---

## 2. Root cause

Two compounding factors:

### 2.1 Spec-coherence-as-fractal trap
Codex (gpt-5.4) reviewing for spec coherence finds drift at every zoom level:
- R1 zoom: sections disagree
- R2 zoom: paragraphs in same section disagree
- R3 zoom: sentences in same paragraph disagree
- R4 zoom: clauses within same sentence disagree
- R5 zoom: word choice in synonymous clauses disagree

There is no natural stopping point. Coherence is asymptotic; perfect convergence is a fixed-point that may not be reachable in finite rounds because each rewrite introduces new surface.

### 2.2 Author overpromise compounds with Codex literalism
Author commit messages claim ambitious convergence ("3 spots verbatim identical", "canonical-pointer pattern", "1 canonical + N pointers"). Codex grades against the literal claim. When the claim is achievable only at a deeper purity level than was actually achieved, Codex flags drift on the gap between claimed and delivered.

---

## 3. Methodology rule (adopt going forward)

### 3.1 Single-canonical-source declaration before R1

For any rule-bundle PR, the PR description MUST explicitly declare:
- **Canonical home**: exactly one file:section that owns the rule body (e.g., `constitution.md §Codex Persona Pipeline Tier-Trigger`)
- **Pointer policy**: every other reference is a pure pointer (file:section name + ≤1 sentence purpose). No rule restatement.
- **Allowed-restatement zones**: explicitly enumerate which docs/sections are allowed to contain rule-shaped content because they own that operational view (e.g., README §命令模板 = bash implementation, README §Anti-bias safeguard = mechanism documentation, RETRO §6.x = decision-arc history). These zones are NOT drift; they are by-design operational/historical content.

Without this declaration, Codex has no way to distinguish "rule body" from "operational documentation" from "changelog narrative", and will flag everything that contains rule-shaped sentences.

### 3.2 Hard-stop at R3 with structural escalation

**v6.1 amendment**: ≥3 Codex rounds on a rule-bundle PR = automatic Opus 4.7 Notion strategic review trigger. Continuing past R3 autonomously enters known-trap territory.

This supersedes the prior "≥4 rounds = governance failure" threshold for rule-bundle PRs specifically. (Other PR types still use ≥4.)

### 3.3 R-budget cap

Rule-bundle PRs get a hard 4-round budget. R5 = forced merge or revert; no R6+ allowed. Author must choose at R5 between:
- (a) merge with explicit acceptance of remaining drift (recorded in PR body as "drift accepted: <list>")
- (b) revert and ship a smaller bundle

PR #11 (5 rounds) and PR #14 (6 rounds) both violated this cap retroactively. Going forward this is enforced.

### 3.4 Anti-overpromise commit-message rule

Commit messages on rule-bundle PRs MUST NOT claim convergence using superlatives:
- ❌ "verbatim identical", "exactly N spots", "pure pointers", "zero rule fragments outside X"
- ✅ "rule body lives at <file:section>; references at <list> updated to point", "operational/historical content at <list> retained by design"

The asymmetric grading (Codex literalism + author overpromise) is the core mechanic. Removing overpromise breaks the cycle.

---

## 4. PR #14 specific — what we accepted as drift

Per Path A merge (2026-04-25), PR #14 ships with these R6-flagged drift surfaces NOT fixed (recorded as "drift accepted by design"):

- `constitution.md:11,151` — changelog summary lines mentioning tier-trigger. Drift accepted: changelog by definition summarizes; pure-pointer changelog is uninformative.
- `RETRO-V61-054.md:161-164` (§6.3) — rollback condition body. Drift accepted: rollback rule was authored in RETRO context (the bundle's own retro), and is referenced from constitution.md:359 as canonical. Constitution treats RETRO §6.3 as the rule home for this specific clause.
- `README.md:104-106, 115-118, 127-131` — Output convention upgrade-path mention, Anti-bias safeguard rollback ref, Cost rollback ref. Drift accepted: these are README's owned operational documentation. They contain rule-shaped sentences because they describe the operational view of the rule, not the rule itself.
- `E11-00-PLAN.md:181, 257, 304, 344` — historical / closure / verification table references. Drift accepted: closure tables and verification tables need acceptance criteria phrased operationally, not as pure pointers. Replacing with pointers would make the closure check unverifiable.

**Test of acceptance:** if a future change to constitution.md:343 (the canonical rule) renders any of the above lines false, that's drift. As of 2026-04-25 commit ee602b0, all listed lines remain consistent with constitution.md:343.

---

## 5. Open questions (deferred to user / Opus 4.7)

- **Q1**: Should §3.2 R3-Opus-trigger be codified into constitution.md v2.4 immediately, or wait for a third recursive-drift instance? (Two instances may not be enough sample size; legislating prematurely is itself a recursive-drift trap.)
- **Q2**: Is the "allowed-restatement zone" enumeration in §3.1 itself drift-prone? (E.g., what stops the zone list from drifting between PRs?) — possibly need a fixed exemption schema in constitution.
- **Q3**: PR #11 + PR #14 both ran on doc-only changes. Is this pattern bounded to doc-only PRs, or will source-code rule-bundle PRs (e.g., a new authority gate in `runner.py`) trigger the same loop?

---

## 6. Provenance

- **Initial diagnosis**: in-session, 2026-04-25, after R6 verdict
- **Status**: candidate methodology rule, not yet codified into constitution v2.4
- **Pending**: Opus 4.7 strategic review (Notion async session) to validate §3.1 declaration template + §3.2 R3 hard-stop threshold + decide whether v2.4 amendment is appropriate

---

## 7. Trailer

```
Authored-by: claudecode-opus47 · v6.1 · solo-autonomy
Status: methodology candidate (not yet constitution-bound)
Supersedes: nothing yet (RETRO-V61-054 §6.5 was the precursor)
Triggers-Opus: yes (Q1 / Q2 / Q3 + §3.1 / §3.2 / §3.3 calibration)
```
