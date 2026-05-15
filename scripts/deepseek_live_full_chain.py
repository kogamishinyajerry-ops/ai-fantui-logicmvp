#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from well_harness.demo_server import (
    build_requirements_fault_injection_prepare_response,
    build_requirements_fault_injection_sandbox_response,
    build_requirements_intake_analysis_response,
    build_requirements_logic_drawing_response,
)


DEFAULT_ARTIFACT_DIR = Path("artifacts/deepseek-live-full-chain")
DEFAULT_DOCUMENT_TEXT = """
演示级反推逻辑需求：当无线电高度 RA 小于 6 ft，TRA 进入反推区，SW1 与 SW2 均有效，发动机运行，EEC 允许，且未被 reverser_inhibited 禁止时，系统允许释放油门锁并形成 THR_LOCK release 概念输出。
工程师已确认：TRA 反推区间按 -1.4° 到 -11.74° 处理；SW1 与 SW2 必须同时有效，逻辑关系为 AND；reverser_inhibited 来自系统抑制信号，true 时禁止释放；RA 门限、TRA 区间、SW1/SW2 状态和 EEC enable 必须保留为可解释参数。
本链路只生成概念逻辑图、故障候选和 dry-run 沙盒注入建议，不能修改控制器真值，也不能声称完成认证。
""".strip()


class LiveChainFailure(RuntimeError):
    pass


def _has_deepseek_key() -> bool:
    return any(os.environ.get(name, "").strip() for name in ("DEEPSEEK_API_KEY", "DeepSeek_API_key"))


def _count_payload(payload: dict[str, Any]) -> dict[str, int]:
    return {
        "concept_nodes": len(payload.get("concept_logic_nodes") or []),
        "concept_edges": len(payload.get("concept_edges") or []),
        "nodes": len(payload.get("nodes") or []),
        "edges": len(payload.get("edges") or []),
        "parameter_panels": len(payload.get("parameter_panels") or []),
        "fault_scenarios": len(payload.get("fault_scenarios") or []),
        "injection_points": len(payload.get("injection_points") or []),
        "boundary_questions": len(payload.get("boundary_questions") or []),
        "sandbox_plans": len(payload.get("sandbox_injection_plan") or []),
        "observations": len(payload.get("observation_points") or []),
        "reviews": len(payload.get("review_checklist") or []),
    }


def _summary_for_payload(name: str, payload: dict[str, Any], elapsed_sec: float) -> dict[str, Any]:
    llm = payload.get("llm") if isinstance(payload.get("llm"), dict) else {}
    return {
        "name": name,
        "ok": True,
        "elapsed_sec": round(elapsed_sec, 2),
        "kind": payload.get("kind"),
        "status": payload.get("status"),
        "llm": {
            "provider": llm.get("provider"),
            "model": llm.get("model"),
            "api_base": llm.get("api_base"),
            "key_source": llm.get("key_source"),
            "response_source": llm.get("response_source"),
        },
        "counts": _count_payload(payload),
    }


def _safe_write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _call_builder(
    name: str,
    builder: Callable[[dict[str, Any]], tuple[dict | None, dict | None, int]],
    request: dict[str, Any],
    artifact_dir: Path,
    report: dict[str, Any],
) -> dict[str, Any]:
    started = time.monotonic()
    response, error, status_code = builder(request)
    elapsed = time.monotonic() - started
    if error is not None or response is None or status_code >= 400:
        item = {
            "name": name,
            "ok": False,
            "elapsed_sec": round(elapsed, 2),
            "status_code": status_code,
            "error": error or {"error": "empty_response"},
        }
        report["steps"].append(item)
        _safe_write(artifact_dir / "run_summary.json", report)
        raise LiveChainFailure(f"{name} failed: {json.dumps(item, ensure_ascii=False)}")
    _safe_write(artifact_dir / f"{name}.json", response)
    item = _summary_for_payload(name, response, elapsed)
    report["steps"].append(item)
    print(f"OK {name} {item['elapsed_sec']}s {item['kind']} {item['status']}")
    return response


def _answer_for_question(question: dict[str, Any], index: int) -> dict[str, str]:
    prompt = str(question.get("prompt_zh") or question.get("prompt") or question.get("id") or f"q{index}").strip()
    key = prompt.lower()
    if "tra" in key:
        answer = "TRA 反推区间按 -1.4° 到 -11.74° 处理；进入反推区必须满足该区间，深反推门限可参考 -11.74°。"
    elif "sw1" in key or "sw2" in key or "开关" in prompt:
        answer = "SW1 与 SW2 均必须有效，逻辑关系为 AND；任一无效都不释放油门锁。"
    elif "inhibit" in key or "禁止" in prompt or "抑制" in prompt:
        answer = "reverser_inhibited 是系统抑制信号；true 时禁止释放，false 时才允许后续门控判断。"
    elif "eec" in key:
        answer = "EEC enable 必须为 true；EEC 不允许时输出保持不释放。"
    else:
        answer = "确认该项用于演示级概念链路，按 dry-run 只读验证处理，不修改控制器真值。"
    return {
        "question_id": str(question.get("id") or f"q{index}"),
        "prompt_zh": prompt,
        "answer_zh": answer,
    }


