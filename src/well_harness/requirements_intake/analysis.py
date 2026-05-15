from __future__ import annotations

import base64
import binascii
import hashlib
import io
import json
import os
import queue
import re
import threading
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from xml.etree import ElementTree


REQUIREMENTS_INTAKE_KIND = "ai-fantui-requirements-intake-analysis"
REQUIREMENTS_INTAKE_VERSION = 1
THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET = "thrust_reverser_demo_chain_v1"
MAX_REQUIREMENTS_TEXT_CHARS = 400_000
MAX_DOCUMENT_BASE64_CHARS = 14_000_000
LLM_TIMEOUT_SECONDS = 180.0
LLM_MAX_TOKENS = 2048
MODEL_INPUT_MAX_CHARS = 32_000
MODEL_INPUT_HEAD_CHARS = 12_000
MODEL_INPUT_TAIL_CHARS = 8_000
MODEL_INPUT_KEY_LINE_CHARS = 12_000

DEEPSEEK_API_BASE = "https://api.deepseek.com"
DEEPSEEK_DEFAULT_MODEL = "deepseek-v4-pro"
MINIMAX_API_BASE = "https://api.minimaxi.com/v1"
MINIMAX_DEFAULT_MODEL = "MiniMax-M2.7-highspeed"
TEXT_DOCUMENT_SUFFIXES = {
    "",
    ".txt",
    ".md",
    ".markdown",
    ".csv",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
}
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE),
)
REQUIREMENT_LINE_RE = re.compile(
    r"(需求|要求|必须|应当|应该|shall|should|when|if|当|如果|条件|逻辑|门限|阈值|"
    r"输入|输出|信号|状态|命令|释放|锁|互锁|故障|失效|注入|冗余|RA|TRA|SW|EEC|"
    r"AND|OR|NOT|gate|logic)",
    re.IGNORECASE,
)
SOURCE_ANCHOR_QUOTE_CHARS = 120

_L1_L4_PATTERNS = {
    "logic1": re.compile(r"(\bL\s*1\b|工作逻辑\s*1|逻辑\s*1|logic\s*1)", re.IGNORECASE),
    "logic2": re.compile(r"(\bL\s*2\b|工作逻辑\s*2|逻辑\s*2|logic\s*2)", re.IGNORECASE),
    "logic3": re.compile(r"(\bL\s*3\b|工作逻辑\s*3|逻辑\s*3|logic\s*3)", re.IGNORECASE),
    "logic4": re.compile(r"(\bL\s*4\b|工作逻辑\s*4|逻辑\s*4|logic\s*4)", re.IGNORECASE),
}
_SIGNAL_PATTERNS = {
    "ra_lt_6ft": re.compile(r"(RA|无线电高度|飞机离地|离地|高度).*?(<|小于|低于|不超过|小於)\s*6\s*ft|RA\s*<\s*6\s*ft", re.IGNORECASE),
    "sw1": re.compile(r"SW\s*1|微动开关\s*1|开关\s*1", re.IGNORECASE),
    "sw2": re.compile(r"SW\s*2|微动开关\s*2|开关\s*2", re.IGNORECASE),
    "tra": re.compile(r"\bTRA\b|反推手柄|油门杆|反推区", re.IGNORECASE),
    "tls": re.compile(r"\bTLS\b|锁定套筒|115\s*VAC", re.IGNORECASE),
    "pls": re.compile(r"\bPLS\b", re.IGNORECASE),
    "vdt90": re.compile(r"\bVDT\b|90\s*%|百分之\s*90", re.IGNORECASE),
    "thr_lock_release": re.compile(r"THR[_\s-]*LOCK|油门锁|反推电子锁|电子锁解锁|油门台.{0,12}锁.{0,4}解锁|释放", re.IGNORECASE),
}
_FAULT_DEFERRED_RE = re.compile(
    r"故障注入.{0,24}(暂不考虑|暂时不考虑|不考虑|不在本轮|后续再做|很复杂)",
    re.IGNORECASE,
)


RequestPost = Callable[[str, bytes, dict[str, str], float], str]


class RequirementsIntakeError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_payload(self) -> dict[str, Any]:
        return {
            "error": self.code,
            "message": self.message,
            **({"details": self.details} if self.details else {}),
        }


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    model: str
    api_base: str
    endpoint: str
    api_key: str
    key_source: str


def _trimmed_env(name: str) -> str | None:
    value = os.environ.get(name)
    if value and value.strip():
        return value.strip()
    return None


def _resolve_key(names: tuple[str, ...]) -> tuple[str, str] | None:
    for name in names:
        value = _trimmed_env(name)
        if value:
            return value, f"env:{name}"
    return None


def _provider_config(provider: str) -> ProviderConfig:
    normalized = (provider or "deepseek").strip().lower()
    if normalized not in {"deepseek", "minimax"}:
        raise RequirementsIntakeError(
            "provider_unknown",
            "provider must be 'deepseek' or 'minimax'.",
            details={"provider": normalized},
        )

    if normalized == "deepseek":
        key = _resolve_key(("DEEPSEEK_API_KEY", "DeepSeek_API_key"))
        if key is None:
            raise RequirementsIntakeError(
                "missing_api_key",
                "DeepSeek API key is not available in the server environment.",
                status_code=503,
                details={"provider": "deepseek", "checked": ["DEEPSEEK_API_KEY", "DeepSeek_API_key"]},
            )
        api_key, key_source = key
        base = os.environ.get("DEEPSEEK_API_BASE", DEEPSEEK_API_BASE).rstrip("/")
        model = os.environ.get("DEEPSEEK_MODEL", DEEPSEEK_DEFAULT_MODEL).strip() or DEEPSEEK_DEFAULT_MODEL
        return ProviderConfig(
            provider="deepseek",
            model=model,
            api_base=base,
            endpoint=f"{base}/chat/completions",
            api_key=api_key,
            key_source=key_source,
        )

    key = _resolve_key(("MINIMAX_API_KEY", "Minimax_API_key"))
    if key is None:
        raise RequirementsIntakeError(
            "missing_api_key",
            "MiniMax API key is not available in the server environment.",
            status_code=503,
            details={"provider": "minimax", "checked": ["MINIMAX_API_KEY", "Minimax_API_key"]},
        )
    api_key, key_source = key
    base = os.environ.get("MINIMAX_API_BASE", MINIMAX_API_BASE).rstrip("/")
    model = os.environ.get("MINIMAX_MODEL", MINIMAX_DEFAULT_MODEL).strip() or MINIMAX_DEFAULT_MODEL
    return ProviderConfig(
        provider="minimax",
        model=model,
        api_base=base,
        endpoint=f"{base}/chat/completions",
        api_key=api_key,
        key_source=key_source,
    )


