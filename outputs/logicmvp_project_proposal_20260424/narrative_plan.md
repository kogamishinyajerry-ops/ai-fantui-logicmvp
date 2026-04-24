# AI FANTUI LogicMVP Project Proposal Deck Plan

Audience: A formal state-owned enterprise project-initiation review. The deck should prioritize strategic value, visible project shape, funding, computing-resource demand, schedule, and stage outcomes. It should avoid deep code detail and avoid overstating shelved LLM/chat functions as current production capabilities.

Objective: Present the project as an aviation control-logic digital-twin verification workbench: deterministic control truth first, adapter-based system expansion, simulation/diagnosis/evidence loop, and optional AI-assisted explanation/knowledge layer for future productionization.

Narrative arc:
1. Start from a clear executive summary: what is being requested and what the enterprise gets.
2. Establish why complex control-logic validation needs a reusable workbench.
3. Show the blueprint and technical route at an executive level.
4. Use current repo evidence as credibility: C919 E-TRAS, thrust-reverser path, timeline simulator, validation suite.
5. Give a phased 18-month path with visible deliverables per stage.
6. Give a controlled budget and data-center compute plan: use existing data center resources first, no large model training cluster in phase one.
7. Close with concrete approval asks.

Slide list:
1. Cover: project name and one-line positioning.
2. Executive request: funding, schedule, data-center resources, pilot scope.
3. Strategic problem: why manual control-logic validation is expensive and risky.
4. Project positioning: verification/diagnosis/evidence workbench, not flight control replacement.
5. Overall blueprint: source material to adapter truth, simulation, diagnosis, knowledge, archive.
6. Current foundation: tested prototype and demo workbench evidence.
7. Technical route: three-layer route with deterministic truth, adapters, and AI-assisted explanation.
8. Development roadmap: 18-month staged plan.
9. Stage outcomes: what the review group can inspect after each stage.
10. Funding model: recommended 18-month budget envelope and allocation.
11. Computing/data-center plan: existing data center, GPU/CPU/storage by stage.
12. Implementation resources: delivery capability packages and governance controls.
13. Risk controls: truth boundary, security, data, schedule.
14. Expected value: reusable industrial software capability.
15. Approval request: decisions needed tomorrow.

Visual system: executive industrial style, deep charcoal background, aviation teal, safety amber, white panels, thin technical linework, dashboard motifs, and one real current UI screenshot used as credibility evidence.

Editability plan: all titles, labels, tables, numbers, timelines, and callouts are editable PowerPoint objects. The current UI screenshot is used only as a visual plate; all important claims remain editable text.

Source plan:
- Repo truth: README.md, .planning/PROJECT.md, .planning/STATE.md, .planning/ROADMAP.md, docs/co-development/roadmap-2026H2.md.
- Current visual plate: runs/codex_c919_reliability_screenshot.png.
- External hardware assumptions: NVIDIA L40S/H200 public specs and public cloud GPU pricing guidance, used only to keep compute sizing realistic.
