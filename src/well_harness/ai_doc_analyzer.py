"""P14 AI Document Analyzer — ambiguity detection, clarification loop, and prompt generation."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import ClassVar

from well_harness.document_intake import (
    assess_intake_packet,
    intake_packet_from_dict,
)
from well_harness.system_spec import (
    AcceptanceScenarioSpec,
    ComponentSpec,
    FaultModeSpec,
    KnowledgeCaptureSpec,
    LogicConditionSpec,
    LogicNodeSpec,
)
from well_harness.workbench_bundle import build_workbench_bundle as _build_workbench_bundle

# ---------------------------------------------------------------------------
# MOCK fixture — returned verbatim when P14_AI_MOCK=1
# ---------------------------------------------------------------------------

MOCK_AMBIGUITIES: list[dict] = [
    {
        "id": "amb-1",
        "text_excerpt": '"L3 active"',
        "description": "L3条件的具体激活逻辑不明确",
        "confidence_score": 0.85,
        "suggested_clarification": "L3在哪些具体条件下激活？",
    },
    {
        "id": "amb-2",
        "text_excerpt": '"VDT90 threshold"',
        "description": "VDT90 传感器的触发阈值未指定",
        "confidence_score": 0.72,
        "suggested_clarification": "VDT90 的 deploy_90_threshold_percent 默认值是多少？",
    },
    {
        "id": "amb-3",
        "text_excerpt": '"signal loss handling"',
        "description": "VDT90信号中断时的降级策略未定义",
        "confidence_score": 0.68,
        "suggested_clarification": "L3激活后若VDT90信号中断，系统如何处理？",
    },
]

MOCK_PROMPT_DOCUMENT: str = """# Claude Code Prompt — Control System Logic Module

## System Overview

**Control Objective:** VDT90-based deploy-90 logic with L3 activation gating.

## Logic Nodes

### Node: L3 Activation
- **Trigger:** VDT90 threshold exceeded AND reverser_inhibited == False
- **Dependencies:** VDT90 sensor reading >= deploy_90_threshold_percent

### Node: VDT90 Sensor
- **Reading:** deploy_90_threshold_percent (default: 90%)
- **Update Rate:** per-flight-cycle

## Condition Rules

| State | VDT90 | L3 |
|-------|-------|----|
| Nominal | < 90% | Inactive |
| Deployed | >= 90% | Active |

## Edge Cases

- If VDT90 sensor is unavailable: L3 remains in last known state
- If reverser_inhibited: L3 cannot activate regardless of VDT90

## Implementation Guidance

