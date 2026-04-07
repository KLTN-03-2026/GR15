from __future__ import annotations

import json
from json import JSONDecodeError
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class OllamaMockInterviewProvider:
    def refine_question(self, question_payload: dict, interview_context: dict, transcript: list[dict]) -> str:
        prompt = _build_question_prompt(question_payload, interview_context, transcript)
        return _call_ollama(prompt, min(settings.mock_interview_max_tokens, 96))

    def refine_report(self, report_payload: dict, interview_context: dict) -> str:
        prompt = _build_report_prompt(report_payload, interview_context)
        return _call_ollama(prompt, settings.mock_interview_max_tokens)


def _call_ollama(prompt: str, max_tokens: int) -> str:
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": settings.ollama_keep_alive,
        "options": {
            "temperature": 0.25,
            "num_predict": max_tokens,
            "num_ctx": settings.ollama_num_ctx,
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
        raise RuntimeError(f"Không gọi được Ollama local cho mock interview: {exc}") from exc

    try:
        data = json.loads(body)
    except JSONDecodeError as exc:
        snippet = body[:300].strip()
        raise RuntimeError(f"Ollama local trả về dữ liệu không hợp lệ cho mock interview: {snippet or 'rỗng'}") from exc

    if data.get("error"):
        raise RuntimeError(f"Ollama local báo lỗi ở mock interview: {data['error']}")

    content = _finalize_text((data.get("response") or "").strip())
    if not content:
        raise RuntimeError("Ollama không trả về nội dung cho mock interview.")
    return content


def _build_question_prompt(question_payload: dict, interview_context: dict, transcript: list[dict]) -> str:
    related_job = interview_context.get("related_job") or {}
    allowed_skills = [skill for skill in ((question_payload.get("focus_skills") or []) + (related_job.get("skills") or [])) if skill]
    recent_history = [
        item.get("content", "")
        for item in transcript[-3:]
        if item.get("content")
    ]
    return f"""
Bạn là người phỏng vấn kỹ thuật bằng tiếng Việt.
Nhiệm vụ:
- Viết lại câu hỏi phỏng vấn sao cho tự nhiên, ngắn gọn và chuyên nghiệp hơn.
- Giữ nguyên ý chính của câu hỏi gốc, không đổi chủ đề.
- Không dùng markdown, không dùng ký tự **, #, `.
- Chỉ trả về đúng một câu hỏi hoàn chỉnh, không thêm bất kỳ nội dung nào khác.
- Nếu là câu follow-up, phải bám sát câu trả lời trước đó và đào sâu hơn.
- Tuyệt đối không đưa ra gợi ý trả lời, ví dụ trả lời, đáp án mẫu, bullet giải thích, tiêu chí chấm điểm hoặc phần mở đầu như "Câu hỏi:", "Gợi ý:", "Trả lời:".
- Không tự chèn thêm công nghệ hoặc kỹ năng mới ngoài danh sách được phép nếu chúng không có trong câu hỏi gốc.

Thông tin ngữ cảnh:
- Vị trí mục tiêu: {related_job.get('title') or 'vị trí mục tiêu'}
- Loại câu hỏi: {question_payload.get('question_type') or 'general'}
- Giai đoạn: {question_payload.get('interview_stage_label') or 'Chung'}
- Kỹ năng trọng tâm: {", ".join(question_payload.get('focus_skills') or []) or 'không có'}
- Kỹ năng được phép nhắc tới: {", ".join(allowed_skills) or 'không có'}
- Câu hỏi gốc: {question_payload.get('question_text') or ''}
- Transcript gần nhất: {" | ".join(recent_history) if recent_history else "chưa có"}
""".strip()


def _build_report_prompt(report_payload: dict, interview_context: dict) -> str:
    related_job = interview_context.get("related_job") or {}
    metadata = report_payload.get("metadata") or {}
    return f"""
Bạn là trợ lý huấn luyện phỏng vấn nghề nghiệp.
Nhiệm vụ:
- Viết lại phần đề xuất cải thiện sau phiên mock interview thành tiếng Việt tự nhiên, ngắn gọn, dễ áp dụng.
- Bám sát dữ liệu cho sẵn, không bịa.
- Không dùng markdown đậm/nghiêng.
- Phải giữ đúng cấu trúc xuống dòng rõ ràng, mỗi ý là một dòng riêng.
- Nếu có danh sách, luôn dùng gạch đầu dòng đơn giản ở đầu dòng.
- Chỉ trả về phần coaching cuối, không nhắc lại toàn bộ điểm số.
- Cấu trúc mong muốn:
  Tóm tắt ngắn:
  - ...

  Ưu tiên cải thiện:
  - ...

  Kế hoạch luyện tiếp:
  - ...

Ngữ cảnh:
- Vị trí mục tiêu: {related_job.get('title') or 'vị trí mục tiêu'}
- Điểm mạnh: {", ".join(report_payload.get('diem_manh') or []) or 'không có'}
- Điểm yếu: {", ".join(report_payload.get('diem_yeu') or []) or 'không có'}
- Điểm yếu nhất: {metadata.get('weakest_dimension') or 'không xác định'}
- Trọng tâm cải thiện: {", ".join(metadata.get('recommended_focus') or []) or 'không có'}
- Kế hoạch luyện tiếp: {", ".join(metadata.get('practice_plan') or []) or 'không có'}
- Bản nháp hiện tại: {report_payload.get('de_xuat_cai_thien') or ''}
""".strip()


def _finalize_text(text: str) -> str:
    cleaned = (
        text.replace("**", "")
        .replace("__", "")
        .replace("`", "")
        .replace("#", "")
        .strip()
    )

    lines = []
    previous_blank = False
    for raw_line in cleaned.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            if lines and not previous_blank:
                lines.append("")
            previous_blank = True
            continue
        if line[:2] in {"- ", "1.", "2.", "3.", "4.", "5."}:
            line = line.rstrip()
        lines.append(line)
        previous_blank = False

    cleaned = "\n".join(lines).strip()
    if not cleaned:
        return cleaned
    if cleaned[-1] in ".!?":
        return cleaned
    return f"{cleaned}."