def resolve_provider_metadata(provider: str = "deepseek") -> dict[str, str]:
    cfg = _provider_config(provider)
    return {
        "provider": cfg.provider,
        "model": cfg.model,
        "api_base": cfg.api_base,
        "key_source": cfg.key_source,
    }


def resolve_provider_status(provider: str = "deepseek") -> dict[str, Any]:
    normalized = (provider or "deepseek").strip().lower()
    try:
        meta = resolve_provider_metadata(normalized)
    except RequirementsIntakeError as exc:
        if exc.code != "missing_api_key":
            raise
        provider_name = str(exc.details.get("provider") or normalized or "deepseek")
        if provider_name == "deepseek":
            model = os.environ.get("DEEPSEEK_MODEL", DEEPSEEK_DEFAULT_MODEL).strip() or DEEPSEEK_DEFAULT_MODEL
            api_base = os.environ.get("DEEPSEEK_API_BASE", DEEPSEEK_API_BASE).rstrip("/")
        elif provider_name == "minimax":
            model = os.environ.get("MINIMAX_MODEL", MINIMAX_DEFAULT_MODEL).strip() or MINIMAX_DEFAULT_MODEL
            api_base = os.environ.get("MINIMAX_API_BASE", MINIMAX_API_BASE).rstrip("/")
        else:
            model = ""
            api_base = ""
        return {
            "provider": provider_name,
            "model": model,
            "api_base": api_base,
            "key_available": False,
            "key_source": "",
            "live_ready": False,
            "error": exc.code,
            "checked": list(exc.details.get("checked") or []),
        }
    return {
        **meta,
        "key_available": True,
        "live_ready": True,
    }


def _decode_text_bytes(blob: bytes, document_name: str) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return blob.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    raise RequirementsIntakeError(
        "unsupported_document_encoding",
        "Uploaded document could not be decoded as UTF-8 or GB18030 text.",
        status_code=415,
        details={"document_name": document_name or "uploaded-document"},
    )


def _docx_paragraphs_from_xml(xml_bytes: bytes) -> list[str]:
    root = ElementTree.fromstring(xml_bytes)
    paragraphs: list[str] = []
    for paragraph in root.iter():
        if not paragraph.tag.endswith("}p"):
            continue
        parts: list[str] = []
        for node in paragraph.iter():
            if node.tag.endswith("}t") and node.text:
                parts.append(node.text)
            elif node.tag.endswith("}tab"):
                parts.append("\t")
            elif node.tag.endswith("}br"):
                parts.append("\n")
        line = "".join(parts).strip()
        if line:
            paragraphs.append(line)
    return paragraphs


def _extract_docx_text(blob: bytes, document_name: str) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(blob), "r") as zf:
            document_xml = zf.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise RequirementsIntakeError(
            "invalid_docx",
            "Uploaded .docx file could not be read as a Word document.",
            status_code=415,
            details={"document_name": document_name},
        ) from exc
    try:
        text = "\n".join(_docx_paragraphs_from_xml(document_xml)).strip()
    except ElementTree.ParseError as exc:
        raise RequirementsIntakeError(
            "invalid_docx_xml",
            "Uploaded .docx document.xml could not be parsed.",
            status_code=415,
            details={"document_name": document_name},
        ) from exc
    if not text:
        raise RequirementsIntakeError(
            "empty_docx",
            "Uploaded .docx file did not contain extractable text.",
            details={"document_name": document_name},
        )
    return text


def extract_document_text_from_payload(request_payload: dict[str, Any]) -> tuple[str, str]:
    document_name = _str(request_payload.get("document_name"), "pasted-requirements.txt")
    document_text = request_payload.get("document_text")
    if isinstance(document_text, str) and document_text.strip():
        return document_text, document_name

    encoded = request_payload.get("document_base64")
    if not isinstance(encoded, str) or not encoded.strip():
        raise RequirementsIntakeError(
            "missing_document_text",
            "document_text must be a non-empty string, or document_base64 must contain an uploaded document.",
            details={"field": "document_text"},
        )
    encoded = encoded.strip()
    if len(encoded) > MAX_DOCUMENT_BASE64_CHARS:
        raise RequirementsIntakeError(
            "document_upload_too_large",
            "document_base64 exceeds the supported upload size.",
            status_code=413,
            details={"max_base64_chars": MAX_DOCUMENT_BASE64_CHARS},
        )
    try:
        blob = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise RequirementsIntakeError(
            "invalid_document_base64",
            "document_base64 must be valid base64 data.",
            details={"field": "document_base64"},
        ) from exc

    suffix = Path(document_name).suffix.lower()
    if suffix == ".docx":
        return _extract_docx_text(blob, document_name), document_name
    if suffix == ".pdf":
        raise RequirementsIntakeError(
            "unsupported_document_type",
            "PDF upload is not enabled in this stdlib-only WebUI slice. Export text or upload .docx/.txt/.md.",
            status_code=415,
            details={"document_name": document_name, "supported": [".docx", ".txt", ".md"]},
        )
    if suffix in TEXT_DOCUMENT_SUFFIXES:
        return _decode_text_bytes(blob, document_name), document_name
    try:
        return _decode_text_bytes(blob, document_name), document_name
    except RequirementsIntakeError as exc:
        raise RequirementsIntakeError(
            "unsupported_document_type",
            "Uploaded document type is not supported by the requirements-intake WebUI.",
            status_code=415,
            details={"document_name": document_name, "supported": [".docx", ".txt", ".md"]},
        ) from exc


def _default_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def _configured_llm_timeout_seconds() -> float:
    raw = os.environ.get("REQUIREMENTS_INTAKE_LLM_TIMEOUT_SECONDS")
    if raw is None or not raw.strip():
        return LLM_TIMEOUT_SECONDS
    try:
        parsed = float(raw)
    except ValueError:
        return LLM_TIMEOUT_SECONDS
    return parsed if parsed > 0 else LLM_TIMEOUT_SECONDS


