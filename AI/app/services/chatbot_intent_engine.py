from __future__ import annotations

from typing import Iterable

from app.services.skill_catalog import normalize_search_text


OUT_OF_SCOPE_MESSAGE = (
    "Tôi được thiết kế để hỗ trợ tư vấn nghề nghiệp, giải thích hồ sơ CV, kết quả matching và thông tin tuyển dụng trong hệ thống. "
    "Với câu hỏi này, tôi chưa phải là trợ lý phù hợp. Bạn có thể hỏi tôi về nghề nghiệp, kỹ năng cần bổ sung, CV, thư xin việc hoặc công việc phù hợp với hồ sơ của bạn."
)

INTENT_OUT_OF_SCOPE = "out_of_scope"
INTENT_SKILL_GAP = "skill_gap"
INTENT_MATCHING_EXPLANATION = "matching_explanation"
INTENT_JOB_RECOMMENDATION = "job_recommendation"
INTENT_NEXT_STEP_ACTION = "next_step_action"
INTENT_CAREER_DIRECTION = "career_direction"
INTENT_LEARNING_PLAN = "learning_plan"
INTENT_CV_IMPROVEMENT = "cv_improvement"
INTENT_COVER_LETTER = "cover_letter"
INTENT_INTERVIEW_PREP = "interview_prep"
INTENT_GENERAL_CAREER = "general_career"

DOMAIN_KEYWORDS = {
    "cv", "ho so", "hồ sơ", "matching", "nghe nghiep", "nghề nghiệp", "ky nang", "kỹ năng",
    "ung tuyen", "ứng tuyển", "job", "cong viec", "công việc", "cover letter", "thu xin viec",
    "thư xin việc", "phong van", "phỏng vấn", "career", "semantic", "skill", "jd", "resume",
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
    INTENT_MATCHING_EXPLANATION: "Giải thích matching",
    INTENT_JOB_RECOMMENDATION: "Gợi ý công việc",
    INTENT_NEXT_STEP_ACTION: "Nên làm gì trước",
    INTENT_CAREER_DIRECTION: "Định hướng nghề",
    INTENT_LEARNING_PLAN: "Lộ trình học",
    INTENT_CV_IMPROVEMENT: "Cải thiện CV",
    INTENT_COVER_LETTER: "Thư xin việc",
    INTENT_INTERVIEW_PREP: "Chuẩn bị phỏng vấn",
    INTENT_GENERAL_CAREER: "Tư vấn nghề nghiệp",
    INTENT_OUT_OF_SCOPE: "Ngoài phạm vi",
}