- Implement VDT90 as a percentage sensor (0-100%)
- L3 gate requires BOTH VDT90 >= threshold AND NOT inhibited
- Default threshold: 90%
"""


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

_AMBIGUITY_COUNTER: int = 0
_QUESTION_COUNTER: int = 0


def _next_ambiguity_id() -> str:
    global _AMBIGUITY_COUNTER
    _AMBIGUITY_COUNTER += 1
    return f"amb-{_AMBIGUITY_COUNTER}"


def _next_question_id() -> str:
    global _QUESTION_COUNTER
    _QUESTION_COUNTER += 1
    return f"q-{_QUESTION_COUNTER}"


@dataclass
class Ambiguity:
    id: str
    text_excerpt: str
    description: str
    confidence_score: float  # 0.0 – 1.0
    suggested_clarification: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text_excerpt": self.text_excerpt,
            "description": self.description,
            "confidence_score": self.confidence_score,
            "suggested_clarification": self.suggested_clarification,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Ambiguity:
        return cls(
            id=str(data["id"]),
            text_excerpt=str(data["text_excerpt"]),
            description=str(data["description"]),
            confidence_score=float(data["confidence_score"]),
            suggested_clarification=str(data["suggested_clarification"]),
        )


@dataclass
class Question:
    id: str
    ambiguity_id: str
    question: str
    is_optional: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ambiguity_id": self.ambiguity_id,
            "question": self.question,
            "is_optional": self.is_optional,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Question:
        return cls(
            id=str(data["id"]),
            ambiguity_id=str(data["ambiguity_id"]),
            question=str(data["question"]),
            is_optional=bool(data.get("is_optional", False)),
        )


@dataclass
class ClarificationResult:
    next_question: Question | None
    is_complete: bool
    progress: dict  # {"answered": int, "remaining": int}

    def to_dict(self) -> dict:
        return {
            "next_question": self.next_question.to_dict() if self.next_question else None,
            "is_complete": self.is_complete,
            "progress": self.progress,
        }


# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------


@dataclass
class P14SessionState:
    session_id: str
    document_text: str
    document_name: str
    created_at: float = field(default_factory=time.time)
    ambiguities: list[Ambiguity] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)  # ordered list of Qs to ask
    answered_question_ids: list[str] = field(default_factory=list)  # answered question ids
    clarification_history: list[tuple[str, str]] = field(default_factory=list)  # (question, answer)
    is_complete: bool = False
    generated_prompt: str | None = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "document_name": self.document_name,
            "ambiguities": [a.to_dict() for a in self.ambiguities],
            "answered_question_ids": list(self.answered_question_ids),
            "clarification_history": list(self.clarification_history),
            "is_complete": self.is_complete,
            "generated_prompt": self.generated_prompt,
        }

    def next_question(self) -> Question | None:
        """Return the next unanswered question, or None if all answered."""
        for q in self.questions:
            if q.id not in self.answered_question_ids:
                return q
        return None

    def progress(self) -> dict:
        answered = len(self.answered_question_ids)
        remaining = len(self.questions) - answered
        return {"answered": answered, "remaining": max(0, remaining)}


# ---------------------------------------------------------------------------
# Session Store (thread-safe in-memory dict)
# ---------------------------------------------------------------------------

import threading


class P14SessionStore:
    """Thread-safe in-memory session store for P14 sessions."""

    _instance: ClassVar[P14SessionStore | None] = None
    _init_lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls) -> P14SessionStore:
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._sessions = {}
                    cls._instance._sessions_lock = threading.Lock()
        return cls._instance

    def create(self, session_id: str, document_text: str, document_name: str) -> P14SessionState:
        with self._sessions_lock:
            # SECURITY: prevent unbounded memory growth
            if len(self._sessions) >= 50:
                oldest = min(self._sessions.items(), key=lambda x: x[1].created_at)
                del self._sessions[oldest[0]]

            session = P14SessionState(
                session_id=session_id,
                document_text=document_text,
                document_name=document_name,
            )
            self._sessions[session_id] = session
            return session

    def get(self, session_id: str) -> P14SessionState | None:
        with self._sessions_lock:
            return self._sessions.get(session_id)

    def update(self, session: P14SessionState) -> None:
        with self._sessions_lock:
            self._sessions[session.session_id] = session

    def delete(self, session_id: str) -> None:
        with self._sessions_lock:
            self._sessions.pop(session_id, None)

    def reset(self) -> None:
        """Clear all sessions and reset counters. For testing only."""
        global _AMBIGUITY_COUNTER, _QUESTION_COUNTER
        with self._sessions_lock:
            self._sessions.clear()
        _AMBIGUITY_COUNTER = 0
        _QUESTION_COUNTER = 0


# ---------------------------------------------------------------------------
# Mock mode detection
# ---------------------------------------------------------------------------

_is_mock: bool | None = None


def _is_mock_mode() -> bool:
    global _is_mock
    if _is_mock is None:
        _is_mock = os.environ.get("P14_AI_MOCK", "0") == "1"
    return _is_mock


# ---------------------------------------------------------------------------
# Core API functions
# ---------------------------------------------------------------------------

_ANTHROPIC_SYSTEM_PROMPT = """You are a control-systems engineer reviewing logic circuit specifications.
Your job is to find ambiguous or underspecified sections that could cause confusion for implementation.
For each ambiguity, provide:
1. A short text excerpt (quoted) from the document
2. A clear description of what is ambiguous
3. A confidence score (0.0–1.0) indicating how confident you are this is truly ambiguous
4. A suggested clarification question

