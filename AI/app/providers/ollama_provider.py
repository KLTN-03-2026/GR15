from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.providers.base import CoverLetterContext


class OllamaCoverLetterProvider:
    def generate(self, context: CoverLetterContext) -> str:
        prompt = _build_vietnamese_prompt(context)
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
        }

        request = Request(
            settings.ollama_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=120) as response:
                body = response.read().decode("utf-8")
        except URLError as exc:
            raise RuntimeError(f"Không gọi được Ollama local: {exc}") from exc

        data = json.loads(body)
        content = (data.get("response") or "").strip()
        if not content:
            raise RuntimeError("Ollama không trả về nội dung thư xin việc.")

        return content


def _build_vietnamese_prompt(context: CoverLetterContext) -> str:
    return f"""
Bạn là trợ lý tuyển dụng chuyên viết thư xin việc bằng tiếng Việt.
Yêu cầu bắt buộc:
- Chỉ trả về đúng nội dung thư xin việc hoàn chỉnh bằng tiếng Việt.
- Không dùng markdown, không giải thích thêm ngoài thư xin việc.
- Văn phong lịch sự, chuyên nghiệp, tự nhiên.
- Xưng hô thống nhất là "Tôi".
- Sử dụng tiếng Việt có dấu đầy đủ.
- Có thể dùng xuống dòng hợp lý và danh sách gạch đầu dòng ngắn nếu giúp bố cục rõ hơn.
- Dựa sát dữ liệu ứng viên và vị trí.
- Nếu có kỹ năng còn thiếu, chỉ nhắc khéo theo hướng sẵn sàng học hỏi.

Thông tin ứng viên:
- Họ tên: {context.candidate_name}
- Kinh nghiệm: {context.experience_summary}
- Kỹ năng nổi bật: {", ".join(context.featured_skills) if context.featured_skills else "Không nêu rõ"}

Thông tin công việc:
- Vị trí: {context.job_title}
- Công ty: {context.company_name}
- Kỹ năng trọng tâm của JD: {", ".join(context.job_focus_skills) if context.job_focus_skills else "Không nêu rõ"}

Đối sánh:
- Điểm phù hợp: {context.matching_score if context.matching_score is not None else "Chưa có"}
- Giải thích ngắn: {context.matching_explanation or "Chưa có"}
- Kỹ năng cần bổ sung: {", ".join(context.missing_skills) if context.missing_skills else "Không đáng kể"}

Hãy viết thư xin việc hoàn chỉnh.
""".strip()
