from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.providers.base import CoverLetterContext


class OpenAICoverLetterProvider:
    def generate(self, context: CoverLetterContext) -> str:
        if not settings.openai_api_key:
            raise RuntimeError("Thiếu OPENAI_API_KEY để dùng OpenAI provider.")

        payload = {
            "model": settings.openai_model,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Bạn là trợ lý viết thư xin việc chuyên nghiệp. "
                                "Luôn trả lời hoàn toàn bằng tiếng Việt. "
                                "Chỉ trả về đúng nội dung thư xin việc hoàn chỉnh, không markdown, không giải thích thêm. "
                                "Xưng hô thống nhất là 'Tôi', dùng tiếng Việt có dấu đầy đủ, bố cục rõ ràng và có thể dùng gạch đầu dòng ngắn nếu phù hợp."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": _build_user_prompt(context),
                        }
                    ],
                },
            ],
        }

        request = Request(
            settings.openai_base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.openai_api_key}",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=120) as response:
                body = response.read().decode("utf-8")
        except URLError as exc:
            raise RuntimeError(f"Không gọi được OpenAI API: {exc}") from exc

        data = json.loads(body)
        content = _extract_response_text(data).strip()
        if not content:
            raise RuntimeError("OpenAI không trả về nội dung thư xin việc.")

        return content


def _build_user_prompt(context: CoverLetterContext) -> str:
    return f"""
Hãy viết một thư xin việc hoàn chỉnh bằng tiếng Việt, văn phong chuyên nghiệp và tự nhiên, dựa trên dữ liệu sau.

Ứng viên:
- Họ tên: {context.candidate_name}
- Kinh nghiệm: {context.experience_summary}
- Kỹ năng nổi bật: {", ".join(context.featured_skills) if context.featured_skills else "Không nêu rõ"}

Vị trí ứng tuyển:
- Chức danh: {context.job_title}
- Công ty: {context.company_name}
- Kỹ năng JD trọng tâm: {", ".join(context.job_focus_skills) if context.job_focus_skills else "Không nêu rõ"}

Kết quả matching:
- Điểm phù hợp: {context.matching_score if context.matching_score is not None else "Chưa có"}
- Giải thích: {context.matching_explanation or "Chưa có"}
- Kỹ năng còn thiếu: {", ".join(context.missing_skills) if context.missing_skills else "Không đáng kể"}

Yêu cầu:
- Chỉ trả về nội dung thư xin việc.
- Không markdown.
- Xưng hô thống nhất là "Tôi".
- Dùng tiếng Việt có dấu đầy đủ.
- Có thể dùng gạch đầu dòng ngắn nếu giúp thư rõ ràng hơn.
- Nếu có kỹ năng thiếu, đề cập khéo léo theo hướng sẵn sàng học hỏi.
""".strip()


def _extract_response_text(payload: dict) -> str:
    output = payload.get("output") or []
    parts: list[str] = []

    for item in output:
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                parts.append(content["text"])

    if parts:
        return "\n".join(parts)

    return payload.get("output_text") or ""
