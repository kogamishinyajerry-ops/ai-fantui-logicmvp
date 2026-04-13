"""P14 AI Document Analyzer — ambiguity detection, clarification loop, and prompt generation."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from typing import ClassVar

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


def _call_anthropic(messages: list[dict], system: str) -> str:
    """Call Anthropic Messages API. Returns error dict string if key is missing."""
    api_key = _get_anthropic_api_key()
    if not api_key:
        return json.dumps({"error": "anthropic_api_key_missing"})

    try:
        import anthropic
    except ImportError:
        return json.dumps({"error": "anthropic_sdk_not_installed"})

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-opus-4-6-20251120",
            max_tokens=4096,
            system=system,
            messages=messages,
        )
        return response.content[0].text
    except Exception as exc:  # noqa: BLE001 — AnthropicSDK raises various subclasses
        return {"error": "anthropic_api_error", "message": str(exc)}