def _configured_llm_max_tokens() -> int:
    raw = os.environ.get("REQUIREMENTS_INTAKE_LLM_MAX_TOKENS")
    if raw is None or not raw.strip():
        return LLM_MAX_TOKENS
    try:
        parsed = int(raw)
    except ValueError:
        return LLM_MAX_TOKENS
    return parsed if parsed > 0 else LLM_MAX_TOKENS


def _post_with_wall_timeout(
    post: RequestPost,
    cfg: ProviderConfig,
    body: bytes,
    headers: dict[str, str],
    timeout_sec: float,
) -> str:
    result_queue: queue.Queue[tuple[str, Any]] = queue.Queue(maxsize=1)

    def run_post() -> None:
        try:
            result_queue.put(("ok", post(cfg.endpoint, body, headers, timeout_sec)))
        except BaseException as exc:  # pragma: no cover - re-raised on caller thread
            result_queue.put(("error", exc))

    worker = threading.Thread(
        target=run_post,
        name=f"requirements-intake-{cfg.provider}-llm-post",
        daemon=True,
    )
    worker.start()
    worker.join(timeout=timeout_sec)
    if worker.is_alive():
        raise RequirementsIntakeError(
            "llm_timeout",
            f"{cfg.provider} request exceeded the configured response timeout.",
            status_code=502,
            details={"provider": cfg.provider, "timeout_sec": timeout_sec},
        )

    status, value = result_queue.get_nowait()
    if status == "error":
        raise value
    return value


def _redact_sensitive(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[redacted]", redacted)
    return redacted


def _short_error_text(value: Any, *, limit: int = 360) -> str:
    text = _redact_sensitive(_str(value))
    text = " ".join(text.split())
    return text[:limit]


def _upstream_error_details(cfg: ProviderConfig, exc: urllib.error.HTTPError) -> dict[str, Any]:
    details: dict[str, Any] = {
        "provider": cfg.provider,
        "upstream_status": exc.code,
    }
    try:
        raw = exc.read().decode("utf-8", errors="replace")
    except Exception:
        raw = ""
    if not raw:
        return details

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        details["upstream_message"] = _short_error_text(raw)
        return details

    if isinstance(payload, dict):
        err = payload.get("error")
        if isinstance(err, dict):
            details["upstream_message"] = _short_error_text(err.get("message") or err.get("msg"))
            details["upstream_error_type"] = _short_error_text(err.get("type") or err.get("code"))
        else:
            details["upstream_message"] = _short_error_text(payload.get("message") or payload.get("msg") or raw)
            details["upstream_error_type"] = _short_error_text(payload.get("type") or payload.get("code"))
    else:
        details["upstream_message"] = _short_error_text(raw)
    return {key: value for key, value in details.items() if value not in ("", None)}


def _strip_model_json(raw: str) -> str:
    text = raw.strip()
    while True:
        start = text.find("<think>")
        if start < 0:
            break
        end = text.find("</think>", start)
        if end < 0:
            text = text[:start].strip()
            break
        text = (text[:start] + text[end + len("</think>"):]).strip()
    if text.startswith("```"):
        text = text.split("```", 1)[1]
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
        text = text.rsplit("```", 1)[0]
    return text.strip()


def _extract_json_object(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise json.JSONDecodeError("No JSON object found in model response.", text, 0)


def _chat_payload(cfg: ProviderConfig, messages: list[dict[str, str]], *, max_tokens: int | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": cfg.model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": max_tokens or _configured_llm_max_tokens(),
        "stream": False,
        "response_format": {"type": "json_object"},
    }
    if cfg.provider == "deepseek":
        payload["thinking"] = {"type": "disabled"}
    return payload


def _call_chat_completion(
    cfg: ProviderConfig,
    messages: list[dict[str, str]],
    *,
    request_post: RequestPost | None = None,
    timeout_sec: float | None = None,
    max_tokens: int | None = None,
) -> str:
    resolved_timeout = timeout_sec if timeout_sec is not None else _configured_llm_timeout_seconds()
    body = json.dumps(_chat_payload(cfg, messages, max_tokens=max_tokens), ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    post = request_post or _default_post
    try:
        raw_body = _post_with_wall_timeout(post, cfg, body, headers, resolved_timeout)
    except urllib.error.HTTPError as exc:
        raise RequirementsIntakeError(
            "llm_http_error",
            f"{cfg.provider} returned HTTP {exc.code}.",
            status_code=502,
            details=_upstream_error_details(cfg, exc),
        ) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RequirementsIntakeError(
            "llm_network_error",
            f"{cfg.provider} request failed before a model response was available.",
            status_code=502,
            details={"provider": cfg.provider, "reason_type": type(exc).__name__},
        ) from exc

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise RequirementsIntakeError(
            "llm_protocol_error",
            f"{cfg.provider} response was not valid JSON.",
            status_code=502,
        ) from exc
    choices = parsed.get("choices") or []
    if not choices:
        raise RequirementsIntakeError("llm_empty_response", f"{cfg.provider} response had no choices.", status_code=502)
    message = choices[0].get("message") or {}
    content = message.get("content") or choices[0].get("text") or ""
    if not isinstance(content, str) or not content.strip():
        raise RequirementsIntakeError(
            "llm_empty_response",
            f"{cfg.provider} response did not include message.content.",
            status_code=502,
        )
    return content


def _compact_document_for_llm(document_text: str) -> tuple[str, dict[str, Any]]:
    text = document_text.strip()
    if len(text) <= MODEL_INPUT_MAX_CHARS:
        return text, {
            "input_chars": len(text),
            "original_chars": len(text),
            "compacted": False,
            "strategy": "full_text",
        }

    key_lines: list[str] = []
    key_chars = 0
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if not line or not REQUIREMENT_LINE_RE.search(line):
            continue
        addition = line[:600]
        if key_chars + len(addition) > MODEL_INPUT_KEY_LINE_CHARS:
            break
        key_lines.append(addition)
        key_chars += len(addition)

    parts = [
        "[BEGIN_DOCUMENT_HEAD]",
        text[:MODEL_INPUT_HEAD_CHARS],
        "[END_DOCUMENT_HEAD]",
    ]
    if key_lines:
        parts.extend(
            [
                "[BEGIN_REQUIREMENT_LIKE_LINES]",
                "\n".join(key_lines),
                "[END_REQUIREMENT_LIKE_LINES]",
            ]
        )
    parts.extend(
        [
            "[BEGIN_DOCUMENT_TAIL]",
            text[-MODEL_INPUT_TAIL_CHARS:],
            "[END_DOCUMENT_TAIL]",
            (
                f"[COMPACTION_NOTICE] 原文 {len(text)} 字符，已按 head/key-lines/tail "
                "确定性抽取后送入模型；未抽取部分不得被模型当作已确认真值。"
            ),
        ]
    )
    compacted = "\n\n".join(parts)
    return compacted[:MODEL_INPUT_MAX_CHARS], {
        "input_chars": min(len(compacted), MODEL_INPUT_MAX_CHARS),
        "original_chars": len(text),
        "compacted": True,
        "strategy": "head_requirement_lines_tail",
        "key_line_count": len(key_lines),
        "max_input_chars": MODEL_INPUT_MAX_CHARS,
    }


def _analysis_prompt(document_text: str, document_name: str, input_meta: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是 AI FANTUI 的需求理解助手，只做概念级控制逻辑梳理。"
                "不得生成可执行仿真、不得宣称认证、不得修改 controller truth。"
                "请只输出一个完整 JSON 对象，不要 Markdown。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"文档名：{document_name or 'unnamed-requirements.txt'}\n\n"
                "任务：提取概念性逻辑电路草图和必要澄清问题。\n"
                "输出字段固定为：summary_zh, document_assumptions, open_questions, "
                "concept_logic_nodes, concept_edges, ready_for_logic_builder；"
                "可选字段：reconstruction_target。\n"
                "限制：summary_zh<=120字；document_assumptions 必须是字符串数组；"
                "open_questions 最多4个，若不能进入逻辑链路绘制至少3个；"
                "每个问题含 id,prompt_zh,rationale_zh,blocks，字符串<=60字，blocks用字符串；"
                "concept_logic_nodes 最多24个，id用英文短id，label<=12字，"
                "node_kind=input|logic|output|component，description_zh<=40字，"
                "每节点 parameters 最多2个；concept_edges 最多36条，含 id,source,target,label。"
                "如果 [工程师澄清回答] 中出现英文信号名，例如 *_cmd、*_ls、*_vdt、*_ctrl、"
                "540vdc、115vac、PDU、PLS、TLS、ETRAC、EEC，必须优先保留为节点、参数或边标签；"
                "每个工作逻辑的直接输出必须单独建 output 节点，"
                "不得把不同逻辑的输出合并到同一个节点，除非澄清回答明确说它们是同一信号。"
                "如果原文不够清楚，请把问题放入 open_questions，不要猜成真值；"
                f"如果输入明确要求“一模一样重构反推逻辑演示舱/反推演示舱链路/ demo 舱 SVG”，"
                f"将 reconstruction_target 设为 {THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET}；"
                "如果需求原文包含 [工程师澄清回答]，回答内容优先级高于模型推测；"
                "已被工程师回答的问题不得重复提出，除非回答与原文直接矛盾；"
                "若澄清后已有清晰的节点、参数和连线候选，应将 ready_for_logic_builder 设为 true 且 open_questions 为空；"
                "如果输入提示包含 COMPACTION_NOTICE，未覆盖内容视为待澄清。\n\n"
                f"输入元数据：{json.dumps(input_meta, ensure_ascii=False)}\n\n"
                f"需求原文：\n{document_text}"
            ),
        },
    ]


def _str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return default
    return str(value).strip()


def _str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_str(item) for item in value if _str(item)]


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
        if len(deduped) >= 6:
            break
    return deduped


