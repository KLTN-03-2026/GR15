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
                                "Thư phải được sinh bằng LLM dựa trên bằng chứng CV-JD, không dùng mẫu cố định. "
                                "Trong thư xin việc, ứng viên được phép tự xưng 'Tôi' vì đây là văn bản gửi nhà tuyển dụng dưới góc nhìn ứng viên. "
                                "Không dùng 'Tôi' để nói về AI/hệ thống. Dùng tiếng Việt có dấu đầy đủ, bố cục rõ ràng và có thể dùng gạch đầu dòng ngắn nếu phù hợp. "
                                "Không dùng cụm tiếng Anh phổ thông; chỉ giữ tên riêng công nghệ, tên vị trí gốc, viết tắt kỹ thuật hoặc framework."
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
            "temperature": 0,
            "max_output_tokens": settings.cover_letter_max_tokens,
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
Hãy viết một thư xin việc hoàn chỉnh bằng tiếng Việt, văn phong chuyên nghiệp, có lập luận chặt chẽ và bám sát dữ liệu sau.

Định hướng chất lượng:
- Viết như một thư ứng tuyển thật, không phải báo cáo phân tích.
- Tính học thuật thể hiện qua cách lập luận: luận điểm rõ, bằng chứng từ CV/JD, giải thích mức phù hợp, xử lý khoảng trống kỹ năng hợp lý.
- Không dùng văn mẫu chung chung như "tôi là người chăm chỉ" nếu không có bằng chứng.
- Không bịa dự án, công ty, chứng chỉ, số liệu hoặc kinh nghiệm ngoài dữ liệu.
- Nếu dữ liệu hạn chế, viết thận trọng và tập trung vào năng lực có căn cứ.

Ứng viên:
- Họ tên: {context.candidate_name}
- Tiêu đề hồ sơ: {context.candidate_title or "Không nêu rõ"}
- Mục tiêu nghề nghiệp: {context.career_goal or "Không nêu rõ"}
- Trình độ: {context.education_level or "Không nêu rõ"}
- Số năm kinh nghiệm: {context.years_experience if context.years_experience is not None else "Không nêu rõ"}
- Kinh nghiệm: {context.experience_summary}
- Kỹ năng nổi bật: {", ".join(context.featured_skills) if context.featured_skills else "Không nêu rõ"}
- Bằng chứng từ CV/dự án/kinh nghiệm: {json.dumps(context.candidate_evidence, ensure_ascii=False)}

Vị trí ứng tuyển:
- Chức danh: {context.job_title}
- Công ty: {context.company_name}
- Cấp bậc: {context.job_level or "Không nêu rõ"}
- Kinh nghiệm yêu cầu: {context.required_experience or "Không nêu rõ"}
- Trình độ yêu cầu: {context.required_education or "Không nêu rõ"}
- Kỹ năng JD trọng tâm: {", ".join(context.job_focus_skills) if context.job_focus_skills else "Không nêu rõ"}
- Bằng chứng/yêu cầu từ JD: {json.dumps(context.job_evidence, ensure_ascii=False)}

Kết quả đối sánh:
- Điểm phù hợp: {context.matching_score if context.matching_score is not None else "Chưa có"}
- Điểm thành phần: {json.dumps(context.score_breakdown, ensure_ascii=False)}
- Giải thích: {context.matching_explanation or "Chưa có"}
- Kỹ năng còn thiếu: {", ".join(context.missing_skills) if context.missing_skills else "Không đáng kể"}

Yêu cầu:
- Chỉ trả về nội dung thư xin việc.
- Không markdown.
- Xưng hô "Tôi" chỉ đại diện cho ứng viên trong thư, không đại diện cho AI/hệ thống.
- Dùng tiếng Việt có dấu đầy đủ.
- Bố cục nên có: lời chào, đoạn mở nêu vị trí, đoạn lập luận phù hợp dựa trên bằng chứng, đoạn xử lý kỹ năng còn thiếu/định hướng đóng góp, lời kết.
- Độ dài khoảng 350-550 từ.
- Hạn chế gạch đầu dòng; chỉ dùng khi thực sự cần làm rõ bằng chứng.
- Nếu có kỹ năng thiếu, đề cập khéo léo theo hướng sẵn sàng học hỏi.
- Không dùng cụm tiếng Anh phổ thông như matching, job, apply, cover letter, portfolio; hãy viết là đối sánh, công việc/vị trí, ứng tuyển, thư xin việc, hồ sơ dự án. Chỉ giữ tên riêng công nghệ hoặc tên vị trí gốc.
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
