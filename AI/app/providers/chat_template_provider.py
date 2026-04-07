from __future__ import annotations

from typing import Iterator

from app.services.chatbot_intent_engine import build_template_answer, resolve_intent


class TemplateChatProvider:
    def generate(self, question: str, context: dict, history: list[dict]) -> str:
        intent = context.get("_chat_intent") or resolve_intent(question, history=history, context=context)
        return build_template_answer(question, context, history, intent)

    def stream(self, question: str, context: dict, history: list[dict]) -> Iterator[str]:
        answer = self.generate(question, context, history)
        for chunk in _chunk_text(answer):
            yield chunk


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
