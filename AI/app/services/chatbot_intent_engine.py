from __future__ import annotations

import json
import re
from typing import Iterable

from app.services.skill_catalog import normalize_search_text


OUT_OF_SCOPE_MESSAGE = (
    "Trợ lý này được thiết kế để hỗ trợ tư vấn nghề nghiệp, giải thích hồ sơ CV, kết quả đối sánh và thông tin tuyển dụng trong hệ thống. "
    "Với câu hỏi này, hệ thống chưa phải là kênh hỗ trợ phù hợp. Bạn có thể hỏi về nghề nghiệp, kỹ năng cần bổ sung, CV, thư xin việc hoặc công việc phù hợp với hồ sơ của bạn."
)

INTENT_OUT_OF_SCOPE = "out_of_scope"
INTENT_SKILL_GAP = "skill_gap"
INTENT_MATCHING_EXPLANATION = "matching_explanation"
INTENT_JOB_RECOMMENDATION = "job_recommendation"
INTENT_NEXT_STEP_ACTION = "next_step_action"
INTENT_CAREER_DIRECTION = "career_direction"
INTENT_LEARNING_PLAN = "career_path_simulator"
INTENT_CV_IMPROVEMENT = "cv_improvement"
INTENT_COVER_LETTER = "cover_letter"
INTENT_INTERVIEW_PREP = "interview_prep"
INTENT_GENERAL_CAREER = "general_career"

DOMAIN_KEYWORDS = {
    "cv", "ho so", "hồ sơ", "matching", "nghe nghiep", "nghề nghiệp", "ky nang", "kỹ năng",
    "ung tuyen", "ứng tuyển", "job", "cong viec", "công việc", "cover letter", "thu xin viec",
    "thư xin việc", "phong van", "phỏng vấn", "career", "skill", "jd", "resume",
    "backend", "frontend", "mobile", "ios", "android", "marketing", "ke toan", "kế toán",
    "huong chinh", "hướng chính", "huong thay the", "hướng thay thế", "giai doan", "giai đoạn",
    "ke hoach", "kế hoạch", "lo trinh", "lộ trình", "dinh huong", "định hướng",
}

DETERMINISTIC_INTENTS = {
    INTENT_SKILL_GAP,
    INTENT_MATCHING_EXPLANATION,
    INTENT_JOB_RECOMMENDATION,
    INTENT_NEXT_STEP_ACTION,
    INTENT_CAREER_DIRECTION,
    INTENT_LEARNING_PLAN,
    INTENT_CV_IMPROVEMENT,
    INTENT_COVER_LETTER,
    INTENT_INTERVIEW_PREP,
    INTENT_GENERAL_CAREER,
}

MODEL_PREFERRED_INTENTS = {
    INTENT_GENERAL_CAREER,
}

INTENT_LABELS = {
    INTENT_SKILL_GAP: "Kỹ năng cần bổ sung",
    INTENT_MATCHING_EXPLANATION: "Giải thích đối sánh",
    INTENT_JOB_RECOMMENDATION: "Gợi ý công việc",
    INTENT_NEXT_STEP_ACTION: "Nên làm gì trước",
    INTENT_CAREER_DIRECTION: "Định hướng nghề",
    INTENT_LEARNING_PLAN: "Mô phỏng lộ trình nghề nghiệp",
    INTENT_CV_IMPROVEMENT: "Cải thiện CV",
    INTENT_COVER_LETTER: "Thư xin việc",
    INTENT_INTERVIEW_PREP: "Chuẩn bị phỏng vấn",
    INTENT_GENERAL_CAREER: "Tư vấn nghề nghiệp",
    INTENT_OUT_OF_SCOPE: "Ngoài phạm vi",
}


def ensure_chat_mapping(value) -> dict:
    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return {}

        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError:
            return {}

        return decoded if isinstance(decoded, dict) else {}

    return {}


def ensure_chat_list(value) -> list:
    if isinstance(value, list):
        return value

    if isinstance(value, (tuple, set)):
        return list(value)

    if isinstance(value, dict):
        return [value]

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []

        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError:
            decoded = None

        if isinstance(decoded, list):
            return decoded
        if isinstance(decoded, dict):
            return [decoded]
        if isinstance(decoded, str):
            stripped = decoded.strip()
            if not stripped:
                return []

        parts = [
            re.sub(r"^[\-\*\u2022]+\s*", "", part).strip()
            for part in re.split(r"[\r\n,;]+", stripped)
        ]
        parts = [part for part in parts if part]
        return parts if parts else [stripped]

    return []


def normalize_chat_history_items(history: list[dict] | None) -> list[dict]:
    normalized: list[dict] = []

    for item in history or []:
        if isinstance(item, dict):
            normalized.append(item)
            continue

        if isinstance(item, str) and item.strip():
            normalized.append({
                "role": "user",
                "content": item.strip(),
                "intent": None,
            })

    return normalized


def normalize_match_entries(matches) -> list[dict]:
    normalized: list[dict] = []

    for item in ensure_chat_list(matches):
        if isinstance(item, dict):
            normalized.append(item)
            continue

        if isinstance(item, str) and item.strip():
            normalized.append({
                "job_title": item.strip(),
                "matched_skills": [],
                "missing_skills": [],
                "explanation": None,
            })

    return normalized


def extract_report_skill_hints(report) -> dict:
    report_map = ensure_chat_mapping(report)
    raw_payload = report_map.get("goi_y_ky_nang_bo_sung")
    payload_map = ensure_chat_mapping(raw_payload)

    if payload_map:
        return {
            "skills": _normalize_string_list(payload_map.get("skills")),
            "strength_categories": _normalize_string_list(payload_map.get("strength_categories")),
            "recommended_roles": _normalize_string_list(payload_map.get("recommended_roles")),
            "raw_text": str(payload_map.get("raw_text") or "").strip() or None,
        }

    normalized_list = _normalize_string_list(raw_payload)
    raw_text = raw_payload.strip() if isinstance(raw_payload, str) and raw_payload.strip() else None

    return {
        "skills": normalized_list,
        "strength_categories": [],
        "recommended_roles": [],
        "raw_text": raw_text,
    }


