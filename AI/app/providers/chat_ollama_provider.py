from __future__ import annotations

import json
from typing import Iterator

from app.core.config import settings
from app.providers.ollama_client import generate_text, stream_text
from app.services.chatbot_intent_engine import (
    ensure_chat_list,
    ensure_chat_mapping,
    normalize_chat_history_items,
    normalize_match_entries,
)


class OllamaChatProvider:
    def generate(self, question: str, context: dict, history: list[dict]) -> str:
        prompt = _build_prompt(question, context, history)
        return _finalize_answer(generate_text(
            prompt,
            max_tokens=_resolve_num_predict(question),
            temperature=0,
            top_p=0.8,
            error_context="Ollama local cho chatbot",
        ))

    def stream(self, question: str, context: dict, history: list[dict]) -> Iterator[str]:
        prompt = _build_prompt(question, context, history)
        for chunk in stream_text(
            prompt,
            max_tokens=_resolve_num_predict(question),
            temperature=0,
            top_p=0.8,
            error_context="Ollama local cho chatbot",
        ):
            sanitized = _sanitize_chunk(chunk)
            if sanitized:
                yield sanitized


def _build_prompt(question: str, context: dict, history: list[dict]) -> str:
    context = ensure_chat_mapping(context)
    history = normalize_chat_history_items(history)
    compact_context = _compact_context(context)
    resolved_intent = context.get("_chat_intent") or "general_career"
    history_text = "\n".join(
        f"{item.get('role', 'user')}[{item.get('intent', 'none')}]: {item.get('content', '')}"
        for item in history[-2:]
    )
    return f"""
Bạn là trợ lý tư vấn nghề nghiệp trong một hệ thống tuyển dụng.
Yêu cầu bắt buộc:
- Chỉ trả lời bằng tiếng Việt có dấu đầy đủ.
- Trả lời trực tiếp, không suy nghĩ thành nhiều bước.
- Không tự xưng "tôi"; khi cần gọi vai trò, dùng "hệ thống" hoặc "trợ lý này".
- Khi nói về người dùng, dùng "bạn"; khi nói về dữ liệu CV, dùng "hồ sơ" hoặc "ứng viên".
- Không dùng cụm tiếng Anh phổ thông trong nội dung tư vấn. Bắt buộc Việt hóa: "Next 30 days" thành "30 ngày", "Next 60 days" thành "60 ngày", "Next 90 days" thành "90 ngày", "mini project" thành "dự án nhỏ", "case study" thành "bài phân tích tình huống", "portfolio" thành "hồ sơ dự án", "matching" thành "đối sánh", "job" thành "công việc/vị trí", "apply" thành "ứng tuyển", "cover letter" thành "thư xin việc".
- Chỉ giữ tiếng Anh khi đó là tên riêng công nghệ, tên vị trí gốc, viết tắt kỹ thuật hoặc tên framework như iOS, Swift, SwiftUI, Firebase, REST API, Docker.
- Chỉ trả lời trong phạm vi: hồ sơ CV, kết quả đối sánh, nghề nghiệp phù hợp, kỹ năng cần bổ sung, công việc trong hệ thống, thư xin việc, chuẩn bị phỏng vấn.
- Câu hỏi hiện tại đã được hệ thống xác nhận là thuộc phạm vi tư vấn nghề nghiệp. Không được trả lời bằng thông báo ngoài phạm vi nếu câu hỏi đang nói về hồ sơ, CV, kỹ năng, nghề phù hợp, công việc, đối sánh hoặc lộ trình phát triển.
- Nếu câu hỏi ngoài phạm vi, trả đúng câu sau:
"Trợ lý này được thiết kế để hỗ trợ tư vấn nghề nghiệp, giải thích hồ sơ CV, kết quả đối sánh và thông tin tuyển dụng trong hệ thống. Với câu hỏi này, hệ thống chưa phải là kênh hỗ trợ phù hợp. Bạn có thể hỏi về nghề nghiệp, kỹ năng cần bổ sung, CV, thư xin việc hoặc công việc phù hợp với hồ sơ của bạn."
- Không bịa dữ liệu ngoài context.
- Nếu thiếu dữ liệu thì nói rõ là chưa đủ dữ liệu.
- Không dùng markdown.
- Không dùng ký tự nhấn mạnh như **, __, #, `.
- Không gộp tất cả thành một đoạn văn dài.
- Ưu tiên trả lời theo đúng cấu trúc sau nếu phù hợp:
Đánh giá nhanh:
- ...
Kỹ năng đang có lợi:
- ...
Kỹ năng cần bổ sung:
- ...
Gợi ý tiếp theo:
- ...
- Mỗi ý ngắn gọn, thực tế, tối đa 1-2 dòng.
- Nếu cần liệt kê, chỉ dùng dấu gạch đầu dòng đơn giản, không dùng markdown đậm/nghiêng.
- Nếu người dùng hỏi về định hướng nghề nghiệp kiểu "nên theo Backend Developer hay hướng khác", phải trả lời rõ:
Đề xuất chính:
- ...
Lý do:
- ...
Hướng thay thế:
- ...
- Nếu người dùng hỏi về lộ trình, phải bám đúng khoảng thời gian/chủ đề người dùng nêu. Chỉ dùng khung 30/60/90 ngày khi người dùng hỏi rõ 30/60/90 ngày hoặc 3 tháng.
- Trả lời phải bám sát đúng câu hỏi hiện tại, không chuyển sang chủ đề khác.
- Ý định câu hỏi đã được hệ thống phân loại là: {resolved_intent}.
- Hãy bám sát đúng ý định đã phân loại. Không được đổi sang dạng trả lời chung chung.
- Giữ cùng cấu trúc trả lời cho cùng một ý định để kết quả ổn định giữa các phiên.

Ngữ cảnh hệ thống:
{json.dumps(compact_context, ensure_ascii=False, separators=(',', ':'))}

Lịch sử hội thoại gần nhất:
{history_text or "Chưa có"}

Câu hỏi hiện tại:
{question}
""".strip()


