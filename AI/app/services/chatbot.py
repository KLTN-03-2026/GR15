from __future__ import annotations

import json
import time
from typing import Iterator

from app.core.config import settings
from app.core.logger import get_logger
from app.providers.chat_ollama_provider import OllamaChatProvider
from app.providers.chat_openai_provider import OpenAIChatProvider
from app.services.chatbot_intent_engine import (
    DETERMINISTIC_INTENTS,
    INTENT_OUT_OF_SCOPE,
    MODEL_PREFERRED_INTENTS,
    OUT_OF_SCOPE_MESSAGE,
    build_template_answer,
    ensure_chat_mapping,
    normalize_chat_history_items,
    resolve_intent,
    should_use_fast_path,
)
from app.services.skill_catalog import normalize_search_text
from app.services.vietnamese_text import normalize_vietnamese_ai_text

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
    history = normalize_chat_history_items(history)
    context = ensure_chat_mapping(context)
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

    template_provider = _resolve_template_provider(message, intent=intent)
    if template_provider:
        answer = _normalize_answer(build_template_answer(message, context, history, intent))
        return {
            "success": True,
            "model_version": f"{MODEL_VERSION}::{template_provider}",
            "data": {
                "answer": answer,
                "provider": template_provider,
                "guardrail_triggered": False,
                "intent": intent,
            },
            "error": None,
        }

    provider_name, provider = _resolve_provider()

    try:
        answer = _normalize_answer(provider.generate(message, context, history))
    except Exception as exc:
        logger.exception("Required chat LLM provider failed. provider=%s", provider_name)
        return {
            "success": False,
            "model_version": f"{MODEL_VERSION}::{provider_name}",
            "data": {},
            "error": f"Không thể gọi LLM cho chatbot: {exc}",
        }

    if _looks_like_provider_guardrail(answer) or _looks_off_intent(answer, intent=intent):
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
    history = normalize_chat_history_items(history)
    context = ensure_chat_mapping(context)
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

    template_provider = _resolve_template_provider(message, intent=intent)
    if template_provider:
        answer = _normalize_answer(build_template_answer(message, context, history, intent))
        yield _sse_event(
            "meta",
            {
                "success": True,
                "model_version": f"{MODEL_VERSION}::{template_provider}",
                "provider": template_provider,
                "guardrail_triggered": False,
                "intent": intent,
            },
        )
        yield from _emit_chunked_sse(answer)
        yield _sse_event(
            "done",
            {
                "answer": answer,
                "model_version": f"{MODEL_VERSION}::{template_provider}",
                "provider": template_provider,
                "guardrail_triggered": False,
                "intent": intent,
            },
        )
        return

    provider_name, provider = _resolve_provider()

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
        yield _sse_event(
            "error",
            {
                "message": f"Không thể gọi LLM cho chatbot: {exc}",
                "model_version": model_version,
                "provider": provider_name,
                "intent": intent,
            },
        )
        return

    final_answer = _normalize_answer(
        "".join(chunks).strip() if provider_name in {"ollama", "openai"} else " ".join(chunks).strip()
    )
    if _looks_like_provider_guardrail(final_answer) or _looks_off_intent(final_answer, intent=intent):
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
    provider = (settings.chatbot_provider or "ollama").strip().lower()
    if provider == "ollama":
        return provider, OllamaChatProvider()
    if provider == "openai":
        return provider, OpenAIChatProvider()
    logger.warning("Unknown CHATBOT_PROVIDER=%s, forcing ollama LLM provider.", settings.chatbot_provider)
    return "ollama", OllamaChatProvider()


def _resolve_template_provider(message: str, *, intent: str) -> str | None:
    if should_use_fast_path(message, intent=intent):
        return "fast_template"

    if intent in DETERMINISTIC_INTENTS and intent not in MODEL_PREFERRED_INTENTS:
        return "intent_template"

    return None


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
    cleaned = normalize_vietnamese_ai_text(text, ensure_punctuation=False)

    if not cleaned:
        return cleaned

    if cleaned[-1] in ".!?":
        return cleaned

    last_stop = max(cleaned.rfind("."), cleaned.rfind("!"), cleaned.rfind("?"))
    if last_stop >= 0 and last_stop >= int(len(cleaned) * 0.6):
        return cleaned[: last_stop + 1].strip()

    return f"{cleaned}."


def _looks_like_provider_guardrail(answer: str) -> bool:
    if not answer:
        return False

    normalized_answer = normalize_search_text(answer)
    normalized_guardrail = normalize_search_text(OUT_OF_SCOPE_MESSAGE)
    return normalized_guardrail[:80] in normalized_answer


def _looks_off_intent(answer: str, *, intent: str) -> bool:
    normalized_answer = normalize_search_text(answer)

    if intent != "career_path_simulator" and "mo phong lo trinh nghe nghiep 30/60/90 ngay" in normalized_answer:
        return True

    return False


def _sse_event(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