def resolve_intent(message: str, *, history: list[dict] | None = None, context: dict | None = None) -> str:
    normalized = normalize_search_text(message)
    history = normalize_chat_history_items(history)
    context = ensure_chat_mapping(context)

    if _looks_like_learning_plan_request(normalized):
        return INTENT_LEARNING_PLAN

    scores = _score_intents(normalized)
    last_intent = _last_in_scope_intent(history)

    if scores:
        if _is_follow_up_question(normalized) and last_intent in {INTENT_CAREER_DIRECTION, INTENT_LEARNING_PLAN}:
            if any(marker in normalized for marker in ["giai doan", "giai đoạn", "ke hoach", "kế hoạch", "lo trinh", "lộ trình"]):
                return INTENT_LEARNING_PLAN
            if any(marker in normalized for marker in ["huong chinh", "hướng chính", "huong thay the", "hướng thay thế", "nen theo", "nên theo"]):
                return INTENT_CAREER_DIRECTION

        return _pick_intent(scores)

    if _is_follow_up_question(normalized) and last_intent is not None:
        return last_intent

    if _is_out_of_scope(message, history=history, context=context):
        return INTENT_OUT_OF_SCOPE

    if _has_chat_context(context) or _history_is_in_scope(history):
        return INTENT_GENERAL_CAREER

    return INTENT_OUT_OF_SCOPE


def should_use_fast_path(message: str, *, intent: str | None = None) -> bool:
    normalized = normalize_search_text(message)
    words = normalized.split()
    if len(normalized) > 90 or len(words) > 14:
        return False

    if intent in {INTENT_LEARNING_PLAN, INTENT_CAREER_DIRECTION, INTENT_GENERAL_CAREER}:
        return False

    return intent in {
        INTENT_SKILL_GAP,
        INTENT_MATCHING_EXPLANATION,
        INTENT_JOB_RECOMMENDATION,
        INTENT_NEXT_STEP_ACTION,
        INTENT_CV_IMPROVEMENT,
        INTENT_COVER_LETTER,
        INTENT_INTERVIEW_PREP,
    }


