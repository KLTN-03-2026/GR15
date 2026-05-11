from __future__ import annotations

import json
import re

from app.core.config import settings
from app.core.logger import get_logger
from app.providers.gemini_client import generate_text
from app.providers.ollama_client import generate_text as generate_ollama_text
from app.services.llm_timeout import TimeoutError, run_with_timeout
from app.services.skill_catalog import normalize_search_text
from app.services.vietnamese_text import (
    normalize_vietnamese_ai_text,
    normalize_vietnamese_text_list,
)


logger = get_logger(__name__)

MODEL_VERSION = f"interview_copilot_v1.1::{settings.interview_copilot_provider}"


def generate_interview_copilot(ung_tuyen_id: int, application_context: dict | None = None) -> dict:
    context = application_context or {}
    job = context.get("job") or {}
    candidate = context.get("candidate") or {}

    job_skills = _as_list(job.get("skills"))
    candidate_skills = _as_list(candidate.get("skills"))
    matched_skills = _match_skills(job_skills, candidate_skills)
    missing_skills = [skill for skill in job_skills if skill not in matched_skills]

    evidence = {
        "ung_tuyen_id": ung_tuyen_id,
        "candidate_summary": normalize_vietnamese_ai_text(
            _candidate_summary(context, matched_skills, missing_skills),
            ensure_punctuation=True,
        ),
        "focus_areas": normalize_vietnamese_text_list(_focus_areas(job, candidate, matched_skills, missing_skills)),
        "questions": _normalize_question_groups(_question_groups(job, candidate, matched_skills, missing_skills)),
        "rubric": _normalize_rubric(_rubric(job, missing_skills)),
        "red_flags": normalize_vietnamese_text_list(_red_flags(candidate, missing_skills)),
    }
    provider = _resolve_provider_name()

    try:
        data = run_with_timeout(
            lambda: _generate_copilot_with_llm("generate", context, evidence, provider),
            settings.ai_llm_fallback_seconds,
        )
    except TimeoutError:
        provider = "rule_timeout_fallback"
        logger.warning(
            "Interview copilot generate LLM timed out ung_tuyen_id=%s timeout_seconds=%s",
            ung_tuyen_id,
            settings.ai_llm_fallback_seconds,
        )
        data = evidence.copy()
    except Exception as exc:
        logger.exception("Interview copilot generate failed provider=%s", provider)
        return {
            "success": False,
            "model_version": _model_version(provider),
            "data": {},
            "error": str(exc),
        }
    data["model_version"] = _model_version(provider)

    return {
        "success": True,
        "model_version": _model_version(provider),
        "data": data,
        "error": None,
    }


def evaluate_interview_copilot(
    ung_tuyen_id: int,
    application_context: dict | None = None,
    interview_notes: dict | None = None,
) -> dict:
    context = application_context or {}
    notes = interview_notes or {}
    scores = {
        key: float(value)
        for key, value in (notes.get("scores") or {}).items()
        if _is_number(value)
    }
    average = round(sum(scores.values()) / len(scores), 1) if scores else None
    note_text = str(notes.get("notes") or "").strip()
    decision = str(notes.get("decision") or "").strip()

    evidence = {
        "ung_tuyen_id": ung_tuyen_id,
        "summary": normalize_vietnamese_ai_text(_evaluation_summary(context, note_text, average), ensure_punctuation=True),
        "strengths": normalize_vietnamese_text_list(_evaluation_strengths(note_text, scores, average)),
        "concerns": normalize_vietnamese_text_list(_evaluation_concerns(note_text, scores, average)),
        "next_steps": normalize_vietnamese_text_list(_evaluation_next_steps(average, decision)),
        "recommendation": normalize_vietnamese_ai_text(
            decision or _recommendation_from_average(average),
            keep_blank_lines=False,
            trim_tail=False,
            ensure_punctuation=True,
        ),
    }
    provider = _resolve_provider_name()

    try:
        data = run_with_timeout(
            lambda: _generate_copilot_with_llm("evaluate", {**context, "interview_notes": notes}, evidence, provider),
            settings.ai_llm_fallback_seconds,
        )
    except TimeoutError:
        provider = "rule_timeout_fallback"
        logger.warning(
            "Interview copilot evaluate LLM timed out ung_tuyen_id=%s timeout_seconds=%s",
            ung_tuyen_id,
            settings.ai_llm_fallback_seconds,
        )
        data = evidence.copy()
    except Exception as exc:
        logger.exception("Interview copilot evaluate failed provider=%s", provider)
        return {
            "success": False,
            "model_version": _model_version(provider),
            "data": {},
            "error": str(exc),
        }
    data["model_version"] = _model_version(provider)

    return {
        "success": True,
        "model_version": _model_version(provider),
        "data": data,
        "error": None,
    }


