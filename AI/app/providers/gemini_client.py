from __future__ import annotations

import hashlib
import json
from json import JSONDecodeError
import re
import ssl
import threading
import time
from typing import Iterator
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import settings

try:
    import certifi
except ModuleNotFoundError:  # pragma: no cover - certifi co san trong nhieu moi truong Python
    certifi = None


_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where()) if certifi else None
_RATE_LOCK = threading.Lock()
_CACHE_LOCK = threading.Lock()
_LAST_REQUEST_AT = 0.0
_COOLDOWN_UNTIL = 0.0
_CACHE: dict[str, tuple[float, str]] = {}


def generate_text(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float = 0,
    format_json: bool = False,
    timeout: int | None = None,
) -> str:
    cache_key = _cache_key(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        format_json=format_json,
    )
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    payload = _build_payload(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        format_json=format_json,
    )
    _wait_for_rate_slot()
    body = _post_json(_gemini_url("generateContent"), payload, timeout=timeout or settings.gemini_timeout_seconds)
    data = json.loads(body)
    content = extract_text(data).strip()
    if format_json and content and not _looks_like_complete_json(content):
        retry_tokens = min(max_tokens * 2, 4096)
        if retry_tokens > max_tokens:
            retry_payload = _build_payload(
                system_prompt=system_prompt,
                user_prompt=(
                    f"{user_prompt}\n\n"
                    "Lần trả lời trước có dấu hiệu JSON bị cụt. "
                    "Hãy trả lại duy nhất một JSON object hoàn chỉnh, đóng đủ dấu ngoặc và dấu nháy."
                ),
                max_tokens=retry_tokens,
                temperature=0,
                format_json=True,
            )
            _wait_for_rate_slot()
            retry_body = _post_json(
                _gemini_url("generateContent"),
                retry_payload,
                timeout=timeout or settings.gemini_timeout_seconds,
            )
            retry_data = json.loads(retry_body)
            retry_content = extract_text(retry_data).strip()
            if retry_content:
                content = retry_content

    if not content:
        raise RuntimeError("Gemini không trả về nội dung.")
    _set_cached(cache_key, content)
    return content


def stream_text(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float = 0,
    format_json: bool = False,
    timeout: int | None = None,
) -> Iterator[str]:
    payload = _build_payload(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        format_json=format_json,
    )
    request = _build_request(_gemini_url("streamGenerateContent", stream=True), payload)
    _wait_for_rate_slot()

    try:
        with urlopen(request, timeout=timeout or settings.gemini_timeout_seconds, context=_SSL_CONTEXT) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line or line.startswith("event:"):
                    continue
                if not line.startswith("data:"):
                    continue

                payload_line = line[len("data:"):].strip()
                if payload_line == "[DONE]":
                    break

                try:
                    event_data = json.loads(payload_line)
                except JSONDecodeError:
                    continue

                chunk = extract_text(event_data)
                if chunk:
                    yield chunk
    except HTTPError as exc:
        error_body = _read_error_body(exc)
        if exc.code == 429:
            _activate_cooldown(_retry_after_seconds(error_body))
        raise RuntimeError(f"Gemini API trả về lỗi HTTP {exc.code}: {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Không gọi được Gemini API: {exc}") from exc


def extract_text(payload: dict | list) -> str:
    if isinstance(payload, list):
        return "".join(extract_text(item) for item in payload if isinstance(item, dict))

    parts: list[str] = []
    for candidate in payload.get("candidates") or []:
        content = candidate.get("content") or {}
        for part in content.get("parts") or []:
            text = part.get("text")
            if text:
                parts.append(text)

    return "".join(parts)


def _build_payload(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    format_json: bool,
) -> dict:
    generation_config = {
        "temperature": temperature,
        "maxOutputTokens": max_tokens,
        "thinkingConfig": {
            "thinkingBudget": settings.gemini_thinking_budget,
        },
    }

    if format_json:
        generation_config["responseMimeType"] = "application/json"

    return {
        "systemInstruction": {
            "parts": [{"text": system_prompt}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}],
            }
        ],
        "generationConfig": generation_config,
    }