def build_template_answer(question: str, context: dict, history: list[dict], intent: str) -> str:
    context = ensure_chat_mapping(context)
    candidate = ensure_chat_mapping(context.get("candidate_profile"))
    report = ensure_chat_mapping(context.get("career_report"))
    matches = normalize_match_entries(context.get("top_matching_jobs"))
    related_job = ensure_chat_mapping(context.get("related_job"))
    rag_context = ensure_chat_mapping(context.get("rag_context"))
    normalized = normalize_search_text(question)

    if intent == INTENT_SKILL_GAP:
        missing = _collect_missing_skills(matches, report)
        if not missing:
            return (
                "Hiện tại chưa thấy kỹ năng còn thiếu nổi bật từ hồ sơ và các job đã đối sánh.\n"
                "- Bạn có thể phân tích thêm JD hoặc tạo kết quả đối sánh mới để hệ thống phân tích sát hơn."
            )

        lines = [
            "Kỹ năng cần bổ sung:",
            *[f"- {skill}" for skill in missing[:5]],
            "",
            "Gợi ý tiếp theo:",
            "- Ưu tiên học các kỹ năng xuất hiện lặp lại trong nhiều job phù hợp trước.",
            "- Sau khi bổ sung 1-2 kỹ năng chính, hãy cập nhật lại CV để phản ánh rõ phần đã học.",
        ]
        return "\n".join(lines)

    if intent == INTENT_MATCHING_EXPLANATION:
        top = matches[0] if matches else {}
        if not top:
            return "Hiện chưa có dữ liệu đối sánh để giải thích điểm phù hợp. Bạn có thể chạy chức năng đối sánh trước."

        matched = top.get("matched_skills", []) or []
        missing = top.get("missing_skills", []) or []
        lines = [
            "Đánh giá nhanh:",
            f"- Vị trí đang gần nhất là {top.get('job_title', 'vị trí phù hợp nhất hiện tại')}.",
        ]
        if matched:
            lines.extend(["", "Kỹ năng đang có lợi:", *[f"- {skill}" for skill in matched[:5]]])
        if missing:
            lines.extend(["", "Kỹ năng cần bổ sung:", *[f"- {skill}" for skill in missing[:5]]])
        explanation = top.get("explanation")
        if explanation:
            lines.extend(["", f"Kết luận ngắn: {explanation}"])
        else:
            lines.extend(["", "Kết luận ngắn: Hồ sơ đang có nền tảng phù hợp nhưng vẫn còn thiếu một số kỹ năng quan trọng để tăng độ phù hợp."])
        return "\n".join(lines)

    if intent == INTENT_JOB_RECOMMENDATION:
        jobs = _job_candidates(matches)
        rag_jobs = _rag_job_candidates(rag_context)
        wants_apply = any(keyword in normalized for keyword in ["apply", "ứng tuyển", "ung tuyen", "apply ngay"])
        if not jobs and rag_jobs:
            jobs = rag_jobs

        if not jobs:
            return (
                "Hiện chưa có đủ dữ liệu để gợi ý job cụ thể.\n"
                "- Bạn nên tạo kết quả đối sánh mới hoặc chọn thêm JD liên quan để hệ thống đề xuất sát hơn."
            )

        lines = [
            "Gợi ý công việc nên xem:",
            *[f"- {job}" for job in jobs[:3]],
        ]
        if rag_jobs:
            lines.extend([
                "",
                "Nguồn tham chiếu:",
                "- Gợi ý được lọc từ dữ liệu hồ sơ, kỹ năng và tin tuyển dụng hiện có trong hệ thống.",
            ])
        if wants_apply:
            lines.extend([
                "",
                "Ưu tiên trước:",
                f"- Bạn có thể ưu tiên ứng tuyển vị trí {jobs[0]} vì đây là vị trí gần nhất với hồ sơ hiện tại.",
            ])
        else:
            lines.extend([
                "",
                "Kết luận ngắn:",
                f"- Vị trí gần nhất hiện tại là {jobs[0]}.",
            ])
        return "\n".join(lines)

    if intent == INTENT_NEXT_STEP_ACTION:
        missing = _collect_missing_skills(matches, report)
        parsed_skills = candidate.get("parsed_skills") or []
        target_title = related_job.get("title") or (matches[0].get("job_title") if matches else None) or "vị trí mục tiêu hiện tại"
        lines = [
            "Việc nên làm trước trong tuần này:",
            f"- Chỉnh lại CV để nhấn mạnh rõ các kỹ năng đang khớp với {target_title}.",
        ]
        if parsed_skills:
            lines.append("- Giữ nổi bật các kỹ năng đã có như " + ", ".join(parsed_skills[:3]) + ".")
        if missing:
            lines.append("- Chọn 1-2 kỹ năng còn thiếu để bổ sung ngay, ưu tiên: " + ", ".join(missing[:2]) + ".")
        lines.extend([
            "- Chuẩn bị một ví dụ dự án hoặc kinh nghiệm thực tế để chứng minh năng lực khi ứng tuyển.",
            "",
            "Bước tiếp theo:",
            "- Sau khi cập nhật CV và bù khoảng trống chính, hãy xem lại các vị trí gần nhất trong hệ thống để chọn vị trí phù hợp nhất.",
        ])
        return "\n".join(lines)

    if intent == INTENT_CAREER_DIRECTION:
        role = report.get("nghe_de_xuat") or related_job.get("title") or "Backend Developer"
        alternatives = _alternative_roles(report, role)
        lines = [
            "Đề xuất chính:",
            f"- Bạn nên ưu tiên theo hướng {role}.",
        ]
        reasons = _direction_reasons(candidate, report, matches)
        if reasons:
            lines.extend(["", "Lý do:", *[f"- {reason}" for reason in reasons[:3]]])
        if alternatives:
            lines.extend(["", "Hướng thay thế:", *[f"- {item}" for item in alternatives[:2]]])
        lines.extend([
            "",
            "Gợi ý tiếp theo:",
            "- Tiếp tục củng cố nhóm kỹ năng cốt lõi trước khi mở rộng sang hướng gần kề.",
        ])
        return "\n".join(lines)

    if intent == INTENT_LEARNING_PLAN:
        return _build_career_path_simulator_answer(question, candidate, report, matches, related_job)

    if intent == INTENT_CV_IMPROVEMENT:
        parsed_skills = candidate.get("parsed_skills") or []
        lines = [
            "Việc nên chỉnh trong CV:",
            "- Giữ tiêu đề hồ sơ bám sát vị trí mục tiêu.",
            "- Làm rõ các dự án hoặc kinh nghiệm liên quan nhất.",
            "- Sắp xếp kỹ năng theo đúng nhóm công việc đang ứng tuyển.",
        ]
        if parsed_skills:
            lines.append("- Nhấn mạnh các kỹ năng nổi bật như " + ", ".join(parsed_skills[:5]) + ".")
        return "\n".join(lines)

    if intent == INTENT_COVER_LETTER:
        return "\n".join([
            "Khi viết thư xin việc, bạn nên tập trung vào:",
            "- Vì sao bạn phù hợp với vị trí đang nhắm tới.",
            "- Những kỹ năng hoặc kinh nghiệm khớp trực tiếp với JD.",
            "- Cách bạn bù đắp các kỹ năng còn thiếu trong ngắn hạn.",
            "",
            "Gợi ý tiếp theo:",
            "- Bạn có thể dùng chức năng tạo Cover Letter bằng AI rồi chỉnh lại theo điểm mạnh của hồ sơ.",
        ])

    if intent == INTENT_INTERVIEW_PREP:
        matched = _collect_matched_skills(matches)
        missing = _collect_missing_skills(matches, report)
        lines = [
            "Những điểm mạnh nên nhấn mạnh khi phỏng vấn:",
        ]
        if matched:
            lines.extend(f"- {skill}" for skill in matched[:4])
        else:
            lines.append("- Nhấn mạnh các kỹ năng và dự án gần nhất với vị trí đang ứng tuyển.")
        lines.extend([
            "",
            "Cách trình bày:",
            "- Nêu ngắn gọn vai trò của bạn trong dự án, việc bạn đã làm và kết quả đạt được.",
        ])
        if missing:
            lines.append("- Với kỹ năng còn thiếu như " + ", ".join(missing[:2]) + ", hãy trả lời theo hướng đã có kế hoạch học và có thể bắt kịp nhanh.")
        return "\n".join(lines)

    if intent == INTENT_GENERAL_CAREER:
        role = report.get("nghe_de_xuat") or related_job.get("title") or "hướng nghề hiện tại"
        strengths = extract_report_skill_hints(report).get("strength_categories") or []
        lines = [
            f"Hướng nghề phù hợp nhất hiện tại là: {role}.",
        ]
        if strengths:
            lines.extend(["", "Nhóm năng lực nổi bật:", *[f"- {item}" for item in strengths[:4]]])
        lines.extend([
            "",
            "Bạn có thể hỏi tiếp:",
            "- Kỹ năng còn thiếu để tăng độ phù hợp.",
            "- Công việc nào nên ưu tiên xem hoặc ứng tuyển.",
            "- Cách cải thiện CV hoặc chuẩn bị phỏng vấn.",
        ])
        return "\n".join(lines)

    return OUT_OF_SCOPE_MESSAGE


