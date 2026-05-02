from __future__ import annotations

import json
from typing import Iterator
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.services.chatbot_intent_engine import OUT_OF_SCOPE_MESSAGE


class OpenAIChatProvider:
    def generate(self, question: str, context: dict, history: list[dict]) -> str:
        if not settings.openai_api_key:
            raise RuntimeError("Thiếu OPENAI_API_KEY để dùng OpenAI provider cho chatbot.")

        payload = {
            "model": settings.openai_model,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Bạn là trợ lý tư vấn nghề nghiệp trong hệ thống tuyển dụng. "
                                "Chỉ trả lời bằng tiếng Việt có dấu. "
                                "Không bịa dữ liệu ngoài context. "
                                "Không dùng markdown đậm/nghiêng. "
                                "Nếu thiếu dữ liệu, hãy nói rõ là chưa đủ dữ liệu. "
                                f"Nếu câu hỏi ngoài phạm vi, trả đúng câu sau: {OUT_OF_SCOPE_MESSAGE}"
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": _build_user_prompt(question, context, history),
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
            raise RuntimeError(f"Không gọi được OpenAI API cho chatbot: {exc}") from exc

        data = json.loads(body)
        content = _extract_response_text(data).strip()
        if not content:
            raise RuntimeError("OpenAI không trả về nội dung chatbot.")
        return content

    def stream(self, question: str, context: dict, history: list[dict]) -> Iterator[str]:
        if not settings.openai_api_key:
            raise RuntimeError("Thiếu OPENAI_API_KEY để dùng OpenAI provider cho chatbot.")

        payload = {
            "model": settings.openai_model,
            "stream": True,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Bạn là trợ lý tư vấn nghề nghiệp trong hệ thống tuyển dụng. "
                                "Chỉ trả lời bằng tiếng Việt có dấu. "
                                "Không bịa dữ liệu ngoài context. "
                                "Không dùng markdown đậm/nghiêng. "
                                "Nếu thiếu dữ liệu, hãy nói rõ là chưa đủ dữ liệu. "
                                f"Nếu câu hỏi ngoài phạm vi, trả đúng câu sau: {OUT_OF_SCOPE_MESSAGE}"
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": _build_user_prompt(question, context, history),
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
                "Accept": "text/event-stream",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=120) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if not line or line.startswith("event:"):
                        continue
                    if not line.startswith("data:"):
                        continue

                    payload_line = line[len("data:"):].strip()
                    if payload_line == "[DONE]":
                        break

                    try:
                        event_data = json.loads(payload_line)
                    except json.JSONDecodeError:
                        continue

                    chunk = _extract_stream_chunk(event_data)
                    if chunk:
                        yield chunk
        except URLError as exc:
            raise RuntimeError(f"Không gọi được OpenAI API cho chatbot: {exc}") from exc


def _build_user_prompt(question: str, context: dict, history: list[dict]) -> str:
    compact_context = _compact_context(context)
    resolved_intent = context.get("_chat_intent") or "general_career"
    return (
        "Ngữ cảnh hệ thống:\n"
        + json.dumps(compact_context, ensure_ascii=False, separators=(",", ":"))
        + "\n\nLịch sử hội thoại gần nhất:\n"
        + json.dumps(history[-4:], ensure_ascii=False, separators=(",", ":"))
        + "\n\nCâu hỏi hiện tại:\n"
        + question
        + f"\n\nÝ định câu hỏi đã được hệ thống phân loại là: {resolved_intent}."
        + "\nHãy bám sát đúng ý định này và trả lời theo dạng ngắn gọn, có xuống dòng rõ ràng nếu cần."
        + "\nNếu ý định là career_path_simulator, hãy sinh lộ trình 30/60/90 ngày dựa trên hồ sơ, skill gap, job gần nhất và mốc kiểm tra rõ ràng."
    )


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


def _extract_stream_chunk(payload: dict) -> str:
    event_type = payload.get("type")
    if event_type == "response.output_text.delta":
        return payload.get("delta") or ""

    if event_type == "response.output_item.added":
        item = payload.get("item") or {}
        if item.get("type") == "output_text" and item.get("text"):
            return item["text"]

    delta = payload.get("delta")
    if isinstance(delta, str):
        return delta

    return ""


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
            "vi_tri_ung_tuyen_muc_tieu": candidate.get("vi_tri_ung_tuyen_muc_tieu"),
            "ten_nganh_nghe_muc_tieu": candidate.get("ten_nganh_nghe_muc_tieu"),
            "kinh_nghiem_nam": candidate.get("kinh_nghiem_nam"),
            "trinh_do": candidate.get("trinh_do"),
            "parsed_skills": (candidate.get("parsed_skills") or [])[:8],
            "builder_skills": (candidate.get("builder_skills") or [])[:8],
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
