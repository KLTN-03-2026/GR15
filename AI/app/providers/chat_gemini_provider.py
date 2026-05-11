from __future__ import annotations

from typing import Iterator

from app.core.config import settings
from app.providers.chat_openai_provider import _build_user_prompt, _compact_context
from app.providers.gemini_client import generate_text, stream_text
from app.services.chatbot_intent_engine import OUT_OF_SCOPE_MESSAGE


class GeminiChatProvider:
    def generate(self, question: str, context: dict, history: list[dict]) -> str:
        return generate_text(
            system_prompt=_system_prompt(),
            user_prompt=_build_user_prompt(question, context, history),
            max_tokens=settings.chatbot_max_tokens,
            temperature=0,
        )

    def stream(self, question: str, context: dict, history: list[dict]) -> Iterator[str]:
        yield from stream_text(
            system_prompt=_system_prompt(),
            user_prompt=_build_user_prompt(question, context, history),
            max_tokens=settings.chatbot_max_tokens,
            temperature=0,
        )


def _system_prompt() -> str:
    return (
        "Bạn là trợ lý tư vấn nghề nghiệp trong hệ thống tuyển dụng. "
        "Chỉ trả lời bằng tiếng Việt có dấu. "
        "Không bịa dữ liệu ngoài context. "
        "Không dùng markdown đậm/nghiêng. "
        "Không tự xưng 'tôi'; khi cần gọi vai trò, dùng 'hệ thống' hoặc 'trợ lý này'. "
        "Không dùng cụm tiếng Anh phổ thông trong nội dung tư vấn; chỉ giữ tên riêng công nghệ, tên vị trí gốc, viết tắt kỹ thuật hoặc framework. "
        "Việt hóa các cụm như Next 30 days thành 30 ngày, mini project, case study, portfolio, matching, job, apply, cover letter. "
        "Ưu tiên câu ngắn, đúng trọng tâm, không lan man. "
        "Nếu người dùng hỏi lộ trình, phải bám đúng mốc thời gian hoặc chủ đề người dùng nêu; chỉ dùng 30/60/90 ngày khi câu hỏi nêu rõ mốc đó hoặc 3 tháng. "
        "Nếu thiếu dữ liệu, hãy nói rõ là chưa đủ dữ liệu. "
        f"Nếu câu hỏi ngoài phạm vi, trả đúng câu sau: {OUT_OF_SCOPE_MESSAGE}"
    )


__all__ = ["GeminiChatProvider", "_compact_context"]