def _score_intents(normalized: str) -> dict[str, int]:
    scored_rules = {
        INTENT_INTERVIEW_PREP: [
            ("phong van", 6),
            ("phỏng vấn", 6),
            ("interview", 6),
            ("diem manh", 4),
            ("điểm mạnh", 4),
            ("nhan manh", 4),
            ("nhấn mạnh", 4),
        ],
        INTENT_COVER_LETTER: [
            ("thu xin viec", 6),
            ("thư xin việc", 6),
            ("cover letter", 6),
        ],
        INTENT_NEXT_STEP_ACTION: [
            ("lam gi truoc", 8),
            ("làm gì trước", 8),
            ("nen lam gi", 7),
            ("nên làm gì", 7),
            ("trong tuan nay", 7),
            ("trong tuần này", 7),
            ("uu tien gi nhat", 7),
            ("ưu tiên gì nhất", 7),
            ("buoc dau tien", 7),
            ("bước đầu tiên", 7),
            ("viec nen lam truoc", 7),
            ("việc nên làm trước", 7),
            ("tang co hoi ung tuyen", 6),
            ("tăng cơ hội ứng tuyển", 6),
        ],
        INTENT_JOB_RECOMMENDATION: [
            ("job nao", 7),
            ("job nào", 7),
            ("cong viec", 5),
            ("công việc", 5),
            ("apply", 5),
            ("ung tuyen", 4),
            ("ứng tuyển", 4),
            ("vi tri nao", 4),
            ("vị trí nào", 4),
            ("gan nhat", 4),
            ("gần nhất", 4),
        ],
        INTENT_LEARNING_PLAN: [
            ("ke hoach", 7),
            ("kế hoạch", 7),
            ("lo trinh", 7),
            ("lộ trình", 7),
            ("roadmap", 7),
            ("career path", 7),
            ("30 ngay", 7),
            ("30 ngày", 7),
            ("60 ngay", 7),
            ("60 ngày", 7),
            ("90 ngay", 8),
            ("90 ngày", 8),
            ("30 60 90", 8),
            ("giai doan", 6),
            ("giai đoạn", 6),
            ("3 thang", 6),
            ("3 tháng", 6),
            ("6 thang", 6),
            ("6 tháng", 6),
        ],
        INTENT_CAREER_DIRECTION: [
            ("nen theo", 7),
            ("nên theo", 7),
            ("huong khac", 6),
            ("hướng khác", 6),
            ("dinh huong", 6),
            ("định hướng", 6),
            ("huong chinh", 5),
            ("hướng chính", 5),
            ("huong thay the", 5),
            ("hướng thay thế", 5),
        ],
        INTENT_SKILL_GAP: [
            ("thieu ky nang", 7),
            ("thiếu kỹ năng", 7),
            ("thieu", 3),
            ("thiếu", 3),
            ("ky nang", 3),
            ("kỹ năng", 3),
            ("hoc gi", 6),
            ("học gì", 6),
            ("bo sung", 5),
            ("bổ sung", 5),
            ("can hoc", 5),
            ("cần học", 5),
        ],
        INTENT_MATCHING_EXPLANATION: [
            ("matching", 7),
            ("match", 6),
            ("diem phu hop", 6),
            ("điểm phù hợp", 6),
            ("vi sao", 5),
            ("vì sao", 5),
        ],
        INTENT_CV_IMPROVEMENT: [
            ("cv", 6),
            ("ho so", 5),
            ("hồ sơ", 5),
            ("sua", 4),
            ("sửa", 4),
            ("chinh", 4),
            ("chỉnh", 4),
        ],
    }

    scores: dict[str, int] = {}
    for intent, rules in scored_rules.items():
        score = 0
        for keyword, weight in rules:
            if keyword in normalized:
                score += weight
        if score > 0:
            scores[intent] = score
    return scores


def _pick_intent(scores: dict[str, int]) -> str:
    priority = {
        INTENT_INTERVIEW_PREP: 10,
        INTENT_COVER_LETTER: 9,
        INTENT_NEXT_STEP_ACTION: 8,
        INTENT_LEARNING_PLAN: 7,
        INTENT_CAREER_DIRECTION: 6,
        INTENT_JOB_RECOMMENDATION: 5,
        INTENT_SKILL_GAP: 4,
        INTENT_MATCHING_EXPLANATION: 3,
        INTENT_CV_IMPROVEMENT: 2,
    }

    return max(scores.items(), key=lambda item: (item[1], priority.get(item[0], 0)))[0]


def _looks_like_learning_plan_request(normalized: str) -> bool:
    plan_markers = [
        "ke hoach", "kế hoạch", "lo trinh", "lộ trình", "giai doan", "giai đoạn",
        "roadmap", "career path", "30 ngay", "30 ngày", "60 ngay", "60 ngày",
        "90 ngay", "90 ngày", "30 60 90", "3 thang", "3 tháng", "6 thang", "6 tháng",
    ]
    direction_markers = [
        "huong chinh", "hướng chính", "huong thay the", "hướng thay thế",
    ]
    return any(marker in normalized for marker in plan_markers) and any(
        marker in normalized for marker in direction_markers
    )


def _is_out_of_scope(message: str, *, history: list[dict] | None = None, context: dict | None = None) -> bool:
    normalized = normalize_search_text(message)
    history = history or []
    context = context or {}

    if any(keyword in normalized for keyword in DOMAIN_KEYWORDS):
        return False

    if _is_follow_up_question(normalized) and (_has_chat_context(context) or _history_is_in_scope(history)):
        return False

    if "?" not in message and len(normalized.split()) <= 2:
        return False
    return True


def _is_follow_up_question(normalized: str) -> bool:
    follow_up_markers = [
        "vay", "vậy", "the con", "thế còn", "con huong", "còn hướng",
        "tiep theo", "tiếp theo", "truoc do", "trước đó", "luc nay", "lúc này",
        "giai doan", "giai đoạn", "ke hoach", "kế hoạch", "lo trinh", "lộ trình",
        "huong chinh", "hướng chính", "huong thay the", "hướng thay thế",
    ]
    return any(marker in normalized for marker in follow_up_markers)


def _last_in_scope_intent(history: list[dict]) -> str | None:
    for item in reversed(normalize_chat_history_items(history)[-6:]):
        intent = item.get("intent")
        if intent and intent != INTENT_OUT_OF_SCOPE:
            return intent
    return None


def _has_chat_context(context: dict) -> bool:
    context = ensure_chat_mapping(context)
    return bool(
        context.get("conversation_summary")
        or ensure_chat_mapping(context.get("candidate_profile")).get("parsed_skills")
        or context.get("career_report")
        or context.get("top_matching_jobs")
        or context.get("related_job")
    )