Return your analysis as a JSON array of objects with keys: id, text_excerpt, description, confidence_score, suggested_clarification.
Respond ONLY with the JSON array, no markdown, no explanation."""


def _build_questions_from_ambiguities(ambiguities: list[Ambiguity]) -> list[Question]:
    """Derive ordered Question list from Ambiguity list (uses suggested_clarification as question text)."""
    questions: list[Question] = []
    for amb in ambiguities:
        q = Question(
            id=_next_question_id(),
            ambiguity_id=amb.id,
            question=amb.suggested_clarification,
            is_optional=False,
        )
        questions.append(q)
    return questions


def analyze_document(text: str) -> list[Ambiguity] | dict:
    """Analyze a document for ambiguities. Returns list[Ambiguity] or error dict."""
    if _is_mock_mode():
        return [Ambiguity.from_dict(a) for a in MOCK_AMBIGUITIES]

    messages = [
        {"role": "user", "content": f"Analyze this specification document for ambiguities:\n\n{text}"}
    ]
    response_text = _call_anthropic(messages, _ANTHROPIC_SYSTEM_PROMPT)

    # _call_anthropic returns {"error": ...} dict on failure
    if isinstance(response_text, dict) and "error" in response_text:
        return response_text

    try:
        data = json.loads(response_text)
        if isinstance(data, dict) and "ambiguities" in data:
            data = data["ambiguities"]
        return [Ambiguity.from_dict(item) for item in data]
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return {"error": "analysis_failed", "message": str(exc)}


def evaluate_clarification(session: P14SessionState, answer: str) -> ClarificationResult:
    """Evaluate a user's answer to the current clarification question.

    Appends the (question_text, answer) pair to clarification_history,
    marks the current question as answered, and returns the next question
    (or is_complete=True if all are answered).
    """
    # Record this answer against the current (unanswered) question
    current_q = session.next_question()
    if current_q is None:
        # No more questions — already complete
        session.is_complete = True
        return ClarificationResult(
            next_question=None,
            is_complete=True,
            progress=session.progress(),
        )

    question_text = current_q.question
    session.clarification_history.append((question_text, answer))
    session.answered_question_ids.append(current_q.id)

    # Check if more questions remain
    next_q = session.next_question()
    if next_q is None:
        session.is_complete = True
        return ClarificationResult(
            next_question=None,
            is_complete=True,
            progress=session.progress(),
        )

    return ClarificationResult(
        next_question=next_q,
        is_complete=False,
        progress=session.progress(),
    )


def generate_prompt_document(session: P14SessionState) -> str | dict:
    """Generate a structured Claude Code prompt document from resolved ambiguities."""
    if _is_mock_mode():
        return MOCK_PROMPT_DOCUMENT

    # Build context from session
    ambiguities_text = "\n".join(
        f"- [{a.id}] {a.description} (confidence: {a.confidence_score})"
        for a in session.ambiguities
    )
    clarification_text = "\n\n".join(f"Q: {q}\nA: {a}" for q, a in session.clarification_history)

    messages = [
        {
            "role": "user",
            "content": (
                "Generate a structured Claude Code prompt document for implementing this control system.\n\n"
                f"Document name: {session.document_name}\n\n"
                f"Document text:\n{session.document_text[:3000]}\n\n"
                f"Detected ambiguities:\n{ambiguities_text}\n\n"
                f"Clarification answers:\n{clarification_text}\n\n"
                "Respond ONLY with the markdown prompt document."
            ),
        }
    ]

    system = """You are a control-systems engineer creating a Claude Code prompt document.
Generate a markdown document with these sections:
1. System Overview — high-level description
2. Logic Nodes — each node with trigger/dependencies
3. Condition Rules — table of states
4. Edge Cases — boundary conditions and error handling
5. Implementation Guidance — concrete implementation hints