def _anchors_for_patterns(
    records: list[dict[str, str]],
    patterns: list[re.Pattern[str]],
    *,
    kind: str,
    limit: int = 4,
) -> list[dict[str, str]]:
    anchors: list[dict[str, str]] = []
    for pattern in patterns:
        anchors.extend(_anchor_from_record(record, kind=kind) for record in _line_matches(records, pattern, limit=limit))
    return _dedupe_anchors(anchors)


def _anchor_ids(anchors: list[dict[str, str]]) -> list[str]:
    return [anchor["id"] for anchor in anchors if anchor.get("id")]


def _deterministic_param(
    param_id: str,
    label: str,
    unit: str,
    default: float,
    anchors: list[dict[str, str]],
    *,
    min_value: float = 0.0,
    max_value: float = 1.0,
) -> dict[str, Any]:
    return {
        "id": param_id,
        "label": label,
        "unit": unit,
        "min": min_value,
        "max": max_value,
        "default": default,
        "source_hint": f"DOCX {'/'.join(_anchor_ids(anchors)[:2])}",
        "source_anchors": anchors[:2],
    }


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


def _deterministic_l1_l4_preparse(document_text: str) -> dict[str, Any]:
    records = _document_line_records(document_text)
    if not records:
        return {"available": False, "reason": "empty_document"}

    logic_anchors = {
        logic_id: [_anchor_from_record(record, kind="正文条件") for record in _line_matches(records, pattern, limit=4)]
        for logic_id, pattern in _L1_L4_PATTERNS.items()
    }
    present_logic_ids = [logic_id for logic_id, anchors in logic_anchors.items() if anchors]
    signal_anchors = {
        signal_id: [_anchor_from_record(record, kind="正文条件") for record in _line_matches(records, pattern, limit=4)]
        for signal_id, pattern in _SIGNAL_PATTERNS.items()
    }
    present_signal_ids = [signal_id for signal_id, anchors in signal_anchors.items() if anchors]
    if len(present_logic_ids) < 4 or len(present_signal_ids) < 4:
        return {
            "available": False,
            "reason": "l1_l4_or_signal_coverage_not_found",
            "present_logic_ids": present_logic_ids,
            "present_signal_ids": present_signal_ids,
            "source_scope": _deterministic_source_scope(records),
        }

    ra_anchors = signal_anchors["ra_lt_6ft"]
    sw1_anchors = signal_anchors["sw1"]
    sw2_anchors = signal_anchors["sw2"]
    tra_anchors = signal_anchors["tra"]
    tls_anchors = signal_anchors["tls"]
    pls_anchors = signal_anchors["pls"]
    vdt_anchors = signal_anchors["vdt90"]
    lock_anchors = signal_anchors["thr_lock_release"]
    l1_anchors = _dedupe_anchors(logic_anchors["logic1"] + ra_anchors + sw1_anchors)
    l2_anchors = _dedupe_anchors(logic_anchors["logic2"] + sw2_anchors + tls_anchors)
    l3_anchors = _dedupe_anchors(logic_anchors["logic3"] + tls_anchors + pls_anchors)
    l4_anchors = _dedupe_anchors(logic_anchors["logic4"] + vdt_anchors + lock_anchors + tra_anchors)

    nodes = [
        _node(
            "ra_lt_6ft",
            "RA<6ft",
            "input",
            "无线电高度低于 6ft 的放行门限。",
            ra_anchors,
            parameters=[_deterministic_param("ra_threshold_ft", "RA门限", "ft", 6.0, ra_anchors, max_value=20.0)],
        ),
        _node("sw1", "SW1", "input", "反推手柄第一开关/区间条件。", sw1_anchors),
        _node("sw2", "SW2", "input", "反推手柄第二开关/区间条件。", sw2_anchors),
        _node(
            "tra_reverse_range",
            "TRA反推区",
            "input",
            "TRA 区间或小于 -11.74deg 的反推手柄条件。",
            tra_anchors,
            parameters=[_deterministic_param("tra_lock_deg", "TRA锁释放门限", "deg", -11.74, tra_anchors, min_value=-20.0, max_value=0.0)],
        ),
        _node("logic1", "L1", "logic", "工作逻辑1：根据 RA/SW1 等条件生成 TLS 解锁链路。", l1_anchors),
        _node("tls_cmd", "TLS", "output", "TLS/115VAC 解锁或供电命令。", tls_anchors),
        _node("logic2", "L2", "logic", "工作逻辑2：根据 SW2 等条件生成 ETRAC 链路。", l2_anchors),
        _node("etrac_cmd", "ETRAC", "output", "ETRAC/540VDC 相关命令。", _dedupe_anchors(l2_anchors + tls_anchors)),
        _node("logic3", "L3", "logic", "工作逻辑3：汇合 TLS/PLS/执行链路。", l3_anchors),
        _node("pls_pdu_cmd", "PLS/PDU", "output", "PLS 供电与 PDU 电机执行链路。", _dedupe_anchors(pls_anchors + l3_anchors)),
        _node(
            "vdt_90",
            "VDT 90%",
            "component",
            "VDT 反馈达到 90% 展开。",
            vdt_anchors,
            parameters=[_deterministic_param("vdt_deploy_percent", "VDT展开", "%", 90.0, vdt_anchors, max_value=100.0)],
        ),
        _node("logic4", "L4", "logic", "工作逻辑4：确认展开反馈后释放 THR_LOCK。", l4_anchors),
        _node("thr_lock_release", "THR_LOCK release", "output", "油门锁释放输出。", lock_anchors),
    ]
    edges = [
        _edge("edge_ra_l1", "ra_lt_6ft", "logic1", "高度门限", _dedupe_anchors(ra_anchors + l1_anchors)),
        _edge("edge_sw1_l1", "sw1", "logic1", "SW1 条件", _dedupe_anchors(sw1_anchors + l1_anchors)),
        _edge("edge_l1_tls", "logic1", "tls_cmd", "TLS 输出", l1_anchors),
        _edge("edge_sw2_l2", "sw2", "logic2", "SW2 条件", _dedupe_anchors(sw2_anchors + l2_anchors)),
        _edge("edge_l2_etrac", "logic2", "etrac_cmd", "ETRAC 输出", l2_anchors),
        _edge("edge_tls_l3", "tls_cmd", "logic3", "TLS 反馈", _dedupe_anchors(tls_anchors + l3_anchors)),
        _edge("edge_l2_l3", "logic2", "logic3", "执行链汇合", _dedupe_anchors(l2_anchors + l3_anchors)),
        _edge("edge_l3_pls_pdu", "logic3", "pls_pdu_cmd", "PLS/PDU 输出", l3_anchors),
        _edge("edge_pls_pdu_vdt", "pls_pdu_cmd", "vdt_90", "展开反馈", _dedupe_anchors(pls_anchors + vdt_anchors)),
        _edge("edge_vdt_l4", "vdt_90", "logic4", "90% 反馈", _dedupe_anchors(vdt_anchors + l4_anchors)),
        _edge("edge_tra_l4", "tra_reverse_range", "logic4", "TRA 锁释放门限", _dedupe_anchors(tra_anchors + l4_anchors)),
        _edge("edge_l4_thr_lock", "logic4", "thr_lock_release", "释放", _dedupe_anchors(l4_anchors + lock_anchors)),
    ]
    requirement_groups = [
        {"id": "logic1", "label": "L1", "source_anchors": l1_anchors, "node_ids": ["ra_lt_6ft", "sw1", "logic1", "tls_cmd"]},
        {"id": "logic2", "label": "L2", "source_anchors": l2_anchors, "node_ids": ["sw2", "logic2", "etrac_cmd"]},
        {"id": "logic3", "label": "L3", "source_anchors": l3_anchors, "node_ids": ["tls_cmd", "logic2", "logic3", "pls_pdu_cmd"]},
        {"id": "logic4", "label": "L4", "source_anchors": l4_anchors, "node_ids": ["vdt_90", "tra_reverse_range", "logic4", "thr_lock_release"]},
    ]
    source_scope = _deterministic_source_scope(records)
    key_outputs = ["L1-L4 已分组", "RA/SW/TRA/VDT 门限已保留"]
    if (source_scope.get("fault_injection") or {}).get("status") == "source_deferred":
        key_outputs.append("故障注入按源文档暂缓")
    return {
        "available": True,
        "version": 1,
        "strategy": "docx_l1_l4_rule_preparse",
        "summary_zh": "本地预解析已从 DOCX 正文抽出 L1-L4、关键门限和输出链路，可进入初版绘图。",
        "nodes": nodes,
        "edges": edges,
        "requirement_groups": requirement_groups,
        "source_scope": source_scope,
        "reading_burden": {
            "current_action_zh": "先检查 L1-L4 分组和门限是否贴合源文档。",
            "key_outputs_zh": key_outputs[:3],
            "detail_policy_zh": "节点、连线、参数和来源锚点默认折叠到详情区。",
        },
        "detected": {
            "logic_ids": present_logic_ids,
            "signal_ids": present_signal_ids,
            "anchor_count": len(records),
        },
    }