def _history_is_in_scope(history: list[dict]) -> bool:
    for item in reversed(normalize_chat_history_items(history)[-6:]):
        normalized = normalize_search_text(item.get("content", ""))
        if any(keyword in normalized for keyword in DOMAIN_KEYWORDS):
            return True
    return False


def _collect_missing_skills(matches: list[dict], report: dict) -> list[str]:
    result: list[str] = []
    for item in normalize_match_entries(matches):
        for skill in _normalize_string_list(item.get("missing_skills")):
            if skill and skill not in result:
                result.append(skill)

    extra = extract_report_skill_hints(report).get("skills") or []
    for skill in extra:
        if skill and skill not in result:
            result.append(skill)
    return result


def _collect_matched_skills(matches: list[dict]) -> list[str]:
    result: list[str] = []
    for item in normalize_match_entries(matches):
        for skill in _normalize_string_list(item.get("matched_skills")):
            if skill and skill not in result:
                result.append(skill)
    return result


def _alternative_roles(report: dict, primary_role: str) -> list[str]:
    roles = extract_report_skill_hints(report).get("recommended_roles") or []
    return [item for item in roles if item and item != primary_role]


def _direction_reasons(candidate: dict, report: dict, matches: list[dict]) -> list[str]:
    reasons: list[str] = []
    parsed_skills = candidate.get("parsed_skills") or []
    strengths = extract_report_skill_hints(report).get("strength_categories") or []
    missing = _collect_missing_skills(matches, report)

    if parsed_skills:
        reasons.append("Hồ sơ hiện đã có nền tảng ở các kỹ năng như " + ", ".join(parsed_skills[:4]) + ".")
    if strengths:
        reasons.append("Các nhóm năng lực nổi bật hiện tại gồm " + ", ".join(strengths[:3]) + ".")
    if missing:
        reasons.append("Khoảng cách kỹ năng còn thiếu vẫn có thể bù theo từng giai đoạn, trước mắt là " + ", ".join(missing[:3]) + ".")
    return reasons


def _job_candidates(matches: list[dict]) -> list[str]:
    jobs: list[str] = []

    for item in normalize_match_entries(matches)[:3]:
        title = item.get("job_title")
        if title and title not in jobs:
            jobs.append(title)

    return jobs


def _rag_job_candidates(rag_context: dict) -> list[str]:
    jobs = []
    for item in ensure_chat_list(rag_context.get("job_snippets")):
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        company = str(item.get("company") or "").strip()
        location = str(item.get("location") or "").strip()
        skills = _normalize_string_list(item.get("skills"))[:3]
        if not title:
            continue
        label = title
        if company:
            label += f" tại {company}"
        extras = []
        if location:
            extras.append(location)
        if skills:
            extras.append("kỹ năng: " + ", ".join(skills))
        if extras:
            label += " (" + "; ".join(extras) + ")"
        jobs.append(label)
    return jobs[:5]


def _build_career_path_simulator_answer(
    question: str,
    candidate: dict,
    report: dict,
    matches: list[dict],
    related_job: dict,
) -> str:
    explicit_focus = _extract_learning_focus(question)
    target_industry = candidate.get("ten_nganh_nghe_muc_tieu")
    target_role = (
        candidate.get("vi_tri_ung_tuyen_muc_tieu")
        or report.get("nghe_de_xuat")
        or related_job.get("title")
        or (matches[0].get("job_title") if matches else None)
        or "vị trí mục tiêu hiện tại"
    )
    current_skills = _unique_list([
        *(candidate.get("parsed_skills") or []),
        *(candidate.get("builder_skills") or []),
        *_collect_matched_skills(matches),
    ])

    if explicit_focus:
        return _build_explicit_learning_focus_answer(
            explicit_focus,
            current_skills=current_skills,
            target_industry=target_industry,
        )

    missing_skills = _collect_missing_skills(matches, report)
    jobs = _job_candidates(matches)
    alternative_roles = _alternative_roles(report, str(target_role))
    current_level = _infer_current_level(candidate, matches)

    lines = [
        "Mô phỏng lộ trình nghề nghiệp 30/60/90 ngày:",
        f"- Mục tiêu chính: {target_role}.",
        f"- Mức hiện tại: {current_level}.",
    ]
    if target_industry:
        lines.append(f"- Ngành mục tiêu: {target_industry}.")

    if current_skills:
        lines.extend([
            "",
            "Nền tảng đang có:",
            "- " + ", ".join(current_skills[:6]) + ".",
        ])

    if missing_skills:
        lines.extend([
            "",
            "Khoảng cách cần bù:",
            "- " + ", ".join(missing_skills[:6]) + ".",
        ])

    lines.extend([
        "",
        "30 ngày:",
        "- Chốt 1 phiên bản CV bám sát mục tiêu, ưu tiên đưa kỹ năng và dự án liên quan lên phần đầu.",
        "- Ôn lại nền tảng cốt lõi của vị trí mục tiêu và ghi lại 3 ví dụ kinh nghiệm/dự án có thể kể khi phỏng vấn.",
    ])
    if missing_skills:
        lines.append(f"- Học sâu kỹ năng ưu tiên số 1: {missing_skills[0]}; tạo một bài thực hành nhỏ để chứng minh năng lực.")
    elif current_skills:
        lines.append(f"- Củng cố kỹ năng mạnh nhất hiện tại: {current_skills[0]}; biến nó thành điểm nhấn trong CV.")

    lines.extend([
        "",
        "60 ngày:",
        "- Hoàn thiện một dự án hoặc bài phân tích tình huống có đầu ra đo được, ví dụ API, bảng điều khiển, chiến dịch, quy trình hoặc báo cáo tùy ngành.",
    ])
    if len(missing_skills) >= 2:
        lines.append("- Bổ sung tiếp: " + ", ".join(missing_skills[1:4]) + ".")
    lines.append("- Chạy lại đối sánh hoặc hỏi trợ lý so sánh CV với vị trí mục tiêu để kiểm tra điểm còn yếu.")

    lines.extend([
        "",
        "90 ngày:",
        "- Tạo bản CV tối ưu theo từng JD, chuẩn bị thư xin việc ngắn và luyện phỏng vấn theo các câu hỏi thường gặp của vị trí mục tiêu.",
    ])
    if jobs:
        lines.append("- Ưu tiên ứng tuyển hoặc theo dõi các vị trí gần nhất: " + "; ".join(jobs[:3]) + ".")
    else:
        lines.append("- Chọn 2-3 JD thật trong hệ thống để đối chiếu lại kỹ năng và yêu cầu tuyển dụng.")

    lines.extend([
        "",
        "Mốc kiểm tra:",
        "- Sau 30 ngày: CV rõ mục tiêu hơn và có ít nhất 1 minh chứng mới.",
        "- Sau 60 ngày: giảm được 1-3 khoảng cách kỹ năng chính.",
        "- Sau 90 ngày: có thể ứng tuyển tự tin hơn vào nhóm vị trí mục tiêu.",
    ])

    if alternative_roles:
        lines.extend([
            "",
            "Hướng thay thế nếu muốn mở rộng:",
            *[f"- {role}" for role in alternative_roles[:2]],
        ])

    return "\n".join(lines)


