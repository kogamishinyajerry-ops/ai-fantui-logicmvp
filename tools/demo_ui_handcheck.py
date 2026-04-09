"""Print a lightweight manual hand-check checklist for the local demo UI."""

from __future__ import annotations

import argparse
import webbrowser


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
START_COMMAND = "PYTHONPATH=src python3 -m well_harness.demo_server"
OPEN_COMMAND = "PYTHONPATH=src python3 -m well_harness.demo_server --open"
TALK_TRACK_PATH = "docs/demo_presenter_talk_track.md"

CORE_PROMPTS = (
    (
        "bridge",
        "logic4 和 throttle lock 有什么关系",
        (
            "intent: logic4_thr_lock_bridge",
            "chain highlight: logic4 / THR_LOCK bridge association",
            "structured sections: evidence / outcome explain the relationship",
            "raw JSON debug: payload updates with matched_node=logic4->thr_lock",
        ),
    ),
    (
        "diagnose",
        "为什么 throttle lock 没释放",
        (
            "intent: diagnose_problem",
            "chain highlight: THR_LOCK / throttle_lock_release_cmd association",
            "structured sections: possible_causes / evidence / risks",
            "raw JSON debug: payload stays visible for diagnosis review",
        ),
    ),
    (
        "trigger",
        "触发 logic3 会发生什么",
        (
            "intent: trigger_node",
            "chain highlight: logic3 plus EEC / PLS / PDU command subnodes",
            "structured sections: evidence / outcome describe the trigger window",
            "raw JSON debug: payload shows matched_node=logic3 and target_logic=logic3",
        ),
    ),
    (
        "proposal",
        "把 logic3 的 TRA 阈值改成 -8 会发生什么",
        (
            "intent: propose_logic_change",
            "chain highlight: logic3 threshold proposal association",
            "structured sections: dry-run / proposal, required_changes / risks",
            "safety check: does not directly modify controller.py",
            "raw JSON debug: payload updates without changing demo answer semantics",
        ),
    ),
)

UI_CHECKPOINTS = (
    "selected prompt state",
    "loading / ready state",
    "control chain highlight",
    "highlight explanation",
    "Answer sections summary",
    "summary chip click / focus",
    "summary chip arrow-key navigation",
    "raw JSON debug collapse / expand",
    "empty prompt error",
)

BOUNDARY_CHECKS = (
    "deterministic controlled demo layer",
    "built-in nominal-deploy / retract-reset scenarios",
    "simplified first-cut plant",
    "not a full natural-language AI system",
    "not a complete physical model",
)

NON_E2E_NOTE = (
    "This is a manual browser hand-check helper, not browser E2E automation. "
    "By default it only prints this checklist; it does not start the server or drive a browser."
)

PRESENTER_WALKTHROUGH_STEPS = (
    (
        "1. [Setup]",
        (
            f"Start the server in a separate terminal: {START_COMMAND}",
            f"Optional launch convenience: {OPEN_COMMAND} asks the standard-library browser launcher to open the URL; it is not browser E2E automation.",
            "Open the local UI URL and keep this walkthrough as the presenter script.",
            "Follow the page callout labels: [Input], [Chain], [Highlight], [Structured answer], [Raw JSON].",
            "Use the screenshot-free route strip: Input -> Chain -> Highlight -> Structured answer -> Raw JSON.",
            "Use the visible Presenter Run Card to launch the bridge / diagnose / trigger / proposal sequence without creating a second presenter-only surface.",
            "If field names need explaining, use the compact answer guide to pair the Audience answer-field legend with Answer sections counts.",
            "On narrow screens, read the same compact answer guide top-to-bottom; section chips stay touch-friendly.",
        ),
    ),
    (
        "2. [Input] [Chain] [Raw JSON]",
        (
            "Run: logic4 和 throttle lock 有什么关系",
            "Point to the logic4 / THR_LOCK bridge highlight, the highlight explanation, and the raw JSON panel.",
            "Callout: this answers the relationship between the upstream logic gate and downstream release command.",
        ),
    ),
    (
        "3. [Structured answer]",
        (
            "Run: 为什么 throttle lock 没释放",
            "Point to possible_causes / evidence / risks in the structured answer.",
            "Callout: this is the controlled diagnosis path for the release window, not a free-form fault hunt.",
        ),
    ),
    (
        "4. [Chain]",
        (
            "Run: 触发 logic3 会发生什么",
            "Point to logic3 plus EEC / PLS / PDU command subnode highlights.",
            "Callout: the chain highlight is answer association, not a complete causal proof.",
        ),
    ),
    (
        "5. [Structured answer] [Safety]",
        (
            "Run: 把 logic3 的 TRA 阈值改成 -8 会发生什么",
            "Point to dry-run proposal, required_changes / risks, and raw JSON.",
            "Callout: this does not directly modify controller.py.",
        ),
    ),
    (
        "6. [Boundary]",
        (
            "Close by naming the boundary: deterministic controlled demo layer.",
            "It uses built-in nominal-deploy / retract-reset scenarios and a simplified first-cut plant.",
            "It is not browser E2E automation, not a new control truth, not a full LLM, and not a complete physical model.",
        ),
    ),
)


