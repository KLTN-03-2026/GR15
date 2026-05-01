from __future__ import annotations

import json
import time
from typing import Iterator

from app.core.config import settings
from app.core.logger import get_logger
from app.providers.chat_ollama_provider import OllamaChatProvider
from app.providers.chat_openai_provider import OpenAIChatProvider
from app.providers.chat_template_provider import TemplateChatProvider
from app.services.chatbot_intent_engine import (
    DETERMINISTIC_INTENTS,
    INTENT_OUT_OF_SCOPE,
    MODEL_PREFERRED_INTENTS,
    OUT_OF_SCOPE_MESSAGE,
    build_template_answer,
    resolve_intent,
    should_use_fast_path,
)


logger = get_logger(__name__)

MODEL_VERSION = "chatbot_v1"


def generate_career_chat_reply(
    session_id: int,
    message: str,
    *,
    history: list[dict] | None = None,
    context: dict | None = None,
    force_model: bool = False,
) -> dict:
    logger.info("Generate chatbot reply for session_id=%s", session_id)
    history = history or []
    context = context or {}
    intent = resolve_intent(message, history=history, context=context)
    context = {**context, "_chat_intent": intent}

    if intent == INTENT_OUT_OF_SCOPE:
        return {
            "success": True,
            "model_version": f"{MODEL_VERSION}::guardrail",
            "data": {
                "answer": OUT_OF_SCOPE_MESSAGE,
                "provider": "guardrail",
                "guardrail_triggered": True,
                "intent": intent,
            },
            "error": None,
        }

    provider_name, provider = _resolve_provider()
    prefers_model = provider_name in {"ollama", "openai"}

    if intent in DETERMINISTIC_INTENTS and not (force_model and intent in MODEL_PREFERRED_INTENTS):
        answer = _normalize_answer(build_template_answer(message, context, history, intent))
        return {
            "success": True,
            "model_version": f"{MODEL_VERSION}::intent_template",
            "data": {
                "answer": answer,
                "provider": "intent_template",
                "guardrail_triggered": False,
                "intent": intent,
            },
            "error": None,
        }

    if not prefers_model and not force_model and should_use_fast_path(message, intent=intent):
        answer = _normalize_answer(build_template_answer(message, context, history, intent))
        return {
            "success": True,
            "model_version": f"{MODEL_VERSION}::fast_template",
            "data": {
                "answer": answer,
                "provider": "fast_template",
                "guardrail_triggered": False,
                "intent": intent,
            },
            "error": None,
        }

    try:
        answer = _normalize_answer(provider.generate(message, context, history))
    except Exception as exc:
        logger.warning("Chat provider failed, fallback to template. provider=%s error=%s", provider_name, exc)
        answer = _normalize_answer(build_template_answer(message, context, history, intent))
        provider_name = "template_fallback"

    if _looks_like_provider_guardrail(answer):
        answer = _normalize_answer(build_template_answer(message, context, history, intent))
        provider_name = "template_fallback"

    return {
        "success": True,
        "model_version": f"{MODEL_VERSION}::{provider_name}",
        "data": {
            "answer": answer,
            "provider": provider_name,
            "guardrail_triggered": False,
            "intent": intent,
        },
        "error": None,
    }