def _build_explicit_learning_focus_answer(
    focus: dict,
    *,
    current_skills: list[str],
    target_industry: str | None = None,
) -> str:
    label = focus["label"]
    track = focus["track"]
    track_config = _learning_track_config(track)
    relevant_skills = _filter_focus_relevant_skills(current_skills, track_config["keywords"])
    current_level = _infer_focus_level(relevant_skills)

    lines = [
        "Mô phỏng lộ trình nghề nghiệp 30/60/90 ngày:",
        f"- Mục tiêu chính: {label}.",
        f"- Mức hiện tại: {current_level}.",
    ]
    if target_industry:
        lines.append(f"- Ngành mục tiêu đang quan tâm: {target_industry}.")

    if relevant_skills:
        lines.extend([
            "",
            "Nền tảng đang có thể tận dụng:",
            "- " + ", ".join(relevant_skills[:6]) + ".",
        ])

    lines.extend([
        "",
        "Trọng tâm nên học:",
        *[f"- {topic}" for topic in track_config["core_topics"]],
        "",
        "30 ngày:",
        *[f"- {item}" for item in track_config["day30"]],
        "",
        "60 ngày:",
        *[f"- {item}" for item in track_config["day60"]],
        "",
        "90 ngày:",
        *[f"- {item}" for item in track_config["day90"]],
        "",
        "Mốc kiểm tra:",
        *[f"- {item}" for item in track_config["checkpoints"]],
    ])

    return "\n".join(lines)


def _infer_current_level(candidate: dict, matches: list[dict]) -> str:
    years = candidate.get("kinh_nghiem_nam")
    try:
        years = int(years or 0)
    except (TypeError, ValueError):
        years = 0

    top_score = 0.0
    normalized_matches = normalize_match_entries(matches)
    if normalized_matches:
        try:
            top_score = float(normalized_matches[0].get("score") or 0)
        except (TypeError, ValueError):
            top_score = 0.0

    if years >= 4 or top_score >= 75:
        return "đang ở mức khá vững, nên tối ưu chiều sâu và hồ sơ dự án"
    if years >= 2 or top_score >= 55:
        return "đã có nền tảng, nên bù khoảng cách kỹ năng và tăng minh chứng thực tế"
    return "giai đoạn intern/fresher, nên ưu tiên nền tảng và dự án chứng minh năng lực"


def _unique_list(items: Iterable) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if not item:
            continue
        value = str(item).strip()
        key = normalize_search_text(value)
        if not value or key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def _normalize_string_list(value) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for item in ensure_chat_list(value):
        text = ""

        if isinstance(item, dict):
            text = str(
                item.get("skill_name")
                or item.get("name")
                or item.get("ten")
                or item.get("title")
                or ""
            ).strip()
        else:
            text = str(item or "").strip()

        if not text:
            continue

        key = normalize_search_text(text)
        if key in seen:
            continue

        seen.add(key)
        normalized.append(text)

    return normalized


def _extract_learning_focus(question: str) -> dict | None:
    match = re.search(r"\b(?:hoc|học)\s+(.+?)(?:[?.!,]|$)", question, flags=re.IGNORECASE)
    if not match:
        return None

    raw_topic = re.sub(
        r"^(?:ve|về|theo|hướng|huong|cho|làm|lam)\s+",
        "",
        match.group(1).strip(),
        flags=re.IGNORECASE,
    ).strip(" \t\r\n.:;!?")

    if not raw_topic:
        return None

    normalized = normalize_search_text(raw_topic)

    if "vue" in normalized:
        return {"label": "Frontend Vue.js", "track": "frontend_vue"}
    if "react" in normalized:
        return {"label": "Frontend React", "track": "frontend_react"}
    if "laravel" in normalized:
        return {"label": "Backend Laravel", "track": "backend_laravel"}
    if any(marker in normalized for marker in ["frontend", "html", "css", "javascript", "typescript", "web ui"]):
        return {"label": _pretty_topic_label(raw_topic), "track": "frontend_web"}
    if any(marker in normalized for marker in ["backend", "api", "node", "spring", "django", "php", "java"]):
        return {"label": _pretty_topic_label(raw_topic), "track": "backend_web"}

    if len(normalized.split()) > 8:
        return None

    return {"label": _pretty_topic_label(raw_topic), "track": "generic_learning"}


def _pretty_topic_label(value: str) -> str:
    compact = re.sub(r"\s+", " ", value).strip()
    if not compact:
        return "chủ đề học hiện tại"

    lower = compact.lower()
    replacements = {
        "vuejs": "Vue.js",
        "reactjs": "React",
        "nodejs": "Node.js",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "frontend": "Frontend",
        "backend": "Backend",
        "laravel": "Laravel",
        "php": "PHP",
        "html": "HTML",
        "css": "CSS",
    }

    words = []
    for part in compact.split():
        words.append(replacements.get(part.lower(), part.capitalize() if part.islower() else part))

    return " ".join(words)


