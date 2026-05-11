from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Iterator
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.config import settings


def generate_text(
    prompt: str,
    *,
    max_tokens: int,
    temperature: float = 0,
    top_p: float = 0.8,
    num_ctx: int | None = None,
    format_json: bool = False,
    error_context: str = "Ollama",
) -> str:
    payload = _build_payload(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        num_ctx=num_ctx,
        format_json=format_json,
        stream=False,
    )
    body = _post(payload, error_context=error_context)
    data = _decode_json(body, error_context=error_context)

    if data.get("error"):
        raise RuntimeError(f"{error_context} báo lỗi: {data['error']}")

    content = (data.get("response") or "").strip()
    if not content:
        raise RuntimeError(f"{error_context} không trả về nội dung.")
    return content


def stream_text(
    prompt: str,
    *,
    max_tokens: int,
    temperature: float = 0,
    top_p: float = 0.8,
    num_ctx: int | None = None,
    format_json: bool = False,
    error_context: str = "Ollama",
) -> Iterator[str]:
    payload = _build_payload(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        num_ctx=num_ctx,
        format_json=format_json,
        stream=True,
    )
    request = _build_request(payload)

    try:
        with urlopen(request, timeout=settings.ollama_timeout_seconds) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except JSONDecodeError:
                    continue

                if data.get("error"):
                    raise RuntimeError(f"{error_context} báo lỗi: {data['error']}")

                chunk = data.get("response") or ""
                if chunk:
                    yield chunk

                if data.get("done") is True:
                    break
    except URLError as exc:
        raise RuntimeError(f"Không gọi được {error_context}: {exc}") from exc


def _build_payload(
    prompt: str,
    *,
    max_tokens: int,
    temperature: float,
    top_p: float,
    num_ctx: int | None,
    format_json: bool,
    stream: bool,
) -> dict:
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": stream,
        "keep_alive": settings.ollama_keep_alive,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": max_tokens,
            "num_ctx": num_ctx or settings.ollama_num_ctx,
            "num_thread": settings.ollama_num_thread,
            "num_batch": settings.ollama_num_batch,
        },
    }

    if format_json:
        payload["format"] = "json"

    return payload


def _build_request(payload: dict) -> Request:
    return Request(
        settings.ollama_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def _post(payload: dict, *, error_context: str) -> str:
    request = _build_request(payload)
    try:
        with urlopen(request, timeout=settings.ollama_timeout_seconds) as response:
            return response.read().decode("utf-8")
    except URLError as exc:
        raise RuntimeError(f"Không gọi được {error_context}: {exc}") from exc


def _decode_json(body: str, *, error_context: str) -> dict:
    try:
        return json.loads(body)
    except JSONDecodeError as exc:
        snippet = body[:300].strip()
        raise RuntimeError(f"{error_context} trả về dữ liệu không hợp lệ: {snippet or 'rỗng'}") from exc