def _resolve_provider_name() -> str:
    provider = (settings.interview_copilot_provider or "ollama").strip().lower()
    if provider == "gemini":
        return "gemini"
    if provider in {"", "llm", "ollama", "template", "rule", "rules", "rule_based", "local"}:
        if provider in {"template", "rule", "rules", "rule_based", "local"}:
            logger.warning("INTERVIEW_COPILOT_PROVIDER=%s is non-LLM; forcing ollama.", settings.interview_copilot_provider)
        return "ollama"
    logger.warning("Unknown INTERVIEW_COPILOT_PROVIDER=%s, forcing ollama.", settings.interview_copilot_provider)
    return "ollama"


def _model_version(provider: str) -> str:
    if provider == "rule_timeout_fallback":
        return "interview_copilot_v1.1::rule_timeout_fallback::internal"
    model = settings.gemini_model if provider == "gemini" else settings.ollama_model
    return f"interview_copilot_v1.1::{provider}::{model}"


def _generate_copilot_with_llm(mode: str, context: dict, evidence: dict, provider: str) -> dict:
    prompt = _build_llm_prompt(mode, context, evidence)
    if provider == "gemini":
        raw = generate_text(
            system_prompt=(
                "Bạn là trợ lý phỏng vấn cho nhà tuyển dụng. "
                "Chỉ trả về JSON hợp lệ, tiếng Việt, không markdown, không bịa dữ liệu ngoài JSON."
            ),
            user_prompt=prompt,
            max_tokens=settings.interview_copilot_max_tokens,
            temperature=0.2,
        )
    else:
        raw = generate_ollama_text(
            prompt,
            max_tokens=settings.interview_copilot_max_tokens,
            temperature=0.2,
            top_p=0.8,
            num_ctx=max(settings.ollama_num_ctx, 4096),
            error_context="Ollama local cho interview copilot",
        )
    return _normalize_llm_payload(raw, evidence, mode)


def _build_llm_prompt(mode: str, context: dict, evidence: dict) -> str:
    if mode == "evaluate":
        schema = '{"summary":"...","strengths":["..."],"concerns":["..."],"next_steps":["..."],"recommendation":"..."}'
        task = "Đánh giá ghi chú phỏng vấn và đề xuất bước tiếp theo cho nhà tuyển dụng."
    else:
        schema = '{"candidate_summary":"...","focus_areas":["..."],"questions":[{"group":"...","items":["..."]}],"rubric":[{"criterion":"...","weight":"...","signals":["..."]}],"red_flags":["..."]}'
        task = "Tạo interview copilot để nhà tuyển dụng phỏng vấn ứng viên theo CV/JD."

    return (
        "Bạn là trợ lý phỏng vấn cho hệ thống tuyển dụng.\n"
        f"Nhiệm vụ: {task}\n"
        "Quy tắc:\n"
        "- Chỉ trả về JSON hợp lệ theo schema, không markdown, không code block.\n"
        "- Viết tiếng Việt rõ ràng, ngắn gọn, bám sát dữ liệu.\n"
        "- Không bịa kỹ năng, kinh nghiệm, công ty hoặc kết quả ngoài JSON.\n"
        "- Nếu dữ liệu thiếu, nêu là cần xác minh thêm.\n"
        f"Schema: {schema}\n"
        f"Dữ liệu gốc: {json.dumps(context, ensure_ascii=False)}\n"
        f"Gợi ý cấu trúc nội bộ để tham khảo: {json.dumps(evidence, ensure_ascii=False)}"
    )