def _normalize_questions(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    questions: list[dict[str, str]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        prompt = _str(item.get("prompt_zh") or item.get("prompt"))
        if not prompt:
            continue
        questions.append(
            {
                "id": _str(item.get("id"), f"q{index}") or f"q{index}",
                "prompt_zh": prompt,
                "rationale_zh": _str(item.get("rationale_zh") or item.get("rationale")),
                "blocks": _str(item.get("blocks"), "logic_builder") or "logic_builder",
            }
        )
    return questions


def _normalize_source_anchors(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    anchors: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        anchor_id = _str(item.get("id") or item.get("anchor_id"))
        quote = _str(item.get("quote_zh") or item.get("quote"))
        if not anchor_id and not quote:
            continue
        anchors.append(
            {
                "id": anchor_id[:32] or f"A{len(anchors) + 1:02d}",
                "kind": _str(item.get("kind"), "正文条件")[:32],
                "origin": _str(item.get("origin"), "model_inference")[:32],
                "quote_zh": quote[:SOURCE_ANCHOR_QUOTE_CHARS],
            }
        )
        if len(anchors) >= 6:
            break
    return _dedupe_anchors(anchors)


def _normalize_parameters(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    params: list[dict[str, Any]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        param_id = _str(item.get("id"), f"param_{index}") or f"param_{index}"
        params.append(
            {
                "id": param_id,
                "label": _str(item.get("label"), param_id) or param_id,
                "unit": _str(item.get("unit")),
                "min": item.get("min"),
                "max": item.get("max"),
                "default": item.get("default"),
                "source_hint": _str(item.get("source_hint")),
                "source_anchors": _normalize_source_anchors(item.get("source_anchors")),
            }
        )
    return params


def _normalize_nodes(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    nodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        node_id = _str(item.get("id"), f"node_{index}") or f"node_{index}"
        if node_id in seen:
            node_id = f"{node_id}_{index}"
        seen.add(node_id)
        nodes.append(
            {
                "id": node_id,
                "label": _str(item.get("label"), node_id) or node_id,
                "node_kind": _str(item.get("node_kind"), "logic") or "logic",
                "description_zh": _str(item.get("description_zh") or item.get("description")),
                "parameters": _normalize_parameters(item.get("parameters")),
                "source_anchors": _normalize_source_anchors(item.get("source_anchors")),
                "provenance": _str(item.get("provenance"), "model_inference") or "model_inference",
            }
        )
    return nodes


def _normalize_edges(value: Any, node_ids: set[str]) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    edges: list[dict[str, str]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        source = _str(item.get("source"))
        target = _str(item.get("target"))
        if not source or not target:
            continue
        edges.append(
            {
                "id": _str(item.get("id"), f"edge_{index}") or f"edge_{index}",
                "source": source,
                "target": target,
                "label": _str(item.get("label")),
                "endpoint_status": "resolved" if source in node_ids and target in node_ids else "concept_unresolved",
                "source_anchors": _normalize_source_anchors(item.get("source_anchors")),
                "provenance": _str(item.get("provenance"), "model_inference") or "model_inference",
            }
        )
    return edges


def _normalize_model_payload(raw_content: str) -> dict[str, Any]:
    stripped = _strip_model_json(raw_content)
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError as exc:
        try:
            payload = _extract_json_object(stripped)
        except json.JSONDecodeError as embedded_exc:
            raise RequirementsIntakeError(
                "llm_json_error",
                "Model response could not be parsed as the required concept JSON.",
                status_code=502,
                details={
                    "reason_type": type(exc).__name__,
                    "response_chars": len(stripped),
                    "embedded_json_found": False,
                },
            ) from embedded_exc
    if not isinstance(payload, dict):
        raise RequirementsIntakeError("llm_json_error", "Model response JSON must be an object.", status_code=502)
    nodes = _normalize_nodes(payload.get("concept_logic_nodes"))
    node_ids = {node["id"] for node in nodes}
    reconstruction_target = _str(payload.get("reconstruction_target"))
    if reconstruction_target != THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET:
        reconstruction_target = ""
    return {
        "summary_zh": _str(payload.get("summary_zh")),
        "document_assumptions": _str_list(payload.get("document_assumptions")),
        "open_questions": _normalize_questions(payload.get("open_questions")),
        "concept_logic_nodes": nodes,
        "concept_edges": _normalize_edges(payload.get("concept_edges"), node_ids),
        "ready_for_logic_builder": bool(payload.get("ready_for_logic_builder")) and bool(nodes),
        "reconstruction_target": reconstruction_target,
    }


def _payload_from_deterministic_preparse(local_facts: dict[str, Any], *, reason: str) -> dict[str, Any]:
    return {
        "summary_zh": _str(local_facts.get("summary_zh"), "本地预解析已生成可绘图 L1-L4 结构。"),
        "document_assumptions": [
            "本地规则仅从 DOCX 正文中出现的 L1-L4、信号名和门限抽取概念结构。",
            "嵌入 Visio 若存在，只能作为结构辅助；正文条件仍是条件来源。",
        ],
        "open_questions": [],
        "concept_logic_nodes": local_facts.get("nodes") or [],
        "concept_edges": local_facts.get("edges") or [],
        "ready_for_logic_builder": True,
        "reconstruction_target": "",
        "requirement_groups": local_facts.get("requirement_groups") or [],
        "source_scope": local_facts.get("source_scope") or {},
        "reading_burden": local_facts.get("reading_burden") or {},
        "deterministic_preparse": {
            "available": True,
            "applied": True,
            "reason": reason,
            "strategy": _str(local_facts.get("strategy"), "docx_l1_l4_rule_preparse"),
            "node_count": len(local_facts.get("nodes") or []),
            "edge_count": len(local_facts.get("edges") or []),
            "candidate_nodes": local_facts.get("nodes") or [],
            "candidate_edges": local_facts.get("edges") or [],
            "detected": local_facts.get("detected") or {},
        },
    }


def build_local_preparse_payload(document_text: str, *, document_name: str = "") -> dict[str, Any]:
    text = document_text.strip() if isinstance(document_text, str) else ""
    if not text:
        raise RequirementsIntakeError("missing_document_text", "document_text must be a non-empty string.")
    if len(text) > MAX_REQUIREMENTS_TEXT_CHARS:
        raise RequirementsIntakeError(
            "document_text_too_large",
            f"document_text exceeds {MAX_REQUIREMENTS_TEXT_CHARS} characters.",
            status_code=413,
            details={"max_chars": MAX_REQUIREMENTS_TEXT_CHARS},
        )

    local_facts = _deterministic_l1_l4_preparse(text)
    text_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if local_facts.get("available"):
        normalized = _payload_from_deterministic_preparse(local_facts, reason="local_preparse_first")
    else:
        normalized = {
            "summary_zh": "本地预解析未找到完整 L1-L4 结构，等待 DeepSeek live 分析补全。",
            "document_assumptions": [
                "本地规则只做可验证正文信号抽取；不完整时不会猜测为真值。",
            ],
            "open_questions": [],
            "concept_logic_nodes": [],
            "concept_edges": [],
            "ready_for_logic_builder": False,
            "reconstruction_target": "",
            "source_scope": local_facts.get("source_scope") or {},
            "deterministic_preparse": {
                "available": False,
                "applied": False,
                "reason": _str(local_facts.get("reason"), "local_preparse_not_available"),
                "present_logic_ids": local_facts.get("present_logic_ids") or [],
                "present_signal_ids": local_facts.get("present_signal_ids") or [],
            },
        }
    ready = bool(normalized.get("ready_for_logic_builder"))
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_intake_analysis_v1.schema.json",
        "kind": REQUIREMENTS_INTAKE_KIND,
        "version": REQUIREMENTS_INTAKE_VERSION,
        "status": "ready_for_logic_builder" if ready else "needs_clarification",
        "source_document": {
            "name": document_name or "pasted-requirements.txt",
            "text_chars": len(text),
            "sha256": text_sha,
        },
        "analysis_input": {
            "input_chars": len(text),
            "original_chars": len(text),
            "compacted": False,
            "strategy": "local_preparse_only",
        },
        "llm": {
            "provider": "local-preparse",
            "model": "deterministic-docx-l1-l4",
            "api_base": "",
            "key_source": "",
            "response_source": "deterministic_preparse",
        },
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
        **normalized,
        "ready_for_logic_builder": ready,
    }


def _node_anchor_map(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        _str(item.get("id")): item
        for item in nodes
        if isinstance(item, dict) and _str(item.get("id"))
    }


_LOCAL_NODE_MATCHERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ra_lt_6ft", _SIGNAL_PATTERNS["ra_lt_6ft"]),
    ("sw2", _SIGNAL_PATTERNS["sw2"]),
    ("sw1", _SIGNAL_PATTERNS["sw1"]),
    ("tra_reverse_range", _SIGNAL_PATTERNS["tra"]),
    ("vdt_90", _SIGNAL_PATTERNS["vdt90"]),
    ("tls_cmd", _SIGNAL_PATTERNS["tls"]),
    ("pls_pdu_cmd", _SIGNAL_PATTERNS["pls"]),
    ("thr_lock_release", _SIGNAL_PATTERNS["thr_lock_release"]),
    ("logic1", _L1_L4_PATTERNS["logic1"]),
    ("logic2", _L1_L4_PATTERNS["logic2"]),
    ("logic3", _L1_L4_PATTERNS["logic3"]),
    ("logic4", _L1_L4_PATTERNS["logic4"]),
)


def _model_node_search_text(node: dict[str, Any]) -> str:
    parts = [
        _str(node.get("id")),
        _str(node.get("label")),
        _str(node.get("description_zh")),
    ]
    parameters = node.get("parameters")
    if isinstance(parameters, list):
        for param in parameters:
            if isinstance(param, dict):
                parts.append(_str(param.get("id")))
                parts.append(_str(param.get("label")))
    return " ".join(part for part in parts if part)


def _matching_local_node_for_model_node(
    model_node: dict[str, Any],
    local_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    exact = local_by_id.get(_str(model_node.get("id")))
    if exact:
        return exact
    search_text = _model_node_search_text(model_node)
    if not search_text:
        return {}
    for local_id, pattern in _LOCAL_NODE_MATCHERS:
        if pattern.search(search_text):
            return local_by_id.get(local_id, {})
    return {}


def _edge_anchor_map(edges: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (_str(item.get("source")), _str(item.get("target"))): item
        for item in edges
        if isinstance(item, dict) and _str(item.get("source")) and _str(item.get("target"))
    }


def _enrich_with_deterministic_preparse(normalized: dict[str, Any], local_facts: dict[str, Any]) -> dict[str, Any]:
    if not local_facts.get("available"):
        source_scope = local_facts.get("source_scope") if isinstance(local_facts, dict) else None
        return {
            **normalized,
            **({"source_scope": source_scope} if source_scope else {}),
        }

    local_nodes = local_facts.get("nodes") or []
    local_edges = local_facts.get("edges") or []
    model_nodes = normalized.get("concept_logic_nodes") or []
    model_edges = normalized.get("concept_edges") or []
    model_drawable = bool(normalized.get("ready_for_logic_builder")) and bool(model_nodes) and bool(model_edges)
    model_empty = not _str(normalized.get("summary_zh")) and not model_nodes and not model_edges and not normalized.get("open_questions")
    if not model_drawable:
        reason = "model_output_not_drawable"
        if model_empty:
            reason = "model_output_empty"
        return _payload_from_deterministic_preparse(local_facts, reason=reason)

    local_by_id = _node_anchor_map(local_nodes)
    local_edges_by_pair = _edge_anchor_map(local_edges)
    enriched_nodes: list[dict[str, Any]] = []
    for node in model_nodes:
        local_node = _matching_local_node_for_model_node(node, local_by_id)
        enriched = dict(node)
        if not enriched.get("source_anchors") and local_node.get("source_anchors"):
            enriched["source_anchors"] = local_node["source_anchors"]
            enriched["provenance"] = local_node.get("provenance", "docx_body_condition")
        enriched_nodes.append(enriched)

    enriched_edges: list[dict[str, Any]] = []
    for edge_item in model_edges:
        local_edge = local_edges_by_pair.get((_str(edge_item.get("source")), _str(edge_item.get("target"))), {})
        enriched = dict(edge_item)
        if not enriched.get("source_anchors") and local_edge.get("source_anchors"):
            enriched["source_anchors"] = local_edge["source_anchors"]
            enriched["provenance"] = local_edge.get("provenance", "docx_body_condition")
        enriched_edges.append(enriched)

    return {
        **normalized,
        "concept_logic_nodes": enriched_nodes,
        "concept_edges": enriched_edges,
        "requirement_groups": local_facts.get("requirement_groups") or [],
        "source_scope": local_facts.get("source_scope") or {},
        "reading_burden": local_facts.get("reading_burden") or {},
        "deterministic_preparse": {
            "available": True,
            "applied": False,
            "reason": "model_output_drawable",
            "strategy": _str(local_facts.get("strategy"), "docx_l1_l4_rule_preparse"),
            "node_count": len(local_nodes),
            "edge_count": len(local_edges),
            "candidate_nodes": local_nodes,
            "candidate_edges": local_edges,
            "detected": local_facts.get("detected") or {},
        },
    }


def _fallback_open_questions(normalized: dict[str, Any], input_meta: dict[str, Any]) -> list[dict[str, str]]:
    questions = list(normalized.get("open_questions") or [])
    if questions:
        return questions

    nodes = normalized.get("concept_logic_nodes") or []
    edges = normalized.get("concept_edges") or []
    summary = _str(normalized.get("summary_zh"))
    fallbacks: list[dict[str, str]] = []
    if not summary:
        fallbacks.append(
            {
                "id": "clarify_control_goal",
                "prompt_zh": "请用一句话确认这个需求文档要控制的对象、触发动作和最终输出命令分别是什么？",
                "rationale_zh": "模型没有提取到可用摘要，无法判断后续逻辑图的控制目标。",
                "blocks": "requirements_understanding",
            }
        )
    if not nodes:
        fallbacks.append(
            {
                "id": "clarify_io_signals",
                "prompt_zh": "请列出最关键的输入信号、输出命令和中间逻辑状态；每个信号请注明单位或真假语义。",
                "rationale_zh": "没有概念节点候选时，逻辑链路绘制模块无法生成节点。",
                "blocks": "logic_builder",
            }
        )
    if nodes and not edges:
        fallbacks.append(
            {
                "id": "clarify_logic_edges",
                "prompt_zh": "请确认这些输入信号如何组合成输出命令：哪些条件是 AND、OR、NOT，是否存在顺序/锁存关系？",
                "rationale_zh": "已有节点但没有连线候选，无法进入可追溯逻辑链路绘制。",
                "blocks": "logic_builder",
            }
        )
    if input_meta.get("compacted"):
        fallbacks.append(
            {
                "id": "clarify_compacted_sections",
                "prompt_zh": "这份文档较长，系统只抽取了 head/key-lines/tail。未覆盖章节是否还包含额外输入、输出、门限或故障逻辑？",
                "rationale_zh": "长文档压缩输入不能把未覆盖章节当作已确认真值。",
                "blocks": "document_coverage",
            }
        )
    if not fallbacks:
        fallbacks.append(
            {
                "id": "clarify_readiness_gate",
                "prompt_zh": "请确认当前摘要、概念节点和连线是否已经足够作为初版逻辑图草稿；如果不够，请补充缺失的控制条件。",
                "rationale_zh": "模型认为还不能进入下一步，但没有给出明确问题；需要工程师确认阻塞点。",
                "blocks": "logic_builder",
            }
        )
    return fallbacks


def _apply_readiness_gate(normalized: dict[str, Any], input_meta: dict[str, Any]) -> dict[str, Any]:
    nodes = normalized.get("concept_logic_nodes") or []
    existing_questions = normalized.get("open_questions") or []
    model_ready = bool(normalized.get("ready_for_logic_builder")) and bool(nodes)
    questions = [] if model_ready and not existing_questions else _fallback_open_questions(normalized, input_meta)
    ready = model_ready and not questions
    return {
        **normalized,
        "open_questions": questions,
        "ready_for_logic_builder": ready,
    }


def analyze_requirements_text(
    document_text: str,
    *,
    document_name: str = "",
    provider: str = "deepseek",
    request_post: RequestPost | None = None,
) -> dict[str, Any]:
    text = document_text.strip() if isinstance(document_text, str) else ""
    if not text:
        raise RequirementsIntakeError("missing_document_text", "document_text must be a non-empty string.")
    if len(text) > MAX_REQUIREMENTS_TEXT_CHARS:
        raise RequirementsIntakeError(
            "document_text_too_large",
            f"document_text exceeds {MAX_REQUIREMENTS_TEXT_CHARS} characters.",
            status_code=413,
            details={"max_chars": MAX_REQUIREMENTS_TEXT_CHARS},
        )

    cfg = _provider_config(provider)
    analysis_text, input_meta = _compact_document_for_llm(text)
    local_preparse = _deterministic_l1_l4_preparse(text)
    if local_preparse.get("available"):
        input_meta["deterministic_preparse"] = {
            "available": True,
            "strategy": local_preparse.get("strategy"),
            "node_count": len(local_preparse.get("nodes") or []),
            "edge_count": len(local_preparse.get("edges") or []),
            "requirement_groups": [
                {
                    "id": group.get("id"),
                    "label": group.get("label"),
                    "source_anchor_ids": _anchor_ids(group.get("source_anchors") or []),
                }
                for group in (local_preparse.get("requirement_groups") or [])
                if isinstance(group, dict)
            ],
            "source_scope": local_preparse.get("source_scope") or {},
        }
    content = _call_chat_completion(
        cfg,
        _analysis_prompt(analysis_text, document_name, input_meta),
        request_post=request_post,
    )
    normalized = _normalize_model_payload(content)
    normalized = _enrich_with_deterministic_preparse(normalized, local_preparse)
    normalized = _apply_readiness_gate(normalized, input_meta)
    ready = bool(normalized["ready_for_logic_builder"])
    text_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_intake_analysis_v1.schema.json",
        "kind": REQUIREMENTS_INTAKE_KIND,
        "version": REQUIREMENTS_INTAKE_VERSION,
        "status": "ready_for_logic_builder" if ready else "needs_clarification",
        "source_document": {
            "name": document_name or "pasted-requirements.txt",
            "text_chars": len(text),
            "sha256": text_sha,
        },
        "analysis_input": input_meta,
        "llm": {
            "provider": cfg.provider,
            "model": cfg.model,
            "api_base": cfg.api_base,
            "key_source": cfg.key_source,
            "response_source": "live_llm",
        },
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
        **normalized,
        "ready_for_logic_builder": ready,
    }
