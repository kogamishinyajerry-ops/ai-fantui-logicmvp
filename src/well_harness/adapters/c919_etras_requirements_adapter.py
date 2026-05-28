"""Candidate-only C919 E-TRAS requirements preparse adapter.

This adapter keeps domain-specific C919 extraction rules out of the generic
requirements-intake analyzer. It produces concept-only graph candidates from
raw requirement text and never promotes those candidates into controller truth.
"""
from __future__ import annotations

import re
from typing import Any


SOURCE_ANCHOR_QUOTE_CHARS = 120

_FAULT_DEFERRED_RE = re.compile(
    r"故障注入.{0,24}(暂不考虑|暂时不考虑|不考虑|不在本轮|后续再做|很复杂)",
    re.IGNORECASE,
)
_C919_ETRAS_PATTERNS = {
    "domain": re.compile(r"\bC\s*919\b|\bE[-\s]*TRAS\b", re.IGNORECASE),
    "wow": re.compile(r"\bWOW\b|weight\s+on\s+wheels|机轮承重|地面信号|双通道地面", re.IGNORECASE),
    "etras_arm_specific": re.compile(r"\bE[-\s]*TRAS\b.{0,24}仅在|仅在.{0,24}\bE[-\s]*TRAS\b", re.IGNORECASE),
    "etras": re.compile(r"\bE[-\s]*TRAS\b|反推.{0,12}预位|预位", re.IGNORECASE),
    "handle_unlock": re.compile(r"反推手柄|解锁区间|unlock|lever", re.IGNORECASE),
    "wow_gate": re.compile(
        r"(WOW|地面信号|机轮承重).{0,40}(前置|门限|gating|有效|预位|条件)|"
        r"(前置|门限|gating).{0,40}(WOW|地面信号|机轮承重)",
        re.IGNORECASE,
    ),
    "v09_cmd2": re.compile(r"5\.1\s*CMD2|SinglePhaseUnlockPower_On\s*=\s*cmd2_active|CMD2.{0,20}单相解锁供电", re.IGNORECASE),
    "v09_cmd3_set": re.compile(r"5\.2\s*CMD3\s*Set|CMD3\s*Set.{0,24}SR\s*锁存器置位端", re.IGNORECASE),
    "v09_cmd3": re.compile(r"5\.4\s*CMD3\s*输出|ThreePhaseTRCUPower_On\s*=\s*cmd3_output|CMD3.{0,20}三相作动供电", re.IGNORECASE),
    "v09_cmd3_sr_output": re.compile(r"ThreePhaseTRCUPower_On\s*=\s*cmd3_output", re.IGNORECASE),
    "v09_cmd3_reset_priority": re.compile(r"IF\s+cmd3_reset_cond\s*==\s*TRUE|Reset\s*优先", re.IGNORECASE),
    "v09_deploy": re.compile(r"5\.5\s*Deploy\s*CMD1|FADEC_Deploy_Command\s*=\s*deploy_cmd1_active|展开命令", re.IGNORECASE),
    "v09_deploy_output": re.compile(r"FADEC_Deploy_Command\s*=\s*deploy_cmd1_active", re.IGNORECASE),
    "v09_deploy_engine_condition": re.compile(r"\|\s*①\s*\|\s*`engine_running\s+OR\s+maintenance_cycle`\s*\|\s*==\s*\|\s*TRUE", re.IGNORECASE),
    "v09_deploy_inhibited_condition": re.compile(r"\|\s*②\s*\|\s*`tr_inhibited`\s*\|\s*==\s*\|\s*FALSE", re.IGNORECASE),
    "v09_deploy_locks_condition": re.compile(r"\|\s*③\s*\|\s*`locks_unlocked_or_confirmed`\s*\|\s*==\s*\|\s*TRUE", re.IGNORECASE),
    "v09_deploy_tr_wow_condition": re.compile(r"\|\s*④\s*\|\s*`tr_wow`\s*\|\s*==\s*\|\s*TRUE", re.IGNORECASE),
    "v09_deploy_n1k_condition": re.compile(r"\|\s*⑤\s*\|\s*`n1k_pct`\s*\|\s*≤\s*\|\s*`max_n1k_deploy_limit_pct`", re.IGNORECASE),
    "v09_deploy_tra_condition": re.compile(r"\|\s*⑥\s*\|\s*`tra_deg`\s*\|\s*<\s*\|\s*-11\.74", re.IGNORECASE),
    "v09_eval_cmd3_output": re.compile(r"6\.\s*评估\s*CMD3\s*SR\s*锁存输出", re.IGNORECASE),
    "v09_eval_deploy_cmd1": re.compile(r"8\.\s*评估\s*Deploy\s*CMD1", re.IGNORECASE),
    "v09_eval_thr_idle_lock": re.compile(r"10\.\s*评估\s*油门慢车锁释放", re.IGNORECASE),
    "v09_mlg_wow": re.compile(r"\|\s*`mlg_wow`\s*\|.*主轮载荷", re.IGNORECASE),
    "v09_cmd2_mlg_wow_condition": re.compile(r"\|\s*①\s*\|\s*`mlg_wow`\s*\|\s*==\s*\|\s*TRUE", re.IGNORECASE),
    "v09_cmd3_apwtla_condition": re.compile(r"\|\s*④\s*\|\s*`apwtla`\s*\|\s*==\s*\|\s*TRUE", re.IGNORECASE),
    "v09_apwtla": re.compile(r"\|\s*`apwtla`\s*\||APWTLA|SW2", re.IGNORECASE),
    "v09_tr_inhibited": re.compile(r"\|\s*`tr_inhibited`\s*\||TR_Inhibited|反推电气抑制", re.IGNORECASE),
    "v09_thr_idle_lock": re.compile(r"5\.7\s*油门慢车锁释放", re.IGNORECASE),
    "v09_thr_idle_output": re.compile(r"\*\*输出\*\*:\s*`thr_idle_lock_release`", re.IGNORECASE),
    "v09_thr_idle_tr_deployed_condition": re.compile(r"\|\s*①\s*\|\s*`tr_deployed_confirmed`\s*\|\s*==\s*\|\s*TRUE", re.IGNORECASE),
    "v09_thr_idle_position_confirm": re.compile(r"TR_Position\s*≥\s*80%.*0\.5s", re.IGNORECASE),
    "v09_accept_thr_idle_lock": re.compile(r"TR_Deployed_Confirmed\s*=\s*TRUE.*thr_idle_lock_release\s*=\s*TRUE", re.IGNORECASE),
    "v09_pre_freeze": re.compile(r"Pre-Freeze|V0\.9|工程推断|冻结版", re.IGNORECASE),
}


