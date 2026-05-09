from __future__ import annotations

from app.core.config import settings
from app.providers.base import CoverLetterContext
from app.providers.gemini_client import generate_text
from app.providers.openai_provider import _build_user_prompt


class GeminiCoverLetterProvider:
    def generate(self, context: CoverLetterContext) -> str:
        return generate_text(
            system_prompt=(
                "Bạn là trợ lý viết thư xin việc chuyên nghiệp. "
                "Luôn trả lời hoàn toàn bằng tiếng Việt. "
                "Chỉ trả về đúng nội dung thư xin việc hoàn chỉnh, không markdown, không giải thích thêm. "
                "Thư phải dựa trên bằng chứng CV-JD, không dùng mẫu cố định và không bịa dữ liệu."
            ),
            user_prompt=_build_user_prompt(context),
            max_tokens=settings.cover_letter_max_tokens,
            temperature=0,
        )
