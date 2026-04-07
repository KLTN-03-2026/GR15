from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Iterator
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class OllamaChatProvider:
    def generate(self, question: str, context: dict, history: list[dict]) -> str:
        prompt = _build_prompt(question, context, history)
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": settings.ollama_keep_alive,
            "options": {
                "temperature": 0.1,
                "num_predict": _resolve_num_predict(question),
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
            raise RuntimeError(f"Không gọi được Ollama local cho chatbot: {exc}") from exc

        try:
            data = json.loads(body)
        except JSONDecodeError as exc:
            snippet = body[:300].strip()
            raise RuntimeError(f"Ollama local trả về dữ liệu không hợp lệ: {snippet or 'rỗng'}") from exc

        if data.get("error"):
            raise RuntimeError(f"Ollama local báo lỗi: {data['error']}")

        content = _finalize_answer((data.get("response") or "").strip())
        if not content:
            raise RuntimeError("Ollama không trả về nội dung chatbot.")
        return content

    def stream(self, question: str, context: dict, history: list[dict]) -> Iterator[str]:
        prompt = _build_prompt(question, context, history)
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": True,
            "keep_alive": settings.ollama_keep_alive,
            "options": {
                "temperature": 0.1,
                "num_predict": _resolve_num_predict(question),
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
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                    except JSONDecodeError:
                        continue

                    if data.get("error"):
                        raise RuntimeError(f"Ollama local báo lỗi: {data['error']}")

                    chunk = _sanitize_chunk(data.get("response") or "")
                    if chunk:
                        yield chunk

                    if data.get("done") is True:
                        break
        except URLError as exc:
            raise RuntimeError(f"Không gọi được Ollama local cho chatbot: {exc}") from exc


def _build_prompt(question: str, context: dict, history: list[dict]) -> str:
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
- Chỉ trả lời trong phạm vi: hồ sơ CV, kết quả matching, nghề nghiệp phù hợp, kỹ năng cần bổ sung, công việc trong hệ thống, cover letter, chuẩn bị phỏng vấn.
- Câu hỏi hiện tại đã được hệ thống xác nhận là thuộc phạm vi tư vấn nghề nghiệp. Không được trả lời bằng thông báo ngoài phạm vi nếu câu hỏi đang nói về hồ sơ, CV, kỹ năng, nghề phù hợp, công việc, matching hoặc lộ trình phát triển.
- Nếu câu hỏi ngoài phạm vi, trả đúng câu sau:
"Tôi được thiết kế để hỗ trợ tư vấn nghề nghiệp, giải thích hồ sơ CV, kết quả matching và thông tin tuyển dụng trong hệ thống. Với câu hỏi này, tôi chưa phải là trợ lý phù hợp. Bạn có thể hỏi tôi về nghề nghiệp, kỹ năng cần bổ sung, CV, thư xin việc hoặc công việc phù hợp với hồ sơ của bạn."
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
- Nếu người dùng hỏi về lộ trình, kế hoạch 3 tháng hoặc 6 tháng, phải chia rõ theo từng giai đoạn:
Giai đoạn 1:
- ...
Giai đoạn 2:
- ...
Giai đoạn 3:
- ...
- Trả lời phải bám sát đúng câu hỏi hiện tại, không chuyển sang chủ đề khác.
- Ý định câu hỏi đã được hệ thống phân loại là: {resolved_intent}.
- Hãy bám sát đúng ý định đã phân loại. Không được đổi sang dạng trả lời chung chung.

Ngữ cảnh hệ thống:
{json.dumps(compact_context, ensure_ascii=False, separators=(',', ':'))}

Lịch sử hội thoại gần nhất:
{history_text or "Chưa có"}

Câu hỏi hiện tại:
{question}
""".strip()


def _compact_context(context: dict) -> dict:
    candidate = context.get("candidate_profile") or {}
    report = context.get("career_report") or {}
    matches = context.get("top_matching_jobs") or []
    related_job = context.get("related_job") or {}
    semantic_jobs = context.get("semantic_jobs") or []
    conversation_summary = context.get("conversation_summary")

    return {
        "conversation_summary": conversation_summary,
        "candidate_profile": {
            "ho_ten": candidate.get("ho_ten"),
            "tieu_de_ho_so": candidate.get("tieu_de_ho_so"),
            "kinh_nghiem_nam": candidate.get("kinh_nghiem_nam"),
            "trinh_do": candidate.get("trinh_do"),
            "parsed_skills": (candidate.get("parsed_skills") or [])[:8],
        },
        "career_report": {
            "nghe_de_xuat": report.get("nghe_de_xuat"),
            "muc_do_phu_hop": report.get("muc_do_phu_hop"),
            "goi_y_ky_nang_bo_sung": {
                "skills": ((report.get("goi_y_ky_nang_bo_sung") or {}).get("skills") or [])[:6],
                "strength_categories": ((report.get("goi_y_ky_nang_bo_sung") or {}).get("strength_categories") or [])[:4],
                "recommended_roles": ((report.get("goi_y_ky_nang_bo_sung") or {}).get("recommended_roles") or [])[:3],
            },
        } if report else None,
        "top_matching_jobs": [
            {
                "job_title": item.get("job_title"),
                "score": item.get("score"),
                "matched_skills": (item.get("matched_skills") or [])[:5],
                "missing_skills": (item.get("missing_skills") or [])[:5],
                "explanation": item.get("explanation"),
            }
            for item in matches[:2]
        ],
        "related_job": {
            "title": related_job.get("title"),
            "level": related_job.get("level"),
            "skills": (related_job.get("skills") or [])[:5],
        } if related_job else None,
        "semantic_jobs": semantic_jobs[:2],
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
        return max(settings.chatbot_max_tokens, 280)
    return settings.chatbot_max_tokens