def resolve_intent(message: str, *, history: list[dict] | None = None, context: dict | None = None) -> str:
    normalized = normalize_search_text(message)
    history = history or []
    context = context or {}

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
    candidate = context.get("candidate_profile") or {}
    report = context.get("career_report") or {}
    matches = context.get("top_matching_jobs") or []
    semantic_jobs = context.get("semantic_jobs") or []
    related_job = context.get("related_job") or {}
    normalized = normalize_search_text(question)

    if intent == INTENT_SKILL_GAP:
        missing = _collect_missing_skills(matches, report)
        if not missing:
            return (
                "Hiện tại tôi chưa thấy kỹ năng còn thiếu nổi bật từ hồ sơ và các job đã đối sánh.\n"
                "- Bạn có thể parse thêm JD hoặc tạo matching mới để tôi phân tích sát hơn."
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
            return "Hiện tôi chưa có dữ liệu matching để giải thích điểm phù hợp. Bạn có thể chạy Generate Matching trước."

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
        jobs = _job_candidates(semantic_jobs, matches)
        wants_apply = any(keyword in normalized for keyword in ["apply", "ứng tuyển", "ung tuyen", "apply ngay"])
        if not jobs:
            return (
                "Hiện tôi chưa có đủ dữ liệu để gợi ý job cụ thể.\n"
                "- Bạn nên tạo matching mới hoặc chọn thêm JD liên quan để tôi đề xuất sát hơn."
            )

        lines = [
            "Gợi ý công việc nên xem:",
            *[f"- {job}" for job in jobs[:3]],
        ]
        if wants_apply:
            lines.extend([
                "",
                "Ưu tiên trước:",
                f"- Bạn có thể ưu tiên apply vị trí {jobs[0]} vì đây là job gần nhất với hồ sơ hiện tại.",
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
            "- Sau khi cập nhật CV và bù khoảng trống chính, hãy xem lại các job gần nhất trong hệ thống để chọn vị trí phù hợp nhất.",
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
        role = report.get("nghe_de_xuat") or related_job.get("title") or "Backend Developer"
        parsed_skills = candidate.get("parsed_skills") or []
        missing = _collect_missing_skills(matches, report)
        lines = [
            "Đề xuất chính:",
            f"- Mục tiêu phù hợp nhất hiện tại là {role}.",
            "",
            "Kế hoạch theo từng giai đoạn:",
            "Giai đoạn 1:",
            "- Rà soát lại CV và dự án để nhấn mạnh các kỹ năng đang có.",
        ]
        if parsed_skills:
            lines.append("- Giữ nổi bật các kỹ năng nền như " + ", ".join(parsed_skills[:3]) + ".")
        lines.extend([
            "",
            "Giai đoạn 2:",
            "- Bổ sung các kỹ năng còn thiếu xuất hiện nhiều trong job mục tiêu.",
        ])
        if missing:
            lines.append("- Ưu tiên lần lượt: " + ", ".join(missing[:4]) + ".")
        lines.extend([
            "- Hoàn thành ít nhất 1 bài thực hành hoặc dự án nhỏ bám sát vị trí mục tiêu.",
            "",
            "Giai đoạn 3:",
            "- Cập nhật lại CV theo kỹ năng mới đã học.",
            "- Chọn 1-2 job gần nhất trong hệ thống để bắt đầu ứng tuyển.",
            "- Chuẩn bị cách trình bày điểm mạnh, điểm còn thiếu và kế hoạch học tiếp khi phỏng vấn.",
        ])
        return "\n".join(lines)

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
        strengths = ((report.get("goi_y_ky_nang_bo_sung") or {}).get("strength_categories") or [])
        lines = [
            f"Hướng nghề phù hợp nhất hiện tại là: {role}.",
        ]
        if strengths:
            lines.extend(["", "Nhóm năng lực nổi bật:", *[f"- {item}" for item in strengths[:4]]])
        lines.extend([
            "",
            "Bạn có thể hỏi tiếp:",
            "- Kỹ năng còn thiếu để tăng độ phù hợp.",
            "- Job nào nên ưu tiên xem hoặc apply.",
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
        "3 thang", "3 tháng", "6 thang", "6 tháng",
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
    for item in reversed(history[-6:]):
        intent = item.get("intent")
        if intent and intent != INTENT_OUT_OF_SCOPE:
            return intent
    return None


def _has_chat_context(context: dict) -> bool:
    return bool(
        context.get("conversation_summary")
        or (context.get("candidate_profile") or {}).get("parsed_skills")
        or context.get("career_report")
        or context.get("top_matching_jobs")
        or context.get("related_job")
    )


def _history_is_in_scope(history: list[dict]) -> bool:
    for item in reversed(history[-6:]):
        normalized = normalize_search_text(item.get("content", ""))
        if any(keyword in normalized for keyword in DOMAIN_KEYWORDS):
            return True
    return False


def _collect_missing_skills(matches: list[dict], report: dict) -> list[str]:
    result: list[str] = []
    for item in matches:
        for skill in item.get("missing_skills", []) or []:
            if skill and skill not in result:
                result.append(skill)

    extra = ((report.get("goi_y_ky_nang_bo_sung") or {}).get("skills") or [])
    for skill in extra:
        if skill and skill not in result:
            result.append(skill)
    return result


def _collect_matched_skills(matches: list[dict]) -> list[str]:
    result: list[str] = []
    for item in matches:
        for skill in item.get("matched_skills", []) or []:
            if skill and skill not in result:
                result.append(skill)
    return result


def _alternative_roles(report: dict, primary_role: str) -> list[str]:
    roles = ((report.get("goi_y_ky_nang_bo_sung") or {}).get("recommended_roles") or [])
    return [item for item in roles if item and item != primary_role]


def _direction_reasons(candidate: dict, report: dict, matches: list[dict]) -> list[str]:
    reasons: list[str] = []
    parsed_skills = candidate.get("parsed_skills") or []
    strengths = ((report.get("goi_y_ky_nang_bo_sung") or {}).get("strength_categories") or [])
    missing = _collect_missing_skills(matches, report)

    if parsed_skills:
        reasons.append("Hồ sơ hiện đã có nền tảng ở các kỹ năng như " + ", ".join(parsed_skills[:4]) + ".")
    if strengths:
        reasons.append("Các nhóm năng lực nổi bật hiện tại gồm " + ", ".join(strengths[:3]) + ".")
    if missing:
        reasons.append("Khoảng cách kỹ năng còn thiếu vẫn có thể bù theo từng giai đoạn, trước mắt là " + ", ".join(missing[:3]) + ".")
    return reasons


def _job_candidates(semantic_jobs: list[dict], matches: list[dict]) -> list[str]:
    jobs: list[str] = []

    for item in semantic_jobs[:3]:
        title = item.get("title") or item.get("job_title")
        company = item.get("company_name")
        if title:
            label = f"{title} - {company}" if company else title
            if label not in jobs:
                jobs.append(label)

    for item in matches[:3]:
        title = item.get("job_title")
        if title and title not in jobs:
            jobs.append(title)

    return jobs