class C919ETRASRequirementsPreparseAdapter:
    """Explicit adapter boundary for C919 E-TRAS intake preparse candidates."""

    system_id = "c919-etras"
    truth_effect = "none"

    def preparse_document(self, document_text: str) -> dict[str, Any]:
        return _deterministic_c919_etras_preparse(document_text)


def build_c919_etras_requirements_preparse(document_text: str) -> dict[str, Any]:
    """Return candidate-only C919 requirements facts for the generic analyzer."""

    return C919ETRASRequirementsPreparseAdapter().preparse_document(document_text)


def _str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return default
    return str(value).strip()


def _document_line_records(document_text: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for raw_line in document_text.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            continue
        records.append({"id": f"B{len(records) + 1:02d}", "text": line})
    return records


def _quote_around_match(text: str, match: re.Match[str]) -> str:
    if len(text) <= SOURCE_ANCHOR_QUOTE_CHARS:
        return text
    start = max(0, match.start() - 60)
    end = min(len(text), start + SOURCE_ANCHOR_QUOTE_CHARS)
    if match.end() > end:
        end = min(len(text), match.end() + 60)
        start = max(0, end - SOURCE_ANCHOR_QUOTE_CHARS)
    return text[start:end]


def _line_matches(records: list[dict[str, str]], pattern: re.Pattern[str], *, limit: int = 4) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for record in records:
        match = pattern.search(record["text"])
        if match:
            matches.append({**record, "quote_zh": _quote_around_match(record["text"], match)})
            if len(matches) >= limit:
                break
    return matches


def _anchor_from_record(record: dict[str, str], *, kind: str) -> dict[str, str]:
    quote = _str(record.get("quote_zh")) or record["text"][:SOURCE_ANCHOR_QUOTE_CHARS]
    return {
        "id": record["id"],
        "kind": kind,
        "origin": "docx_body",
        "quote_zh": quote,
    }


def _dedupe_anchors(anchors: list[dict[str, str]]) -> list[dict[str, str]]:
    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for anchor in anchors:
        anchor_id = _str(anchor.get("id"))
        quote = _str(anchor.get("quote_zh") or anchor.get("quote"))
        key = (anchor_id, quote)
        if not anchor_id or key in seen:
            continue
        seen.add(key)
        deduped.append(
            {
                "id": anchor_id[:32],
                "kind": _str(anchor.get("kind"), "正文条件")[:32],
                "origin": _str(anchor.get("origin"), "docx_body")[:32],
                "quote_zh": quote[:SOURCE_ANCHOR_QUOTE_CHARS],
            }
        )
        if len(deduped) >= 10:
            break
    return deduped


def _node(
    node_id: str,
    label: str,
    node_kind: str,
    description: str,
    anchors: list[dict[str, str]],
    *,
    parameters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "label": label,
        "node_kind": node_kind,
        "description_zh": description,
        "parameters": parameters or [],
        "source_anchors": anchors,
        "provenance": "docx_body_condition" if anchors else "model_assumption",
    }


def _edge(
    edge_id: str,
    source: str,
    target: str,
    label: str,
    anchors: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "id": edge_id,
        "source": source,
        "target": target,
        "label": label,
        "source_anchors": anchors,
        "provenance": "docx_body_condition" if anchors else "model_assumption",
    }


def _deterministic_source_scope(records: list[dict[str, str]]) -> dict[str, Any]:
    fault_deferred_records = _line_matches(records, _FAULT_DEFERRED_RE, limit=2)
    if not fault_deferred_records:
        return {}
    anchors = [_anchor_from_record(record, kind="范围约束") for record in fault_deferred_records]
    return {
        "fault_injection": {
            "status": "source_deferred",
            "reason_zh": "源文档声明故障注入本轮暂不考虑。",
            "source_anchors": anchors,
        }
    }


def _c919_anchor(records: list[dict[str, str]], pattern: re.Pattern[str], anchor_id: str) -> list[dict[str, str]]:
    matches = _line_matches(records, pattern, limit=1)
    if not matches:
        return []
    record = matches[0]
    quote = _str(record.get("quote_zh")) or record["text"][:SOURCE_ANCHOR_QUOTE_CHARS]
    return [
        {
            "id": anchor_id,
            "kind": "需求条款",
            "origin": "c919_etras_doc",
            "quote_zh": quote,
        }
    ]


def _deterministic_c919_etras_v09_preparse(records: list[dict[str, str]]) -> dict[str, Any]:
    domain_records = _line_matches(records, _C919_ETRAS_PATTERNS["domain"], limit=2)
    cmd2_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_cmd2"], "C919-V09-CMD2")
    cmd3_set_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_cmd3_set"], "C919-V09-CMD3-SET")
    cmd3_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_cmd3"], "C919-V09-CMD3")
    cmd3_sr_output_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_cmd3_sr_output"], "C919-V09-CMD3-SR-OUTPUT")
    cmd3_reset_priority_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_cmd3_reset_priority"], "C919-V09-CMD3-RESET-PRIORITY")
    deploy_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_deploy"], "C919-V09-DEPLOY-CMD1")
    deploy_output_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_deploy_output"], "C919-V09-DEPLOY-CMD1-OUTPUT")
    deploy_engine_condition_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_deploy_engine_condition"], "C919-V09-DEPLOY-CMD1-ENGINE")
    deploy_inhibited_condition_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_deploy_inhibited_condition"], "C919-V09-DEPLOY-CMD1-INHIBITED")
    deploy_locks_condition_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_deploy_locks_condition"], "C919-V09-DEPLOY-CMD1-LOCKS")
    deploy_tr_wow_condition_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_deploy_tr_wow_condition"], "C919-V09-DEPLOY-CMD1-TR-WOW")
    deploy_n1k_condition_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_deploy_n1k_condition"], "C919-V09-DEPLOY-CMD1-N1K")
    deploy_tra_condition_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_deploy_tra_condition"], "C919-V09-DEPLOY-CMD1-TRA")
    eval_cmd3_output_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_eval_cmd3_output"], "C919-V09-EVAL-CMD3-SR-OUTPUT")
    eval_deploy_cmd1_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_eval_deploy_cmd1"], "C919-V09-EVAL-DEPLOY-CMD1")
    eval_thr_idle_lock_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_eval_thr_idle_lock"], "C919-V09-EVAL-THR-IDLE-LOCK")
    mlg_wow_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_mlg_wow"], "C919-V09-MLG-WOW")
    cmd2_mlg_wow_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_cmd2_mlg_wow_condition"], "C919-V09-CMD2-MLG-WOW")
    cmd3_apwtla_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_cmd3_apwtla_condition"], "C919-V09-CMD3-SET-APWTLA")
    apwtla_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_apwtla"], "C919-V09-APWTLA")
    tr_inhibited_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_tr_inhibited"], "C919-V09-TR-INHIBITED")
    thr_idle_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_thr_idle_lock"], "C919-V09-THR-IDLE-LOCK")
    thr_idle_output_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_thr_idle_output"], "C919-V09-THR-IDLE-OUTPUT")
    thr_idle_condition_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_thr_idle_tr_deployed_condition"], "C919-V09-THR-IDLE-TR-DEPLOYED")
    thr_idle_position_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_thr_idle_position_confirm"], "C919-V09-THR-IDLE-POS-CONF")
    accept_thr_idle_lock_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_accept_thr_idle_lock"], "C919-V09-ACCEPT-THR-IDLE-LOCK")
    pre_freeze_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["v09_pre_freeze"], "C919-V09-PRE-FREEZE")
    if not (
        domain_records
        and cmd2_anchors
        and cmd3_set_anchors
        and cmd3_anchors
        and cmd3_sr_output_anchors
        and cmd3_reset_priority_anchors
        and deploy_anchors
        and deploy_output_anchors
        and deploy_engine_condition_anchors
        and deploy_inhibited_condition_anchors
        and deploy_locks_condition_anchors
        and deploy_tr_wow_condition_anchors
        and deploy_n1k_condition_anchors
        and deploy_tra_condition_anchors
        and eval_cmd3_output_anchors
        and eval_deploy_cmd1_anchors
        and eval_thr_idle_lock_anchors
        and mlg_wow_anchors
        and cmd2_mlg_wow_anchors
        and cmd3_apwtla_anchors
        and thr_idle_anchors
        and thr_idle_output_anchors
        and thr_idle_condition_anchors
        and thr_idle_position_anchors
        and accept_thr_idle_lock_anchors
    ):
        return {
            "available": False,
            "reason": "c919_etras_v09_coverage_not_found",
            "present_signal_ids": [
                signal_id
                for signal_id, anchors in (
                    ("domain", domain_records),
                    ("cmd2_active", cmd2_anchors),
                    ("cmd3_set", cmd3_set_anchors),
                    ("cmd3_output", cmd3_anchors),
                    ("cmd3_sr_output", cmd3_sr_output_anchors),
                    ("cmd3_reset_priority", cmd3_reset_priority_anchors),
                    ("deploy_cmd1_active", deploy_anchors),
                    ("deploy_cmd1_output", deploy_output_anchors),
                    ("deploy_cmd1_engine_condition", deploy_engine_condition_anchors),
                    ("deploy_cmd1_inhibited_condition", deploy_inhibited_condition_anchors),
                    ("deploy_cmd1_locks_condition", deploy_locks_condition_anchors),
                    ("deploy_cmd1_tr_wow_condition", deploy_tr_wow_condition_anchors),
                    ("deploy_cmd1_n1k_condition", deploy_n1k_condition_anchors),
                    ("deploy_cmd1_tra_condition", deploy_tra_condition_anchors),
                    ("eval_cmd3_sr_output", eval_cmd3_output_anchors),
                    ("eval_deploy_cmd1", eval_deploy_cmd1_anchors),
                    ("eval_thr_idle_lock", eval_thr_idle_lock_anchors),
                    ("mlg_wow", mlg_wow_anchors),
                    ("cmd2_mlg_wow_condition", cmd2_mlg_wow_anchors),
                    ("cmd3_apwtla_condition", cmd3_apwtla_anchors),
                    ("apwtla", apwtla_anchors),
                    ("tr_inhibited_clear", tr_inhibited_anchors),
                    ("thr_idle_lock_release", thr_idle_anchors),
                    ("thr_idle_output", thr_idle_output_anchors),
                    ("thr_idle_tr_deployed_condition", thr_idle_condition_anchors),
                    ("thr_idle_position_confirm", thr_idle_position_anchors),
                    ("accept_thr_idle_lock", accept_thr_idle_lock_anchors),
                )
                if anchors
            ],
            "source_scope": _deterministic_source_scope(records),
        }

    cmd2_node_anchors = _dedupe_anchors(cmd2_anchors + mlg_wow_anchors + tr_inhibited_anchors)
    cmd3_node_anchors = _dedupe_anchors(
        cmd3_sr_output_anchors
        + cmd3_reset_priority_anchors
        + cmd3_set_anchors
        + cmd3_anchors
        + mlg_wow_anchors
        + apwtla_anchors
        + cmd3_apwtla_anchors
        + tr_inhibited_anchors
    )
    deploy_node_anchors = _dedupe_anchors(
        deploy_output_anchors
        + deploy_engine_condition_anchors
        + deploy_inhibited_condition_anchors
        + deploy_locks_condition_anchors
        + deploy_tr_wow_condition_anchors
        + deploy_n1k_condition_anchors
        + deploy_tra_condition_anchors
        + deploy_anchors
        + eval_deploy_cmd1_anchors
        + cmd3_anchors
        + mlg_wow_anchors
    )
    thr_idle_node_anchors = _dedupe_anchors(
        thr_idle_anchors
        + thr_idle_output_anchors
        + thr_idle_condition_anchors
        + thr_idle_position_anchors
        + eval_thr_idle_lock_anchors
        + accept_thr_idle_lock_anchors
    )
    nodes = [
        _node("mlg_wow", "MLG_WOW", "input", "主轮载荷/WOW 已解析单路输入。", mlg_wow_anchors),
        _node("tr_inhibited_clear", "TR_Inhibited=0", "input", "反推电气未抑制的安全门限。", tr_inhibited_anchors),
        _node("cmd2_active", "CMD2 单相解锁", "logic", "TLS 与吊挂锁 115VAC 单相解锁供电候选节点。", cmd2_node_anchors),
        _node("apwtla", "APWTLA/SW2", "input", "TRA 经过 SW2 窗口后的三相作动请求。", _dedupe_anchors(apwtla_anchors + cmd3_apwtla_anchors)),
        _node("cmd3_output", "CMD3 三相作动", "logic", "TRCU 115VAC 三相作动供电 SR 锁存输出。", cmd3_node_anchors),
        _node("deploy_cmd1_active", "Deploy CMD1", "logic", "FADEC 展开命令候选节点。", deploy_node_anchors),
        _node("thr_idle_lock_release", "慢车锁释放", "output", "TR 展开确认后释放油门慢车电子锁。", thr_idle_node_anchors),
    ]
    edges = [
        _edge("c919_v09_e1", "mlg_wow", "cmd2_active", "CMD2 ground gate", _dedupe_anchors(cmd2_mlg_wow_anchors + cmd2_anchors)),
        _edge("c919_v09_e2", "tr_inhibited_clear", "cmd2_active", "inhibit clear", _dedupe_anchors(tr_inhibited_anchors + cmd2_anchors)),
        _edge("c919_v09_e3", "mlg_wow", "cmd3_output", "CMD3 ground gate", _dedupe_anchors(mlg_wow_anchors + cmd3_anchors)),
        _edge(
            "c919_v09_e4",
            "apwtla",
            "cmd3_output",
            "SW2 set gate",
            _dedupe_anchors(cmd3_set_anchors + cmd3_apwtla_anchors + cmd3_sr_output_anchors + cmd3_reset_priority_anchors),
        ),
        _edge(
            "c919_v09_e5",
            "cmd3_output",
            "deploy_cmd1_active",
            "Deploy CMD1 evaluation after CMD3",
            _dedupe_anchors(
                cmd3_sr_output_anchors
                + deploy_output_anchors
                + deploy_engine_condition_anchors
                + deploy_inhibited_condition_anchors
                + deploy_locks_condition_anchors
                + deploy_tr_wow_condition_anchors
                + deploy_n1k_condition_anchors
                + deploy_tra_condition_anchors
                + eval_cmd3_output_anchors
                + eval_deploy_cmd1_anchors
            ),
        ),
        _edge(
            "c919_v09_e6",
            "deploy_cmd1_active",
            "thr_idle_lock_release",
            "TR deployed confirmation",
            _dedupe_anchors(
                thr_idle_output_anchors
                + thr_idle_condition_anchors
                + thr_idle_position_anchors
                + deploy_output_anchors
                + deploy_engine_condition_anchors
                + deploy_inhibited_condition_anchors
                + deploy_locks_condition_anchors
                + deploy_tr_wow_condition_anchors
                + deploy_n1k_condition_anchors
                + deploy_tra_condition_anchors
            ),
        ),
    ]
    source_scope = {
        **_deterministic_source_scope(records),
        "c919_etras": {
            "status": "candidate_only",
            "reason_zh": "V0.9 原文是 Pre-Freeze Reference；本地规则只生成候选链路，不构成冻结版或认证声明。",
            "source_anchors": _dedupe_anchors(pre_freeze_anchors + cmd2_anchors + cmd3_anchors + deploy_anchors),
        },
        "engineering_inference": {
            "status": "source_declared",
            "reason_zh": "源文档声明 Stow CMD1 等项目含工程推断，候选图不得升级为真值。",
            "source_anchors": pre_freeze_anchors,
        },
    }
    return {
        "available": True,
        "version": 1,
        "strategy": "c919_etras_v09_rule_preparse",
        "model": "deterministic-c919-etras-v09",
        "summary_zh": "本地预解析已从 C919 ETRAS V0.9 文档抽出 CMD2、CMD3、Deploy 与慢车锁释放候选链路。",
        "document_assumptions": [
            "本地规则只从 C919 ETRAS V0.9 原文中的信号字典、核心逻辑节点和评估顺序抽取候选结构。",
            "V0.9 属于 Pre-Freeze Reference；输出仅用于工程师在场确认，不修改控制真值，也不构成冻结版或认证声明。",
        ],
        "nodes": nodes,
        "edges": edges,
        "requirement_groups": [
            {"id": "c919_v09_cmd2", "label": "CMD2", "source_anchors": cmd2_node_anchors, "node_ids": ["mlg_wow", "tr_inhibited_clear", "cmd2_active"]},
            {"id": "c919_v09_cmd3", "label": "CMD3", "source_anchors": cmd3_node_anchors, "node_ids": ["mlg_wow", "apwtla", "cmd3_output"]},
            {"id": "c919_v09_deploy", "label": "Deploy CMD1", "source_anchors": deploy_node_anchors, "node_ids": ["cmd3_output", "deploy_cmd1_active", "thr_idle_lock_release"]},
        ],
        "source_scope": source_scope,
        "reading_burden": {
            "current_action_zh": "先确认 MLG_WOW 到 CMD2，再确认 CMD3/Deploy 是否贴合 V0.9 原文。",
            "key_outputs_zh": ["CMD2 单相解锁", "CMD3 三相作动", "Deploy CMD1 与慢车锁释放"],
            "detail_policy_zh": "节点、连线和来源锚点默认折叠到详情区。",
        },
        "detected": {
            "domain": "c919_etras_v09",
            "signal_ids": [node["id"] for node in nodes],
            "anchor_count": len(records),
        },
    }