Respond ONLY with the markdown document, no JSON, no explanation."""

    response = _call_anthropic(messages, system)
    # _call_anthropic returns {"error": ...} dict on failure
    if isinstance(response, dict) and "error" in response:
        return response
    return response


# ---------------------------------------------------------------------------
# Anthropic API wrapper
# ---------------------------------------------------------------------------

_ANTHROPIC_API_KEY: str | None = None


def _get_anthropic_api_key() -> str:
    global _ANTHROPIC_API_KEY
    if _ANTHROPIC_API_KEY is None:
        _ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    return _ANTHROPIC_API_KEY


def _call_anthropic(messages: list[dict], system: str) -> str | dict:
    """Call Anthropic Messages API. Returns error dict on failure, text str on success."""
    api_key = _get_anthropic_api_key()
    if not api_key:
        return {"error": "anthropic_api_key_missing"}

    try:
        import anthropic
        from anthropic.types import TextBlock
    except ImportError:
        return {"error": "anthropic_sdk_not_installed"}

    try:
        base_url = os.environ.get("ANTHROPIC_BASE_URL")
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        client = anthropic.Anthropic(**client_kwargs)
        response = client.messages.create(
            model="MiniMax-2.7",
            max_tokens=8192,
            system=system,
            messages=messages,
            thinking={"type": "disabled"},
        )
        text_blocks = [block for block in response.content if isinstance(block, TextBlock)]
        if not text_blocks:
            return {"error": "no_text_in_response"}
        return "".join(block.text for block in text_blocks)
    except Exception as exc:  # noqa: BLE001 — AnthropicSDK raises various subclasses
        return {"error": "anthropic_api_error", "message": str(exc)}


# ---------------------------------------------------------------------------
# P15 — Pipeline Integration
# ---------------------------------------------------------------------------

_MOCK_INTAKE_PACKET = {
    "system_id": "vdt90-deploy-system",
    "title": "VDT90 Deploy-90 Logic with L3 Activation",
    "objective": "Implement VDT90-based deploy-90 logic with L3 activation gating",
    "source_of_truth": "P14 AI Document Analyzer generated spec",
    "source_documents": [
        {
            "id": "src-1",
            "kind": "markdown",
            "title": "Claude Code Prompt",
            "location": "session",
            "role": "primary",
            "notes": "",
        }
    ],
    "components": [
        {
            "id": "vdt90_sensor",
            "label": "VDT90 Sensor",
            "kind": "sensor",
            "state_shape": "percentage",
            "unit": "%",
            "description": "Deploy position sensor",
            "allowed_range": [0, 100],
            "allowed_states": [],
            "monitor_priority": "required",
        },
        {
            "id": "l3_gate",
            "label": "L3 Gate",
            "kind": "logic_gate",
            "state_shape": "boolean",
            "unit": "state",
            "description": "L3 activation gate",
            "allowed_range": None,
            "allowed_states": ["0", "1"],
            "monitor_priority": "required",
        },
        {
            "id": "reverser_inhibited",
            "label": "Reverser Inhibited",
            "kind": "pilot_input",
            "state_shape": "boolean",
            "unit": "state",
            "description": "Reverser inhibit signal",
            "allowed_range": None,
            "allowed_states": ["0", "1"],
            "monitor_priority": "optional",
        },
    ],
    "logic_nodes": [
        {
            "id": "l3_activation",
            "label": "L3 Activation",
            "description": "L3 activates when VDT90 >= 90% and not inhibited",
            "conditions": [
                {
                    "name": "vdt90_threshold",
                    "source_component_id": "vdt90_sensor",
                    "comparison": ">=",
                    "threshold_value": 90,
                    "note": "VDT90 must be at or above 90%",
                },
                {
                    "name": "not_inhibited",
                    "source_component_id": "reverser_inhibited",
                    "comparison": "==",
                    "threshold_value": False,
                    "note": "Reverser must not be inhibited",
                },
            ],
            "downstream_component_ids": ["l3_gate"],
            "evidence_priority": "high",
        }
    ],
    "acceptance_scenarios": [
        {
            "id": "nominal_deploy",
            "label": "Nominal Deploy",
            "description": "VDT90 >= 90%, reverser not inhibited -> L3 active",
            "time_scale_factor": 1.0,
            "total_duration_s": 5.0,
            "monitored_signal_ids": ["vdt90_sensor", "l3_gate"],
            "steady_signals": [
                {"signal_id": "reverser_inhibited", "value": False, "unit": "state", "note": "Reverser not inhibited"}
            ],
            "transitions": [
                {
                    "signal_id": "vdt90_sensor",
                    "start_s": 0.0,
                    "end_s": 3.0,
                    "start_value": 0.0,
                    "end_value": 95.0,
                    "unit": "%",
                    "note": "VDT90 rises to 95%",
                }
            ],
            "completion_condition": "l3_gate == True",
        }
    ],
    "fault_modes": [
        {
            "id": "vdt90_signal_loss",
            "target_component_id": "vdt90_sensor",
            "fault_kind": "open_circuit",
            "symptom": "VDT90 sensor signal is lost — open circuit detected",
            "reasoning_scope_component_ids": ["vdt90_sensor", "l3_activation"],
            "expected_diagnostic_sections": ["symptoms", "repair_hint"],
            "optimization_prompt": "L3 remains in last known state when VDT90 signal is lost.",
        }
    ],
    "knowledge_capture": {
        "incident_fields": ["system_id", "scenario_id", "fault_mode_id", "observed_symptoms", "evidence_links"],
        "resolution_fields": ["confirmed_root_cause", "repair_action", "validation_after_fix", "residual_risk"],
        "optimization_fields": ["suggested_logic_change", "reliability_gain_hypothesis", "redundancy_reduction_or_guardrail_note"],
    },
}


def _is_mock_p15() -> bool:
    return os.environ.get("P15_AI_MOCK", "0") == "1"


def convert_markdown_to_intake(markdown_text: str, system_id: str = "generated-system") -> dict:
    """Convert a P14 markdown prompt document into an intake packet dict.

    If P15_AI_MOCK=1, returns a mock intake packet with the given system_id.
    Otherwise calls the Anthropic API to extract structured data from the markdown.
    """
    if _is_mock_p15():
        packet = dict(_MOCK_INTAKE_PACKET)
        packet["system_id"] = system_id
        return packet

    system_prompt = (
        "You are a control-systems engineer extracting structured data from a markdown specification.\n"
        "Extract and return a single JSON object (no markdown, no explanation) with these fields:\n"
        "- system_id: a slug derived from the title\n"
        "- title: the system title\n"
        "- objective: a 1-sentence objective\n"
        "- source_documents: list of source document references\n"
        "- components: list of components with id, label, kind, state_shape, unit, description, allowed_range\n"
        "- logic_nodes: list of logic nodes with id, label, description, conditions (name, source_component_id, comparison, threshold_value, note), downstream_component_ids\n"
        "- acceptance_scenarios: list with id, label, description, time_scale_factor, total_duration_s, monitored_signal_ids, steady_signals, transitions (signal_id, start_s, end_s, start_value, end_value, unit, note), completion_condition\n"
        "- fault_modes: list with id, target_component_id, fault_kind, symptom, reasoning_scope_component_ids, expected_diagnostic_sections, optimization_prompt\n"
        "- knowledge_capture: object with incident_fields, resolution_fields, optimization_fields\n"
        "Use default values for any missing information."
    )

    messages = [{"role": "user", "content": f"Extract structured data from this markdown:\n\n{markdown_text}"}]
    response = _call_anthropic(messages, system_prompt)
    if isinstance(response, dict) and "error" in response:
        return response

    try:
        result = json.loads(response)
        # Ensure required schema fields that AI might omit
        if not result.get("source_of_truth"):
            result["source_of_truth"] = "P14 AI Document Analyzer — " + system_id

        # Normalize component fields
        for comp in result.get("components", []):
            if not isinstance(comp, dict):
                continue
            # 1. Rename allowed_range -> allowed_states when state_shape == "enum"
            if comp.get("state_shape") == "enum" and comp.get("allowed_range") and not comp.get("allowed_states"):
                comp["allowed_states"] = comp["allowed_range"]
                comp["allowed_range"] = None
            # 2. Clear allowed_range if it has >2 items or non-numeric items
            allowed_range = comp.get("allowed_range")
            if allowed_range is not None:
                if isinstance(allowed_range, list):
                    if len(allowed_range) > 2:
                        comp["allowed_range"] = None
                    else:
                        non_numeric = any(not isinstance(v, (int, float)) for v in allowed_range)
                        if non_numeric:
                            comp["allowed_range"] = None
                else:
                    comp["allowed_range"] = None
            # 3. Ensure unit is always a non-empty string
            if not comp.get("unit"):
                comp["unit"] = "N/A"

        # Normalize fault_kind values to schema-valid enum values
        valid_fault_kinds = {"bias_low", "bias_high", "stuck_low", "stuck_high",
                              "open_circuit", "short_to_power", "latched_no_unlock", "command_path_failure"}
        # Mapping of common AI-generated names to schema values
        fault_kind_aliases = {
            "hardware_failure": "open_circuit",
            "sensor_false_positive": "bias_high",
            "logic_race_condition": "latched_no_unlock",
            "stuck_open": "open_circuit",
            "sensor_misread": "bias_high",
        }
        for fm in result.get("fault_modes", []):
            if not isinstance(fm, dict):
                continue
            fk = str(fm.get("fault_kind") or "")
            if fk and fk not in valid_fault_kinds:
                fm["fault_kind"] = fault_kind_aliases.get(fk, "command_path_failure")

        # Normalize note fields in logic node conditions
        for ln in result.get("logic_nodes", []):
            if not isinstance(ln, dict):
                continue
            for cond in ln.get("conditions", []):
                if not cond.get("note"):
                    cond["note"] = "N/A"
                # Normalize threshold_value to numeric (AI may pass enum states like "IDLE")
                tv = cond.get("threshold_value")
                if tv is not None and not isinstance(tv, (int, float)):
                    cond["threshold_value"] = None

        # Normalize acceptance scenario numeric fields that AI may fill with enum strings
        for scenario in result.get("acceptance_scenarios", []):
            for trans in scenario.get("transitions", []):
                if not isinstance(trans, dict):
                    continue
                if not trans.get("note"):
                    trans["note"] = "N/A"
                if not trans.get("unit"):
                    trans["unit"] = "N/A"
                for fld in ("start_value", "end_value"):
                    v = trans.get(fld)
                    if v is not None and not isinstance(v, (int, float)):
                        trans[fld] = 0.0
            for sig in scenario.get("steady_signals", []):
                if not isinstance(sig, dict):
                    continue
                if not sig.get("note"):
                    sig["note"] = "N/A"
                if not sig.get("unit"):
                    sig["unit"] = "N/A"
                v = sig.get("value")
                if v is not None and not isinstance(v, (int, float)):
                    sig["value"] = 0.0

        # Normalize source_documents: must be list of dicts with all SourceDocumentRef required fields
        src_docs = result.get("source_documents", [])
        normalized_docs = []
        for i, doc in enumerate(src_docs):
            n = i + 1
            if isinstance(doc, dict):
                # Avoid turning None/null into literal "None" string
                def _norm_field(val, fallback):
                    if val is None or val == "":
                        return fallback
                    return str(val)
                normalized_docs.append({
                    "id": _norm_field(doc.get("id"), f"source-{n}"),
                    "title": _norm_field(doc.get("title"), f"Source {n}"),
                    "kind": _norm_field(doc.get("kind"), "markdown"),
                    "location": _norm_field(doc.get("location"), f"session-{n}"),
                    "role": _norm_field(doc.get("role"), "primary"),
                    "notes": str(doc.get("notes") or ""),
                })
            elif isinstance(doc, str):
                normalized_docs.append({
                    "id": f"source-{n}",
                    "title": doc or f"Source {n}",
                    "kind": "markdown",
                    "location": f"session-{n}",
                    "role": "primary",
                    "notes": "",
                })
        result["source_documents"] = normalized_docs
        return result
    except json.JSONDecodeError as exc:
        return {"error": "json_decode_failed", "message": str(exc)}


def run_pipeline_from_intake(intake_packet: dict) -> dict:
    """Run the full P7/P8 intake pipeline: validate -> assess -> build bundle.

    Returns combined result with assessment, bundle summary, and system_snapshot.
    """
    try:
        packet = intake_packet_from_dict(intake_packet)
    except (ValueError, KeyError, TypeError) as exc:
        return {"error": "intake_validation_failed", "message": str(exc)}

    assessment = assess_intake_packet(packet)

    bundle = _build_workbench_bundle(packet)

    system_snapshot = {
        "system_id": packet.system_id,
        "title": packet.title,
        "component_count": len(packet.components),
        "logic_node_count": len(packet.logic_nodes),
        "acceptance_scenario_count": len(packet.acceptance_scenarios),
        "fault_mode_count": len(packet.fault_modes),
        "ready_for_spec_build": assessment.get("ready_for_spec_build", False),
    }

    return {
        "assessment": assessment,
        "bundle": {
            "system_id": bundle.system_id,
            "system_title": bundle.system_title,
            "bundle_kind": bundle.bundle_kind,
            "ready_for_spec_build": bundle.ready_for_spec_build,
            "scenario_count": len(bundle.playback_report.scenarios) if bundle.playback_report else 0,
            "fault_mode_count": len(bundle.fault_diagnosis_report.fault_modes) if bundle.fault_diagnosis_report else 0,
        } if bundle else None,
        "system_snapshot": system_snapshot,
    }
