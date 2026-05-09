from __future__ import annotations

import json
from json import JSONDecodeError
import ssl
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


def generate_text(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float = 0,
    timeout: int = 120,
) -> str:
    payload = _build_payload(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    body = _post_json(_gemini_url("generateContent"), payload, timeout=timeout)
    data = json.loads(body)
    content = extract_text(data).strip()
    if not content:
        raise RuntimeError("Gemini không trả về nội dung.")
    return content


def stream_text(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float = 0,
    timeout: int = 120,
) -> Iterator[str]:
    payload = _build_payload(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    request = _build_request(_gemini_url("streamGenerateContent", stream=True), payload)

    try:
        with urlopen(request, timeout=timeout, context=_SSL_CONTEXT) as response:
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
        raise RuntimeError(f"Gemini API trả về lỗi HTTP {exc.code}: {_read_error_body(exc)}") from exc
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


def _build_payload(*, system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> dict:
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
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "thinkingConfig": {
                "thinkingBudget": settings.gemini_thinking_budget,
            },
        },
    }


def _post_json(url: str, payload: dict, *, timeout: int) -> str:
    request = _build_request(url, payload)
    try:
        with urlopen(request, timeout=timeout, context=_SSL_CONTEXT) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(f"Gemini API trả về lỗi HTTP {exc.code}: {_read_error_body(exc)}") from exc
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