def _learning_track_config(track: str) -> dict:
    configs = {
        "frontend_vue": {
            "keywords": ["vue", "javascript", "typescript", "html", "css", "frontend", "pinia", "router", "api"],
            "core_topics": [
                "HTML/CSS responsive, JavaScript hiện đại và cách tổ chức component.",
                "Vue.js nền tảng: props/emit, computed, watch, lifecycle, form binding.",
                "Vue Router, Pinia và cách gọi API để nối giao diện với dữ liệu thật.",
            ],
            "day30": [
                "Ôn HTML, CSS, JavaScript ES6+, DOM, async/await và cách đọc dữ liệu từ API.",
                "Học Vue.js nền tảng: component, props/emit, computed, watch, lifecycle và xử lý form.",
                "Làm 2-3 bài thực hành nhỏ như todo list, bộ lọc sản phẩm hoặc form validation bằng Vue.",
            ],
            "day60": [
                "Học Vue Router, Pinia, tổ chức thư mục dự án và tái sử dụng component.",
                "Kết nối API thật bằng fetch/axios, xử lý loading, lỗi và trạng thái đăng nhập cơ bản.",
                "Hoàn thiện một dự án nhỏ như dashboard quản trị, job board mini hoặc trang bán hàng đơn giản.",
            ],
            "day90": [
                "Nâng dự án lên mức có CRUD đầy đủ, auth cơ bản, responsive và deploy được.",
                "Tối ưu code: tách component hợp lý, lazy loading, quy ước đặt tên và README rõ ràng.",
                "Chuẩn bị 1-2 case study để đưa vào CV hoặc hồ sơ dự án khi ứng tuyển frontend Vue.js.",
            ],
            "checkpoints": [
                "Sau 30 ngày: tự dựng được giao diện nhỏ bằng Vue và hiểu reactivity/component.",
                "Sau 60 ngày: có một dự án Vue hoàn chỉnh kết nối API thật.",
                "Sau 90 ngày: có thể trình bày dự án, tối ưu CV và bắt đầu ứng tuyển vị trí frontend Vue.js.",
            ],
        },
        "frontend_react": {
            "keywords": ["react", "javascript", "typescript", "html", "css", "frontend", "redux", "router", "api"],
            "core_topics": [
                "HTML/CSS responsive, JavaScript hiện đại và tư duy chia UI thành component.",
                "React nền tảng: props, state, effect, form, lifecycle theo tư duy hàm.",
                "Routing, quản lý state và kết nối API để xây giao diện có dữ liệu thật.",
            ],
            "day30": [
                "Ôn HTML, CSS, JavaScript ES6+, array methods, async/await và fetch API.",
                "Học React nền tảng: JSX, props, state, useEffect, form control, component composition.",
                "Làm 2-3 bài thực hành nhỏ như todo list, form tìm kiếm hoặc bộ lọc dữ liệu.",
            ],
            "day60": [
                "Học React Router, state management cơ bản và tổ chức cấu trúc dự án.",
                "Kết nối API thật, xử lý loading, lỗi, pagination và auth flow cơ bản.",
                "Hoàn thiện một dự án nhỏ như dashboard, trang quản trị hoặc job board mini.",
            ],
            "day90": [
                "Nâng dự án lên mức có CRUD đầy đủ, auth cơ bản, responsive và deploy được.",
                "Viết README, làm sạch component tree và chuẩn hóa luồng state.",
                "Chuẩn bị 1-2 case study để đưa vào CV hoặc hồ sơ dự án khi ứng tuyển frontend React.",
            ],
            "checkpoints": [
                "Sau 30 ngày: tự dựng được giao diện React nhỏ với state và form cơ bản.",
                "Sau 60 ngày: có một dự án React hoàn chỉnh kết nối API thật.",
                "Sau 90 ngày: có thể trình bày dự án và bắt đầu ứng tuyển vị trí frontend React.",
            ],
        },
        "frontend_web": {
            "keywords": ["frontend", "javascript", "typescript", "html", "css", "ui", "ux", "api", "responsive"],
            "core_topics": [
                "HTML/CSS responsive, JavaScript hiện đại và cấu trúc giao diện web.",
                "Tư duy component, form, gọi API và quản lý trạng thái giao diện.",
                "Dự án thực hành có dữ liệu thật và quy trình tối ưu CV/portfolio frontend.",
            ],
            "day30": [
                "Ôn HTML, CSS, JavaScript ES6+, DOM, async/await và responsive layout.",
                "Làm 2-3 bài thực hành nhỏ như landing page, bộ lọc dữ liệu hoặc form validation.",
                "Chọn một framework frontend chính để theo sâu và dựng lại giao diện thật bằng framework đó.",
            ],
            "day60": [
                "Học routing, state management cơ bản và cách nối giao diện với API thật.",
                "Hoàn thiện một dự án frontend nhỏ có dữ liệu động và trải nghiệm người dùng rõ ràng.",
                "Viết README, chụp màn hình dự án và mô tả vai trò bản thân trong từng phần.",
            ],
            "day90": [
                "Nâng dự án lên mức có CRUD, auth cơ bản, responsive và deploy được.",
                "Rà soát accessibility, tốc độ tải trang và quy ước đặt tên component.",
                "Chuẩn bị hồ sơ dự án để đưa vào CV khi ứng tuyển vị trí frontend.",
            ],
            "checkpoints": [
                "Sau 30 ngày: nắm chắc nền tảng giao diện web và tự dựng được trang hoàn chỉnh.",
                "Sau 60 ngày: có một dự án frontend nhỏ kết nối dữ liệu thật.",
                "Sau 90 ngày: có thể dùng dự án làm minh chứng khi ứng tuyển vị trí frontend.",
            ],
        },
        "backend_laravel": {
            "keywords": ["laravel", "php", "mysql", "sql", "backend", "api", "eloquent", "composer", "docker", "redis"],
            "core_topics": [
                "PHP nền tảng, OOP, Composer và vòng đời request trong Laravel.",
                "Routing, controller, form request, migration, Eloquent và auth/API.",
                "Dự án REST API có validation, phân quyền, test và deploy cơ bản.",
            ],
            "day30": [
                "Ôn PHP, OOP, Composer và cách Laravel tổ chức route, controller, model, request.",
                "Học migration, Eloquent ORM, validation, quan hệ dữ liệu và xử lý lỗi API JSON.",
                "Làm một dự án CRUD nhỏ bằng Laravel như quản lý bài viết, công việc hoặc sản phẩm.",
            ],
            "day60": [
                "Mở rộng sang REST API, auth bằng Sanctum, upload file, filter, pagination và policy cơ bản.",
                "Học queue, cache, event hoặc mail ở mức đủ dùng cho một dự án backend thực tế.",
                "Hoàn thiện một API project có tài liệu endpoint và dữ liệu mẫu rõ ràng.",
            ],
            "day90": [
                "Bổ sung test, logging, cấu hình môi trường, Docker hoặc deploy demo lên server.",
                "Rà soát performance: query, eager loading, validation flow và cấu trúc service/repository nếu cần.",
                "Chuẩn bị 1-2 case study backend Laravel để đưa vào CV khi ứng tuyển.",
            ],
            "checkpoints": [
                "Sau 30 ngày: tự dựng được CRUD Laravel có migration, relation và validation.",
                "Sau 60 ngày: có một API project hoàn chỉnh với auth và tài liệu endpoint.",
                "Sau 90 ngày: có thể trình bày dự án, test/deploy cơ bản và bắt đầu ứng tuyển backend Laravel.",
            ],
        },
        "backend_web": {
            "keywords": ["backend", "api", "server", "database", "sql", "docker", "auth", "queue", "cache"],
            "core_topics": [
                "HTTP, REST API, database, auth và cấu trúc service phía server.",
                "Validation, logging, query tối ưu và xử lý lỗi rõ ràng.",
                "Dự án backend có tài liệu endpoint, test và deploy cơ bản.",
            ],
            "day30": [
                "Ôn nền tảng HTTP, REST API, database, auth cơ bản và cách tổ chức code backend.",
                "Làm một dự án CRUD nhỏ có validation, filter, pagination và error handling rõ ràng.",
                "Hiểu cách thiết kế bảng dữ liệu, relation và vòng đời request-response.",
            ],
            "day60": [
                "Bổ sung auth, phân quyền, upload file, logging và background job nếu stack hỗ trợ.",
                "Hoàn thiện một API project có tài liệu endpoint và dữ liệu mẫu rõ ràng.",
                "Học cách đọc log, debug lỗi và tối ưu query chậm.",
            ],
            "day90": [
                "Bổ sung test, Docker hoặc deploy demo để mô phỏng môi trường thật.",
                "Rà soát performance, cấu trúc service và khả năng mở rộng của dự án.",
                "Chuẩn bị 1-2 case study backend để đưa vào CV khi ứng tuyển.",
            ],
            "checkpoints": [
                "Sau 30 ngày: dựng được CRUD API với relation và validation rõ ràng.",
                "Sau 60 ngày: có một API project có auth và tài liệu endpoint.",
                "Sau 90 ngày: có thể trình bày dự án backend như một minh chứng ứng tuyển.",
            ],
        },
        "generic_learning": {
            "keywords": [],
            "core_topics": [
                "Nền tảng cốt lõi của chủ đề đang học.",
                "Bài thực hành nhỏ để chuyển từ lý thuyết sang làm thật.",
                "Một dự án hoàn chỉnh đủ để đưa vào hồ sơ dự án hoặc CV.",
            ],
            "day30": [
                "Ôn lại khái niệm nền tảng, cài môi trường và làm 2-3 bài thực hành ngắn bám sát chủ đề.",
                "Ghi chú lại các kiến thức cốt lõi theo ngôn ngữ của bản thân để dễ ôn tập.",
                "Chốt một mini project nhỏ để kiểm tra khả năng áp dụng kiến thức vừa học.",
            ],
            "day60": [
                "Mở rộng mini project thành một dự án nhỏ có đầu ra đo được và dữ liệu rõ ràng.",
                "Bù các phần còn yếu xuất hiện lặp lại trong lúc làm dự án.",
                "Viết README hoặc tài liệu ngắn mô tả mục tiêu, chức năng và cách chạy dự án.",
            ],
            "day90": [
                "Hoàn thiện một dự án có thể dùng làm minh chứng năng lực.",
                "Rà soát lại code, cấu trúc, tài liệu và các phần có thể giải thích khi phỏng vấn.",
                "Tổng hợp lại phần đã học để đưa vào CV hoặc hồ sơ dự án nếu cần ứng tuyển.",
            ],
            "checkpoints": [
                "Sau 30 ngày: hiểu khái niệm nền tảng và hoàn thành được bài thực hành nhỏ.",
                "Sau 60 ngày: có một dự án nhỏ hoạt động được và giải thích được lựa chọn kỹ thuật.",
                "Sau 90 ngày: có một minh chứng năng lực đủ rõ để đưa vào hồ sơ ứng tuyển.",
            ],
        },
    }

    return configs.get(track, configs["generic_learning"])


def _filter_focus_relevant_skills(skills: list[str], keywords: list[str]) -> list[str]:
    if not keywords:
        return []

    result: list[str] = []
    for skill in skills:
        normalized_skill = normalize_search_text(skill)
        if any(keyword in normalized_skill for keyword in keywords) and skill not in result:
            result.append(skill)

    return result


def _infer_focus_level(relevant_skills: list[str]) -> str:
    if len(relevant_skills) >= 4:
        return "đã có nền tảng ban đầu, nên chuyển dần sang dự án thực chiến và hồ sơ dự án"
    if len(relevant_skills) >= 2:
        return "đã chạm vào chủ đề này, nên hệ thống hóa kiến thức và tăng thực hành có đầu ra"
    return "đang ở giai đoạn xây nền, nên ưu tiên học chắc khái niệm cốt lõi trước khi mở rộng"