def _deterministic_c919_etras_preparse(document_text: str) -> dict[str, Any]:
    records = _document_line_records(document_text)
    if not records:
        return {"available": False, "reason": "empty_document"}

    v09_facts = _deterministic_c919_etras_v09_preparse(records)
    if v09_facts.get("available"):
        return v09_facts
    if any(signal_id != "domain" for signal_id in v09_facts.get("present_signal_ids", [])):
        return v09_facts

    domain_records = _line_matches(records, _C919_ETRAS_PATTERNS["domain"], limit=2)
    wow_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["wow"], "C919-ETRAS-WOW")
    etras_anchors = _c919_anchor(
        records,
        _C919_ETRAS_PATTERNS["etras_arm_specific"],
        "C919-ETRAS-ARM",
    ) or _c919_anchor(records, _C919_ETRAS_PATTERNS["etras"], "C919-ETRAS-ARM")
    handle_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["handle_unlock"], "C919-ETRAS-HANDLE")
    gate_anchors = _c919_anchor(records, _C919_ETRAS_PATTERNS["wow_gate"], "C919-ETRAS-WOW-EDGE")
    domain_present = bool(domain_records)
    if not (domain_present and wow_anchors and etras_anchors):
        return {
            "available": False,
            "reason": "c919_etras_coverage_not_found",
            "present_signal_ids": [
                signal_id
                for signal_id, anchors in (
                    ("domain", domain_records),
                    ("wow_valid", wow_anchors),
                    ("etras_armed", etras_anchors),
                    ("handle_unlock_range", handle_anchors),
                )
                if anchors
            ],
            "source_scope": _deterministic_source_scope(records),
        }

    etras_node_anchors = _dedupe_anchors(etras_anchors + handle_anchors + gate_anchors)
    wow_gate_anchors = _dedupe_anchors(gate_anchors + wow_anchors + etras_anchors)
    nodes = [
        _node("wow_valid", "WOW 有效", "input", "C919 ETRAS 地面/WOW 有效候选条件。", wow_anchors),
        _node("etras_armed", "ETRAS 预位", "logic", "仅作为 ETRAS 进入预位的候选解释。", etras_node_anchors),
    ]
    if handle_anchors:
        nodes.insert(
            1,
            _node("handle_unlock_range", "手柄解锁区", "input", "反推手柄进入解锁区间候选条件。", handle_anchors),
        )
    edges = [_edge("c919_e1", "wow_valid", "etras_armed", "WOW gating", wow_gate_anchors)]
    if handle_anchors:
        edges.append(
            _edge(
                "c919_e2",
                "handle_unlock_range",
                "etras_armed",
                "handle unlock gating",
                _dedupe_anchors(handle_anchors + etras_anchors),
            )
        )
    source_scope = {
        **_deterministic_source_scope(records),
        "c919_etras": {
            "status": "candidate_only",
            "reason_zh": "本地规则只把 C919 ETRAS 原文转成候选链路，不构成冻结版或认证声明。",
            "source_anchors": _dedupe_anchors(wow_anchors + etras_anchors + gate_anchors),
        },
    }
    return {
        "available": True,
        "version": 1,
        "strategy": "c919_etras_rule_preparse",
        "model": "deterministic-c919-etras",
        "summary_zh": "本地预解析已从 C919 ETRAS 原始文本抽出 WOW 门限与 ETRAS 预位候选链路。",
        "document_assumptions": [
            "本地规则只从 C919 ETRAS 原文中出现的 WOW、ETRAS 和手柄解锁条件抽取候选结构。",
            "该输出仅用于工程师在场确认，不修改控制真值，也不构成冻结版或认证声明。",
        ],
        "nodes": nodes,
        "edges": edges,
        "requirement_groups": [
            {
                "id": "c919_etras_wow_gate",
                "label": "WOW gating",
                "source_anchors": _dedupe_anchors(wow_anchors + etras_anchors + gate_anchors),
                "node_ids": [node["id"] for node in nodes],
            }
        ],
        "source_scope": source_scope,
        "reading_burden": {
            "current_action_zh": "先确认 WOW 门限是否可以作为 ETRAS 预位候选链路的前置条件。",
            "key_outputs_zh": ["WOW 有效候选节点", "ETRAS 预位候选节点", "WOW gating 候选连线"],
            "detail_policy_zh": "节点、连线和来源锚点默认折叠到详情区。",
        },
        "detected": {
            "domain": "c919_etras",
            "signal_ids": ["wow_valid", "etras_armed", *([] if not handle_anchors else ["handle_unlock_range"])],
            "anchor_count": len(records),
        },
    }
