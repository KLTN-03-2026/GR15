from __future__ import annotations

import json
from queue import Empty, Queue
import re
import time
from typing import Iterator

from app.core.config import settings
from app.core.logger import get_logger
from app.providers.chat_gemini_provider import GeminiChatProvider
from app.providers.chat_ollama_provider import OllamaChatProvider
from app.providers.chat_openai_provider import OpenAIChatProvider
from app.services.chatbot_intent_engine import (
    INTENT_OUT_OF_SCOPE,
    OUT_OF_SCOPE_MESSAGE,
    build_template_answer,
    ensure_chat_mapping,
    normalize_chat_history_items,
    resolve_intent,
)
from app.services.llm_timeout import TimeoutError, run_with_timeout
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
    history = normalize_chat_history_items(history)
    context = ensure_chat_mapping(context)
    intent = resolve_intent(message, history=history, context=context)
    context = {**context, "_chat_intent": intent}
    logger.info(
        "Generate chatbot reply session_id=%s intent=%s provider_path=resolver",
        session_id,
        intent,
    )

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
    logger.info(
        "Generate chatbot reply session_id=%s intent=%s provider=%s",
        session_id,
        intent,
        provider_name,
    )

    try:
        answer = _normalize_answer(_generate_with_timeout(provider, message, context, history))
    except TimeoutError:
        provider_name = "template_timeout_fallback"
        logger.warning(
            "Chatbot LLM timed out session_id=%s intent=%s fallback_provider=%s timeout_seconds=%s",
            session_id,
            intent,
            provider_name,
            settings.chatbot_llm_fallback_seconds,
        )
        answer = _normalize_answer(build_template_answer(message, context, history, intent))
    except Exception as exc:
        logger.exception("Required chat LLM provider failed. provider=%s", provider_name)
        return {
            "success": False,
            "model_version": f"{MODEL_VERSION}::{provider_name}",
            "data": {},
            "error": f"Không thể gọi LLM cho chatbot: {exc}",
        }

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
    logger.info("Stream chatbot reply session_id=%s intent=%s", session_id, intent)

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
    logger.info(
        "Stream chatbot reply session_id=%s intent=%s provider=%s",
        session_id,
        intent,
        provider_name,
    )

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
            stream_iter = _stream_with_first_chunk_timeout(provider, message, context, history)
            for chunk in stream_iter:
                if chunk:
                    chunks.append(chunk)
                    yield _sse_event("chunk", {"content": chunk})
        else:
            answer = _normalize_answer(_generate_with_timeout(provider, message, context, history))
            for chunk in _chunk_text(answer):
                chunks.append(chunk)
                yield _sse_event("chunk", {"content": chunk})
                time.sleep(0.035)
    except TimeoutError:
        provider_name = "template_timeout_fallback"
        model_version = f"{MODEL_VERSION}::{provider_name}"
        logger.warning(
            "Chatbot stream LLM timed out session_id=%s intent=%s fallback_provider=%s timeout_seconds=%s",
            session_id,
            intent,
            provider_name,
            settings.chatbot_llm_fallback_seconds,
        )
        final_answer = _normalize_answer(build_template_answer(message, context, history, intent))
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
        yield from _emit_chunked_sse(final_answer)
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
        return
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
        "".join(chunks).strip() if provider_name in {"ollama", "openai", "gemini"} else " ".join(chunks).strip()
    )
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
    if provider == "gemini":
        return provider, GeminiChatProvider()
    logger.warning("Unknown CHATBOT_PROVIDER=%s, forcing ollama LLM provider.", settings.chatbot_provider)
    return "ollama", OllamaChatProvider()


def _generate_with_timeout(provider, message: str, context: dict, history: list[dict]) -> str:
    return run_with_timeout(
        lambda: provider.generate(message, context, history),
        settings.chatbot_llm_fallback_seconds,
    )


def _stream_with_first_chunk_timeout(provider, message: str, context: dict, history: list[dict]) -> Iterator[str]:
    queue: Queue[tuple[str, str | BaseException | None]] = Queue()
    sentinel = ("done", None)

    def worker() -> None:
        try:
            for chunk in provider.stream(message, context, history):
                if chunk:
                    queue.put(("chunk", chunk))
            queue.put(sentinel)
        except BaseException as exc:  # noqa: BLE001 - surface provider exception to SSE handler
            queue.put(("error", exc))

    from concurrent.futures import ThreadPoolExecutor

    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(worker)
    first_chunk_seen = False
    try:
        while True:
            try:
                kind, payload = queue.get(timeout=settings.chatbot_llm_fallback_seconds if not first_chunk_seen else None)
            except Empty:
                raise TimeoutError()

            if kind == "done":
                return
            if kind == "error":
                raise payload if isinstance(payload, BaseException) else RuntimeError("Chatbot stream failed.")

            first_chunk_seen = True
            yield str(payload or "")
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def _chunk_text(text: str, chunk_size: int = 60) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []
    current = ""

    tokens = re.split(r"(\s+)", text)
    for token in tokens:
        if not token:
            continue
        tentative = f"{current}{token}"
        if len(tentative) <= chunk_size or not current:
            current = tentative
            if current.endswith(("\n", ". ", "! ", "? ", ": ")):
                chunks.append(current)
                current = ""
            continue

        chunks.append(current)
        current = token

    if current:
        chunks.append(current)

    return chunks


def _emit_chunked_sse(text: str, delay_seconds: float = 0.075) -> Iterator[str]:
    for chunk in _chunk_text(text, chunk_size=42):
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