def _post_json(url: str, payload: dict, *, timeout: int) -> str:
    request = _build_request(url, payload)
    try:
        with urlopen(request, timeout=timeout, context=_SSL_CONTEXT) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        error_body = _read_error_body(exc)
        if exc.code == 429:
            _activate_cooldown(_retry_after_seconds(error_body))
        raise RuntimeError(f"Gemini API trả về lỗi HTTP {exc.code}: {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Không gọi được Gemini API: {exc}") from exc


def _build_request(url: str, payload: dict) -> Request:
    if not settings.gemini_api_key:
        raise RuntimeError("Thiếu GEMINI_API_KEY để dùng Gemini provider.")

    return Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": settings.gemini_api_key,
        },
        method="POST",
    )


def _gemini_url(method: str, *, stream: bool = False) -> str:
    base_url = settings.gemini_base_url.rstrip("/")
    model = settings.gemini_model.strip()
    if model.startswith("models/"):
        model = model[len("models/"):]
    url = f"{base_url}/models/{model}:{method}"
    if stream:
        return f"{url}?{urlencode({'alt': 'sse'})}"
    return url


def _read_error_body(exc: HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8").strip()
    except Exception:
        body = ""
    return body[:500] or exc.reason


def _wait_for_rate_slot() -> None:
    global _LAST_REQUEST_AT

    now = time.monotonic()
    with _RATE_LOCK:
        if now < _COOLDOWN_UNTIL:
            remaining = max(1, int(_COOLDOWN_UNTIL - now))
            raise RuntimeError(f"Gemini đang tạm cooldown do quota/rate limit, thử lại sau khoảng {remaining}s.")

        min_interval = max(0.0, settings.gemini_min_interval_seconds)
        wait_seconds = (_LAST_REQUEST_AT + min_interval) - now
        if wait_seconds > 0:
            time.sleep(wait_seconds)

        _LAST_REQUEST_AT = time.monotonic()


def _activate_cooldown(retry_after: float | None = None) -> None:
    global _COOLDOWN_UNTIL

    cooldown = retry_after if retry_after and retry_after > 0 else settings.gemini_cooldown_seconds
    with _RATE_LOCK:
        _COOLDOWN_UNTIL = max(_COOLDOWN_UNTIL, time.monotonic() + cooldown)


def _retry_after_seconds(body: str) -> float | None:
    retry_match = re.search(r"retry in\s+([0-9]+(?:\.[0-9]+)?)s", body, flags=re.I)
    if retry_match:
        return float(retry_match.group(1)) + 1.0

    try:
        payload = json.loads(body)
    except JSONDecodeError:
        return None

    details = payload.get("error", {}).get("details", [])
    for detail in details:
        retry_delay = detail.get("retryDelay") if isinstance(detail, dict) else None
        if not retry_delay:
            continue
        delay_match = re.match(r"([0-9]+(?:\.[0-9]+)?)s", str(retry_delay))
        if delay_match:
            return float(delay_match.group(1)) + 1.0

    return None


def _looks_like_complete_json(content: str) -> bool:
    text = content.strip()
    if not text:
        return False

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

    try:
        json.loads(text)
        return True
    except JSONDecodeError:
        return False


def _cache_key(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    format_json: bool,
) -> str:
    raw = json.dumps(
        {
            "model": settings.gemini_model,
            "system": system_prompt,
            "user": user_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "format_json": format_json,
            "thinking_budget": settings.gemini_thinking_budget,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _get_cached(key: str) -> str | None:
    ttl = settings.gemini_cache_ttl_seconds
    if ttl <= 0:
        return None

    with _CACHE_LOCK:
        item = _CACHE.get(key)
        if item is None:
            return None

        expires_at, value = item
        if expires_at < time.monotonic():
            _CACHE.pop(key, None)
            return None

    return value


def _set_cached(key: str, value: str) -> None:
    ttl = settings.gemini_cache_ttl_seconds
    if ttl <= 0:
        return

    max_items = max(1, settings.gemini_cache_max_items)
    with _CACHE_LOCK:
        if len(_CACHE) >= max_items:
            oldest_key = min(_CACHE, key=lambda item_key: _CACHE[item_key][0])
            _CACHE.pop(oldest_key, None)

        _CACHE[key] = (time.monotonic() + ttl, value)