def stream_career_chat_reply(
    session_id: int,
    message: str,
    *,
    history: list[dict] | None = None,
    context: dict | None = None,
    force_model: bool = False,
) -> Iterator[str]:
    history = history or []
    context = context or {}
    intent = resolve_intent(message, history=history, context=context)
    context = {**context, "_chat_intent": intent}

    if intent == INTENT_OUT_OF_SCOPE:
        yield _sse_event(
            "meta",
            {
                "success": True,
                "model_version": f"{MODEL_VERSION}::guardrail",
                "provider": "guardrail",
                "guardrail_triggered": True,
                "intent": intent,
            },
        )
        yield from _emit_chunked_sse(OUT_OF_SCOPE_MESSAGE)
        yield _sse_event(
            "done",
            {
                "answer": OUT_OF_SCOPE_MESSAGE,
                "model_version": f"{MODEL_VERSION}::guardrail",
                "provider": "guardrail",
                "guardrail_triggered": True,
                "intent": intent,
            },
        )
        return

    provider_name, provider = _resolve_provider()
    prefers_model = provider_name in {"ollama", "openai"}

    if intent in DETERMINISTIC_INTENTS and not (force_model and intent in MODEL_PREFERRED_INTENTS):
        answer = _normalize_answer(build_template_answer(message, context, history, intent))
        yield _sse_event(
            "meta",
            {
                "success": True,
                "model_version": f"{MODEL_VERSION}::intent_template",
                "provider": "intent_template",
                "guardrail_triggered": False,
                "intent": intent,
            },
        )
        yield from _emit_chunked_sse(answer)
        yield _sse_event(
            "done",
            {
                "answer": answer,
                "model_version": f"{MODEL_VERSION}::intent_template",
                "provider": "intent_template",
                "guardrail_triggered": False,
                "intent": intent,
            },
        )
        return

    if not prefers_model and not force_model and should_use_fast_path(message, intent=intent):
        answer = _normalize_answer(build_template_answer(message, context, history, intent))
        yield _sse_event(
            "meta",
            {
                "success": True,
                "model_version": f"{MODEL_VERSION}::fast_template",
                "provider": "fast_template",
                "guardrail_triggered": False,
                "intent": intent,
            },
        )
        yield from _emit_chunked_sse(answer)
        yield _sse_event(
            "done",
            {
                "answer": answer,
                "model_version": f"{MODEL_VERSION}::fast_template",
                "provider": "fast_template",
                "guardrail_triggered": False,
                "intent": intent,
            },
        )
        return

    model_version = f"{MODEL_VERSION}::{provider_name}"

    yield _sse_event(
        "meta",
        {
            "success": True,
            "model_version": model_version,
            "provider": provider_name,
            "guardrail_triggered": False,
            "intent": intent,
        },
    )

    chunks: list[str] = []
    try:
        if hasattr(provider, "stream"):
            for chunk in provider.stream(message, context, history):
                if chunk:
                    chunks.append(chunk)
                    yield _sse_event("chunk", {"content": chunk})
        else:
            answer = _normalize_answer(provider.generate(message, context, history))
            for chunk in _chunk_text(answer):
                chunks.append(chunk)
                yield _sse_event("chunk", {"content": chunk})
                time.sleep(0.035)
    except Exception as exc:
        logger.warning("Chat stream provider failed, fallback to generate. provider=%s error=%s", provider_name, exc)
        try:
            answer = _normalize_answer(provider.generate(message, context, history))
            for chunk in _chunk_text(answer):
                chunks.append(chunk)
                yield _sse_event("chunk", {"content": chunk})
                time.sleep(0.035)
        except Exception as fallback_exc:
            yield _sse_event(
                "error",
                {
                    "message": str(fallback_exc),
                    "model_version": model_version,
                    "provider": provider_name,
                    "intent": intent,
                },
            )
            return

    final_answer = _normalize_answer(
        "".join(chunks).strip() if provider_name in {"ollama", "openai"} else " ".join(chunks).strip()
    )
    if _looks_like_provider_guardrail(final_answer):
        provider_name = "template_fallback"
        model_version = f"{MODEL_VERSION}::{provider_name}"
        final_answer = _normalize_answer(build_template_answer(message, context, history, intent))

    yield _sse_event(
        "done",
        {
            "answer": final_answer,
            "model_version": model_version,
            "provider": provider_name,
            "guardrail_triggered": False,
            "intent": intent,
        },
    )


def _resolve_provider():
    provider = settings.chatbot_provider
    if provider == "ollama":
        return provider, OllamaChatProvider()
    if provider == "openai":
        return provider, OpenAIChatProvider()
    return "template", TemplateChatProvider()


