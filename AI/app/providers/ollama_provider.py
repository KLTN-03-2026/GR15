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
            "options": {
                "temperature": 0,
                "top_p": 0.8,
                "num_predict": settings.cover_letter_max_tokens,
                "num_ctx": max(settings.ollama_num_ctx, 3072),
                "num_thread": settings.ollama_num_thread,
            },
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
- Thư phải được sinh bằng LLM dựa trên bằng chứng CV-JD, không dùng mẫu cố định.
- Văn phong lịch sự, chuyên nghiệp, tự nhiên, có lập luận chặt chẽ.
- Tính học thuật thể hiện qua cách lập luận: luận điểm rõ, bằng chứng từ CV/JD, giải thích mức phù hợp, xử lý khoảng trống kỹ năng hợp lý.
- Không dùng văn mẫu chung chung nếu không có bằng chứng.
- Không bịa dự án, công ty, chứng chỉ, số liệu hoặc kinh nghiệm ngoài dữ liệu.
- Xưng hô "Tôi" chỉ đại diện cho ứng viên trong thư, không đại diện cho AI/hệ thống.
- Sử dụng tiếng Việt có dấu đầy đủ.
- Không dùng cụm tiếng Anh phổ thông như matching, job, apply, cover letter, portfolio; hãy viết là đối sánh, công việc/vị trí, ứng tuyển, thư xin việc, hồ sơ dự án. Chỉ giữ tên riêng công nghệ hoặc tên vị trí gốc.
- Bố cục nên có: lời chào, đoạn mở nêu vị trí, đoạn lập luận phù hợp dựa trên bằng chứng, đoạn xử lý kỹ năng còn thiếu/định hướng đóng góp, lời kết.
- Độ dài khoảng 350-550 từ.
- Hạn chế gạch đầu dòng; chỉ dùng khi thực sự cần làm rõ bằng chứng.
- Dựa sát dữ liệu ứng viên và vị trí.
- Nếu có kỹ năng còn thiếu, chỉ nhắc khéo theo hướng sẵn sàng học hỏi.

Thông tin ứng viên:
- Họ tên: {context.candidate_name}
- Tiêu đề hồ sơ: {context.candidate_title or "Không nêu rõ"}
- Mục tiêu nghề nghiệp: {context.career_goal or "Không nêu rõ"}
- Trình độ: {context.education_level or "Không nêu rõ"}
- Số năm kinh nghiệm: {context.years_experience if context.years_experience is not None else "Không nêu rõ"}
- Kinh nghiệm: {context.experience_summary}
- Kỹ năng nổi bật: {", ".join(context.featured_skills) if context.featured_skills else "Không nêu rõ"}
- Bằng chứng từ CV/dự án/kinh nghiệm: {json.dumps(context.candidate_evidence, ensure_ascii=False)}

Thông tin công việc:
- Vị trí: {context.job_title}
- Công ty: {context.company_name}
- Cấp bậc: {context.job_level or "Không nêu rõ"}
- Kinh nghiệm yêu cầu: {context.required_experience or "Không nêu rõ"}
- Trình độ yêu cầu: {context.required_education or "Không nêu rõ"}
- Kỹ năng trọng tâm của JD: {", ".join(context.job_focus_skills) if context.job_focus_skills else "Không nêu rõ"}
- Bằng chứng/yêu cầu từ JD: {json.dumps(context.job_evidence, ensure_ascii=False)}

Đối sánh:
- Điểm phù hợp: {context.matching_score if context.matching_score is not None else "Chưa có"}
- Điểm thành phần: {json.dumps(context.score_breakdown, ensure_ascii=False)}
- Giải thích ngắn: {context.matching_explanation or "Chưa có"}
- Kỹ năng cần bổ sung: {", ".join(context.missing_skills) if context.missing_skills else "Không đáng kể"}

Hãy viết thư xin việc hoàn chỉnh.
""".strip()
