from __future__ import annotations

from app.core.config import settings
from app.providers.gemini_client import generate_text
from app.providers.mock_interview_ollama_provider import (
    _build_question_prompt,
    _build_report_prompt,
    _finalize_text,
)


class GeminiMockInterviewProvider:
    def refine_question(self, question_payload: dict, interview_context: dict, transcript: list[dict]) -> str:
        content = generate_text(
            system_prompt="Bạn là người phỏng vấn kỹ thuật. Chỉ trả về đúng một câu hỏi tiếng Việt tự nhiên, không markdown.",
            user_prompt=_build_question_prompt(question_payload, interview_context, transcript),
            max_tokens=min(settings.mock_interview_max_tokens, 160),
            temperature=0.25,
        )
        return _finalize_text(content)

    def refine_report(self, report_payload: dict, interview_context: dict) -> str:
        content = generate_text(
            system_prompt="Bạn là trợ lý huấn luyện phỏng vấn. Chỉ trả về phần coaching tiếng Việt, bám sát dữ liệu.",
            user_prompt=_build_report_prompt(report_payload, interview_context),
            max_tokens=settings.mock_interview_max_tokens,
            temperature=0.25,
        )
        return _finalize_text(content)