def _chunk_text(text: str, chunk_size: int = 60) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []
    current = ""

    for line in text.splitlines(keepends=True):
        tentative = f"{current}{line}"
        if len(tentative) <= chunk_size:
            current = tentative
            continue

        if current:
            chunks.append(current)
            current = ""

        while len(line) > chunk_size:
            chunks.append(line[:chunk_size])
            line = line[chunk_size:]

        current = line

    if current:
        chunks.append(current)

    return chunks


def _emit_chunked_sse(text: str, delay_seconds: float = 0.04) -> Iterator[str]:
    for chunk in _chunk_text(text):
        yield _sse_event("chunk", {"content": chunk})
        time.sleep(delay_seconds)


def _normalize_answer(text: str) -> str:
    cleaned = (
        text.replace("**", "")
        .replace("__", "")
        .replace("`", "")
        .replace("#", "")
        .strip()
    )

    normalized_lines: list[str] = []
    previous_blank = False
    for raw_line in cleaned.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            if normalized_lines and not previous_blank:
                normalized_lines.append("")
            previous_blank = True
            continue

        normalized_lines.append(line)
        previous_blank = False

    cleaned = "\n".join(normalized_lines).strip()
    cleaned = _normalize_vietnamese_terms(cleaned)
    cleaned = _trim_incomplete_tail(cleaned)

    if not cleaned:
        return cleaned

    if cleaned[-1] in ".!?":
        return cleaned

    last_stop = max(cleaned.rfind("."), cleaned.rfind("!"), cleaned.rfind("?"))
    if last_stop >= 0 and last_stop >= int(len(cleaned) * 0.6):
        return cleaned[: last_stop + 1].strip()

    return f"{cleaned}."


def _normalize_vietnamese_terms(text: str) -> str:
    replacements = {
        "Next 30 days": "30 ngày đầu",
        "Next 60 days": "60 ngày",
        "Next 90 days": "90 ngày",
        "next 30 days": "30 ngày đầu",
        "next 60 days": "60 ngày",
        "next 90 days": "90 ngày",
        "Career Path Simulator": "Mô phỏng lộ trình nghề nghiệp",
        "career path simulator": "mô phỏng lộ trình nghề nghiệp",
        "mini project": "dự án nhỏ",
        "Mini project": "Dự án nhỏ",
        "case study": "bài phân tích tình huống",
        "Case study": "Bài phân tích tình huống",
        "portfolio": "hồ sơ dự án",
        "Portfolio": "Hồ sơ dự án",
        "matching": "đối sánh",
        "Matching": "Đối sánh",
        "apply": "ứng tuyển",
        "Apply": "Ứng tuyển",
        "cover letter": "thư xin việc",
        "Cover letter": "Thư xin việc",
        "job mục tiêu": "vị trí mục tiêu",
        "job phù hợp": "vị trí phù hợp",
        "job gần nhất": "vị trí gần nhất",
        "job ": "công việc ",
        "Job ": "Công việc ",
        "skill gap": "khoảng cách kỹ năng",
        "Skill gap": "Khoảng cách kỹ năng",
    }
    output = text
    for source, target in replacements.items():
        output = output.replace(source, target)
    return output


def _looks_like_provider_guardrail(answer: str) -> bool:
    if not answer:
        return False

    normalized_answer = normalize_search_text(answer)
    normalized_guardrail = normalize_search_text(OUT_OF_SCOPE_MESSAGE)
    return normalized_guardrail[:80] in normalized_answer


def _trim_incomplete_tail(text: str) -> str:
    if not text:
        return text

    lines = [line.rstrip() for line in text.splitlines()]
    while lines:
        last_line = lines[-1].strip()
        if not last_line:
            lines.pop()
            continue

        if (
            last_line.endswith((":", ",", ";", "-", "/", "("))
            or last_line.count("(") > last_line.count(")")
            or len(last_line) <= 4
        ):
            lines.pop()
            continue

        break

    return "\n".join(lines).strip()


def _sse_event(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