def demo_url(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    return f"http://{host}:{port}/"


def _bullet_list(items: tuple[str, ...]) -> list[str]:
    return [f"- {item}" for item in items]


def _prompt_list() -> list[str]:
    lines: list[str] = []
    for category, prompt, observations in CORE_PROMPTS:
        lines.append(f"- [{category}] {prompt}")
        lines.append("  expected observations:")
        lines.extend(f"  - {observation}" for observation in observations)
    return lines


def render_checklist(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    lines = [
        "Well Harness UI Demo Hand-check",
        "",
        NON_E2E_NOTE,
        "",
        "1. Start the local UI server in a separate terminal:",
        f"   {START_COMMAND}",
        "",
        "2. Open the local UI URL:",
        f"   {demo_url(host, port)}",
        "",
        "3. Run these core prompts:",
        *_prompt_list(),
        "",
        "4. Check the UI behavior:",
        *_bullet_list(UI_CHECKPOINTS),
        "",
        "5. Confirm the demo boundary copy:",
        *_bullet_list(BOUNDARY_CHECKS),
        "",
        "Notes:",
        "- The optional --open flag only opens the URL with Python's standard-library webbrowser module.",
        "- --open still does not start the server and does not automate the browser.",
        f"- Server launch convenience: {OPEN_COMMAND} opens the UI URL after server startup, but it is still not browser E2E automation.",
        "- The expected observations are manual review hints, not a new answer payload or control truth.",
    ]
    return "\n".join(lines)


def render_walkthrough(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    lines = [
        "Well Harness UI Demo Presenter Walkthrough",
        "",
        "This is a concise manual presenter walkthrough, not browser E2E automation.",
        "It is not a new answer payload or control truth.",
        "",
        "Local UI URL:",
        f"  {demo_url(host, port)}",
        "",
        "Presenter steps:",
    ]
    for title, step_lines in PRESENTER_WALKTHROUGH_STEPS:
        lines.append(title)
        lines.extend(f"  - {line}" for line in step_lines)
    lines.extend(
        (
            "",
            "Use the full hand-check checklist without --walkthrough when you need detailed expected observations.",
            f"One-page presenter talk track: {TALK_TRACK_PATH}",
            "Presenter readiness run card: see the talk track section with the same name, and the matching visible card on the first screen.",
            "No screenshots or browser automation are generated by this helper.",
        )
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="manual browser hand-check checklist; not browser E2E automation."
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Host shown in the checklist URL; does not start the server.",
    )
    parser.add_argument(
        "--port",
        default=DEFAULT_PORT,
        type=int,
        help="Port shown in the checklist URL; does not start the server.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the checklist URL with webbrowser.open after printing; does not start the server.",
    )
    parser.add_argument(
        "--walkthrough",
        action="store_true",
        help="Print the concise presenter walkthrough instead of the full hand-check checklist.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = (
        render_walkthrough(args.host, args.port)
        if args.walkthrough
        else render_checklist(args.host, args.port)
    )
    print(report)
    if args.open:
        webbrowser.open(demo_url(args.host, args.port))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
