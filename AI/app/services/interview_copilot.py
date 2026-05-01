from __future__ import annotations

from app.core.config import settings
from app.services.skill_catalog import normalize_search_text


MODEL_VERSION = f"interview_copilot_v1.0::rule_based::{settings.local_llm_model}"


def generate_interview_copilot(ung_tuyen_id: int, application_context: dict | None = None) -> dict:
    context = application_context or {}
    job = context.get("job") or {}
    candidate = context.get("candidate") or {}

    job_skills = _as_list(job.get("skills"))
    candidate_skills = _as_list(candidate.get("skills"))
    matched_skills = _match_skills(job_skills, candidate_skills)
    missing_skills = [skill for skill in job_skills if skill not in matched_skills]

    data = {
        "ung_tuyen_id": ung_tuyen_id,
        "candidate_summary": _candidate_summary(context, matched_skills, missing_skills),
        "focus_areas": _focus_areas(job, candidate, matched_skills, missing_skills),
        "questions": _question_groups(job, candidate, matched_skills, missing_skills),
        "rubric": _rubric(job, missing_skills),
        "red_flags": _red_flags(candidate, missing_skills),
        "model_version": MODEL_VERSION,
    }

    return {
        "success": True,
        "model_version": MODEL_VERSION,
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

    data = {
        "ung_tuyen_id": ung_tuyen_id,
        "summary": _evaluation_summary(context, note_text, average),
        "strengths": _evaluation_strengths(note_text, scores, average),
        "concerns": _evaluation_concerns(note_text, scores, average),
        "next_steps": _evaluation_next_steps(average, decision),
        "recommendation": decision or _recommendation_from_average(average),
        "model_version": MODEL_VERSION,
    }

    return {
        "success": True,
        "model_version": MODEL_VERSION,
        "data": data,
        "error": None,
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