def _run_intake(document_text: str, artifact_dir: Path, report: dict[str, Any], max_rounds: int) -> dict[str, Any]:
    answers: list[dict[str, str]] = []
    latest: dict[str, Any] | None = None
    for round_index in range(1, max_rounds + 1):
        request: dict[str, Any] = {
            "document_name": "deepseek-v4-pro-live-demo.md",
            "document_text": document_text,
            "provider": "deepseek",
            "allow_fallback": False,
        }
        if answers:
            request["clarification_answers"] = answers
        latest = _call_builder(
            f"01_requirements_intake_round_{round_index}",
            build_requirements_intake_analysis_response,
            request,
            artifact_dir,
            report,
        )
        if latest.get("status") == "ready_for_logic_builder" and latest.get("ready_for_logic_builder") is True:
            _safe_write(artifact_dir / "01_requirements_intake.json", latest)
            return latest
        questions = latest.get("open_questions")
        if not isinstance(questions, list) or not questions:
            break
        answers = [_answer_for_question(question, index) for index, question in enumerate(questions, start=1) if isinstance(question, dict)]
        report.setdefault("clarification_rounds", []).append(
            {
                "round": round_index,
                "question_count": len(questions),
                "answer_count": len(answers),
            }
        )
    _safe_write(artifact_dir / "01_requirements_intake.json", latest or {})
    raise LiveChainFailure("requirements intake did not reach ready_for_logic_builder with live DeepSeek")


def run_live_chain(document_text: str, artifact_dir: Path, max_rounds: int) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "ok": False,
        "provider": "deepseek",
        "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        "artifact_dir": str(artifact_dir),
        "steps": [],
    }
    if not _has_deepseek_key():
        raise LiveChainFailure("DEEPSEEK_API_KEY or DeepSeek_API_key is required for live verification")

    requirements = _run_intake(document_text, artifact_dir, report, max_rounds)
    drawing = _call_builder(
        "02_logic_drawing",
        build_requirements_logic_drawing_response,
        {
            "provider": "deepseek",
            "allow_fallback": False,
            "requirements_payload": requirements,
        },
        artifact_dir,
        report,
    )
    fault = _call_builder(
        "03_fault_preparation",
        build_requirements_fault_injection_prepare_response,
        {
            "provider": "deepseek",
            "allow_fallback": False,
            "requirements_payload": requirements,
            "drawing_payload": drawing,
            "change_history": [],
        },
        artifact_dir,
        report,
    )
    boundary_answers = [
        {
            "id": str(question.get("id") or f"boundary_{index}"),
            "prompt_zh": str(question.get("prompt_zh") or question.get("prompt") or ""),
            "answer_zh": "确认本次只生成 dry-run 沙盒建议，不触发真实执行；边界限制按演示输入范围处理。",
        }
        for index, question in enumerate(fault.get("boundary_questions") or [], start=1)
        if isinstance(question, dict)
    ]
    sandbox = _call_builder(
        "04_sandbox_plan",
        build_requirements_fault_injection_sandbox_response,
        {
            "provider": "deepseek",
            "allow_fallback": False,
            "fault_injection_preparation_payload": fault,
            "boundary_answers": boundary_answers,
        },
        artifact_dir,
        report,
    )
    report["ok"] = True
    report["final_counts"] = {
        "requirements": _count_payload(requirements),
        "drawing": _count_payload(drawing),
        "fault": _count_payload(fault),
        "sandbox": _count_payload(sandbox),
    }
    _safe_write(artifact_dir / "run_summary.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the live DeepSeek V4 Pro requirements-to-sandbox chain.")
    parser.add_argument("--artifact-dir", default=str(DEFAULT_ARTIFACT_DIR))
    parser.add_argument("--document-text", default=DEFAULT_DOCUMENT_TEXT)
    parser.add_argument("--max-rounds", type=int, default=3)
    args = parser.parse_args()

    try:
        report = run_live_chain(args.document_text, Path(args.artifact_dir), max(1, args.max_rounds))
    except LiveChainFailure as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    print("SUMMARY " + json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