def _compact_context(context: dict) -> dict:
    context = ensure_chat_mapping(context)
    candidate = ensure_chat_mapping(context.get("candidate_profile"))
    matches = normalize_match_entries(context.get("top_matching_jobs"))
    related_job = ensure_chat_mapping(context.get("related_job"))
    conversation_summary = context.get("conversation_summary")

    return {
        "conversation_summary": conversation_summary,
        "candidate_profile": {
            "ho_ten": candidate.get("ho_ten"),
            "tieu_de_ho_so": candidate.get("tieu_de_ho_so"),
            "vi_tri_ung_tuyen_muc_tieu": candidate.get("vi_tri_ung_tuyen_muc_tieu"),
            "ten_nganh_nghe_muc_tieu": candidate.get("ten_nganh_nghe_muc_tieu"),
            "kinh_nghiem_nam": candidate.get("kinh_nghiem_nam"),
            "trinh_do": candidate.get("trinh_do"),
            "parsed_skills": ensure_chat_list(candidate.get("parsed_skills"))[:8],
            "builder_skills": ensure_chat_list(candidate.get("builder_skills"))[:8],
        },
        "top_matching_jobs": [
            {
                "job_title": item.get("job_title"),
                "score": item.get("score"),
                "matched_skills": ensure_chat_list(item.get("matched_skills"))[:5],
                "missing_skills": ensure_chat_list(item.get("missing_skills"))[:5],
                "explanation": item.get("explanation"),
            }
            for item in matches[:2]
        ],
        "related_job": {
            "title": related_job.get("title"),
            "level": related_job.get("level"),
            "skills": ensure_chat_list(related_job.get("skills"))[:5],
        } if related_job else None,
    }


def _sanitize_chunk(text: str) -> str:
    return (
        text.replace("**", "")
        .replace("__", "")
        .replace("`", "")
        .replace("#", "")
    )


def _finalize_answer(text: str) -> str:
    cleaned = _sanitize_chunk(text).strip()

    normalized_lines: list[str] = []
    previous_blank = False
    for raw_line in cleaned.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            if normalized_lines and not previous_blank:
                normalized_lines.append("")
            previous_blank = True
            continue

        normalized_lines.append(line)
        previous_blank = False

    cleaned = "\n".join(normalized_lines).strip()
    cleaned = _trim_incomplete_tail(cleaned)

    if not cleaned:
        return cleaned

    if cleaned[-1] in ".!?":
        return cleaned

    last_stop = max(cleaned.rfind("."), cleaned.rfind("!"), cleaned.rfind("?"))
    if last_stop >= 0 and last_stop >= int(len(cleaned) * 0.55):
        return cleaned[: last_stop + 1].strip()

    return f"{cleaned}."


def _trim_incomplete_tail(text: str) -> str:
    if not text:
        return text

    lines = [line.rstrip() for line in text.splitlines()]
    while lines:
        last_line = lines[-1].strip()
        if not last_line:
            lines.pop()
            continue

        if (
            last_line.endswith((":", ",", ";", "-", "/", "("))
            or last_line.count("(") > last_line.count(")")
            or len(last_line) <= 4
        ):
            lines.pop()
            continue

        break

    return "\n".join(lines).strip()


def _resolve_num_predict(question: str) -> int:
    normalized = question.lower()
    detailed_markers = [
        "kế hoạch", "ke hoach", "lộ trình", "lo trinh", "3 tháng", "3 thang",
        "6 tháng", "6 thang", "phân tích", "phan tich", "chi tiết", "chi tiet",
        "nên theo", "huong khac", "hướng khác", "định hướng", "dinh huong",
    ]
    if any(marker in normalized for marker in detailed_markers):
        return min(max(settings.chatbot_max_tokens, 260), 360)
    return settings.chatbot_max_tokens