def _normalize_llm_payload(raw: str, evidence: dict, mode: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise RuntimeError("LLM trả về JSON không phải object.")

    if mode == "evaluate":
        return {
            "ung_tuyen_id": evidence["ung_tuyen_id"],
            "summary": normalize_vietnamese_ai_text(str(payload.get("summary") or evidence.get("summary") or ""), ensure_punctuation=True),
            "strengths": normalize_vietnamese_text_list(payload.get("strengths") or evidence.get("strengths") or []),
            "concerns": normalize_vietnamese_text_list(payload.get("concerns") or evidence.get("concerns") or []),
            "next_steps": normalize_vietnamese_text_list(payload.get("next_steps") or evidence.get("next_steps") or []),
            "recommendation": normalize_vietnamese_ai_text(str(payload.get("recommendation") or evidence.get("recommendation") or ""), ensure_punctuation=True),
        }

    return {
        "ung_tuyen_id": evidence["ung_tuyen_id"],
        "candidate_summary": normalize_vietnamese_ai_text(str(payload.get("candidate_summary") or evidence.get("candidate_summary") or ""), ensure_punctuation=True),
        "focus_areas": normalize_vietnamese_text_list(payload.get("focus_areas") or evidence.get("focus_areas") or []),
        "questions": _normalize_question_groups(payload.get("questions") or evidence.get("questions") or []),
        "rubric": _normalize_rubric(payload.get("rubric") or evidence.get("rubric") or []),
        "red_flags": normalize_vietnamese_text_list(payload.get("red_flags") or evidence.get("red_flags") or []),
    }


def _candidate_summary(context: dict, matched_skills: list[str], missing_skills: list[str]) -> str:
    candidate = context.get("candidate") or {}
    job = context.get("job") or {}
    name = candidate.get("name") or "Ứng viên"
    title = job.get("title") or "vị trí đang tuyển"
    profile_title = candidate.get("profile_title") or "hồ sơ chưa có tiêu đề rõ"
    years = candidate.get("years_experience")
    years_text = f"{years} năm kinh nghiệm" if years is not None else "kinh nghiệm chưa cập nhật"
    matched_text = ", ".join(matched_skills[:5]) if matched_skills else "chưa thấy kỹ năng khớp rõ"
    missing_text = ", ".join(missing_skills[:4]) if missing_skills else "chưa có khoảng trống kỹ năng lớn"

    return (
        f"{name} ứng tuyển vị trí {title}. Hồ sơ hiện tại là {profile_title}, "
        f"{years_text}. Kỹ năng khớp nổi bật: {matched_text}. "
        f"Điểm cần kiểm tra thêm: {missing_text}."
    )


def _focus_areas(job: dict, candidate: dict, matched_skills: list[str], missing_skills: list[str]) -> list[str]:
    areas = [
        "Xác nhận vai trò cá nhân, phạm vi trách nhiệm và kết quả đo lường trong các kinh nghiệm gần nhất.",
        "Đánh giá cách ứng viên phân tích vấn đề, ưu tiên công việc và xử lý trade-off.",
    ]
    if matched_skills:
        areas.insert(0, "Đào sâu mức độ thành thạo các kỹ năng đã khớp: " + ", ".join(matched_skills[:4]) + ".")
    if missing_skills:
        areas.append("Làm rõ các yêu cầu/kỹ năng chưa thể hiện rõ trong CV: " + ", ".join(missing_skills[:4]) + ".")
    if candidate.get("years_experience") is None:
        areas.append("Xác minh số năm kinh nghiệm và mức độ thực chiến vì CV chưa thể hiện rõ.")
    return areas


def _question_groups(job: dict, candidate: dict, matched_skills: list[str], missing_skills: list[str]) -> list[dict]:
    title = job.get("title") or "vị trí này"
    questions = [
        {
            "group": "Tóm tắt kinh nghiệm",
            "items": [
                f"Bạn hãy giới thiệu kinh nghiệm gần nhất liên quan trực tiếp tới {title}?",
                "Trong kinh nghiệm đó, phần nào do bạn trực tiếp chịu trách nhiệm và kết quả cụ thể là gì?",
            ],
        },
        {
            "group": "Kỹ năng theo JD",
            "items": [
                *(f"Bạn đã áp dụng {skill} trong tình huống thực tế nào?" for skill in matched_skills[:3]),
                *(f"CV chưa thể hiện rõ {skill}; bạn có kinh nghiệm nào liên quan không?" for skill in missing_skills[:3]),
            ] or ["Bạn đánh giá kỹ năng nào của mình phù hợp nhất với JD và vì sao?"],
        },
        {
            "group": "Hành vi và phối hợp",
            "items": [
                "Hãy kể một lần bạn gặp yêu cầu mơ hồ hoặc thay đổi liên tục. Bạn xử lý thế nào?",
                "Khi bất đồng với đồng đội hoặc quản lý về cách làm, bạn thường giải quyết ra sao?",
            ],
        },
        {
            "group": "Kỳ vọng và phù hợp",
            "items": [
                "Bạn kỳ vọng gì ở vai trò, team và môi trường làm việc trong 6 tháng đầu?",
                "Nếu được nhận, bạn cần những điều kiện nào để bắt đầu công việc hiệu quả?",
            ],
        },
    ]
    return questions


def _normalize_question_groups(groups: list[dict]) -> list[dict]:
    normalized_groups = []
    for group in groups:
        normalized_groups.append(
            {
                **group,
                "group": normalize_vietnamese_ai_text(
                    str(group.get("group") or ""),
                    keep_blank_lines=False,
                    trim_tail=False,
                    ensure_punctuation=False,
                ),
                "items": normalize_vietnamese_text_list(group.get("items") or []),
            }
        )
    return normalized_groups


def _rubric(job: dict, missing_skills: list[str]) -> list[dict]:
    return [
        {
            "criterion": "Phù hợp kỹ năng",
            "weight": 35,
            "expectation": "Ứng viên nêu được ví dụ thực tế cho kỹ năng chính trong JD, không chỉ liệt kê công cụ.",
        },
        {
            "criterion": "Kinh nghiệm liên quan",
            "weight": 25,
            "expectation": "Kinh nghiệm gắn với trách nhiệm của vị trí và có kết quả/đóng góp đo lường được.",
        },
        {
            "criterion": "Tư duy giải quyết vấn đề",
            "weight": 20,
            "expectation": "Có cách phân tích, ưu tiên, xử lý rủi ro và giải thích quyết định rõ ràng.",
        },
        {
            "criterion": "Giao tiếp và phù hợp văn hóa",
            "weight": 20,
            "expectation": "Trả lời mạch lạc, hợp tác tốt, kỳ vọng phù hợp với team và vai trò.",
        },
    ]


def _normalize_rubric(rubric: list[dict]) -> list[dict]:
    normalized = []
    for item in rubric:
        normalized.append(
            {
                **item,
                "criterion": normalize_vietnamese_ai_text(
                    str(item.get("criterion") or ""),
                    keep_blank_lines=False,
                    trim_tail=False,
                    ensure_punctuation=False,
                ),
                "expectation": normalize_vietnamese_ai_text(
                    str(item.get("expectation") or "; ".join(item.get("signals") or [])),
                    keep_blank_lines=False,
                    trim_tail=False,
                    ensure_punctuation=True,
                ),
            }
        )
    return normalized


def _red_flags(candidate: dict, missing_skills: list[str]) -> list[str]:
    flags = [
        "Ứng viên không mô tả được vai trò cá nhân hoặc kết quả cụ thể trong dự án.",
        "Câu trả lời chỉ dừng ở lý thuyết, thiếu ví dụ thực tế.",
    ]
    if missing_skills:
        flags.append("Chưa có minh chứng cho các kỹ năng/yêu cầu: " + ", ".join(missing_skills[:4]) + ".")
    if not candidate.get("projects") and not candidate.get("certificates"):
        flags.append("CV thiếu dự án/chứng chỉ để kiểm chứng năng lực.")
    return flags


def _evaluation_summary(context: dict, note_text: str, average: float | None) -> str:
    candidate = (context.get("candidate") or {}).get("name") or "Ứng viên"
    score_text = f" Điểm rubric trung bình {average}/10." if average is not None else ""
    note_summary = note_text[:240] if note_text else "Chưa có ghi chú chi tiết từ HR."
    return f"{candidate} đã được ghi nhận đánh giá sau phỏng vấn.{score_text} Tóm tắt ghi chú: {note_summary}"


def _evaluation_strengths(note_text: str, scores: dict[str, float], average: float | None) -> list[str]:
    strengths = []
    for key, value in scores.items():
        if value >= 7:
            strengths.append(f"{key}: điểm tốt ({value}/10).")
    if not strengths and note_text:
        strengths.append("Có ghi chú phỏng vấn để làm căn cứ đánh giá sâu hơn.")
    return strengths or ["Chưa xác định điểm mạnh rõ ràng từ dữ liệu nhập vào."]


def _evaluation_concerns(note_text: str, scores: dict[str, float], average: float | None) -> list[str]:
    concerns = []
    for key, value in scores.items():
        if value < 6:
            concerns.append(f"{key}: cần kiểm tra thêm ({value}/10).")
    if not note_text:
        concerns.append("HR chưa nhập ghi chú phỏng vấn chi tiết.")
    if average is not None and average < 6:
        concerns.append("Điểm trung bình thấp, cần cân nhắc trước khi cho qua vòng.")
    return concerns or ["Chưa phát hiện rủi ro lớn từ điểm rubric."]


def _evaluation_next_steps(average: float | None, decision: str) -> list[str]:
    if decision:
        return ["Đối chiếu khuyến nghị với rubric và cập nhật trạng thái ứng tuyển phù hợp."]
    if average is not None and average >= 7:
        return ["Cân nhắc chuyển ứng viên sang vòng tiếp theo hoặc chuẩn bị offer nếu đây là vòng cuối."]
    if average is not None and average < 6:
        return ["Cân nhắc từ chối hoặc yêu cầu thêm bài kiểm tra nếu còn thiếu dữ liệu."]
    return ["Bổ sung ghi chú/rubric chi tiết hơn trước khi ra quyết định."]


def _recommendation_from_average(average: float | None) -> str:
    if average is None:
        return "Chưa đủ dữ liệu để khuyến nghị chắc chắn."
    if average >= 8:
        return "Nên ưu tiên cho bước tiếp theo."
    if average >= 6.5:
        return "Có thể xem xét cho bước tiếp theo nếu không có rủi ro lớn."
    if average >= 5:
        return "Cần cân nhắc thêm hoặc phỏng vấn bổ sung."
    return "Không nên ưu tiên nếu không có dữ liệu bổ sung tích cực."


def _match_skills(required: list[str], candidate: list[str]) -> list[str]:
    candidate_normalized = {normalize_search_text(skill): skill for skill in candidate}
    matched = []
    for skill in required:
        normalized = normalize_search_text(skill)
        if not normalized:
            continue
        if any(normalized in key or key in normalized for key in candidate_normalized):
            matched.append(skill)
    return matched


def _as_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def _is_number(value) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
