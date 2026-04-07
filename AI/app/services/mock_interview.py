from __future__ import annotations

from collections import Counter
import re

from app.core.config import settings
from app.core.logger import get_logger
from app.providers.mock_interview_ollama_provider import OllamaMockInterviewProvider
from app.services.skill_catalog import extract_skills_from_text, normalize_search_text


logger = get_logger(__name__)

MODEL_VERSION = f"mock_interview_v3.0::{settings.mock_interview_provider}::{settings.local_llm_model}"
DEFAULT_MAX_QUESTIONS = 5
MIN_MAX_QUESTIONS = 3
HARD_MAX_QUESTIONS = 7
ollama_provider = OllamaMockInterviewProvider()


def generate_mock_interview_question(
    session_id: int,
    *,
    interview_context: dict | None = None,
    transcript: list[dict] | None = None,
    question_index: int = 1,
    max_questions: int = DEFAULT_MAX_QUESTIONS,
) -> dict:
    interview_context = interview_context or {}
    transcript = transcript or []

    try:
        role_family = _resolve_role_family(interview_context)
        question_plan = _build_question_plan(interview_context)
        resolved_max_questions = _resolve_max_questions(max_questions)
        question_payload = _resolve_initial_question_payload(question_plan, question_index, resolved_max_questions)
        question_payload = _refine_question_payload(question_payload, interview_context, transcript)

        return {
            "success": True,
            "model_version": MODEL_VERSION,
            "data": {
                "session_id": session_id,
                "question_index": question_payload["question_index"],
                "max_questions": resolved_max_questions,
                "question_type": question_payload["question_type"],
                "interview_stage_label": question_payload["interview_stage_label"],
                "focus_skills": question_payload["focus_skills"],
                "suggested_answer_points": question_payload["suggested_answer_points"],
                "question_text": question_payload["question_text"],
                "selection_strategy": question_payload.get("selection_strategy", "initial_plan"),
                "generation_provider": question_payload.get("generation_provider", "rule_based"),
                "role_family": role_family,
            },
            "error": None,
        }
    except Exception as exc:
        logger.exception("Generate mock interview question failed for session_id=%s", session_id)
        return {
            "success": False,
            "model_version": MODEL_VERSION,
            "data": {},
            "error": str(exc),
        }


def evaluate_mock_interview_answer(
    session_id: int,
    *,
    question_payload: dict,
    answer: str,
    interview_context: dict | None = None,
    transcript: list[dict] | None = None,
    max_questions: int = DEFAULT_MAX_QUESTIONS,
) -> dict:
    interview_context = interview_context or {}
    transcript = transcript or []

    try:
        normalized_answer = normalize_search_text(answer)
        role_family = _resolve_role_family(interview_context)
        current_index = int(question_payload.get("question_index") or 1)
        focus_skills = question_payload.get("focus_skills") or []
        question_type = question_payload.get("question_type") or "general"
        resolved_max_questions = _resolve_max_questions(
            int(question_payload.get("max_questions") or max_questions or DEFAULT_MAX_QUESTIONS)
        )

        technical_score = _score_technical_answer(normalized_answer, focus_skills, interview_context, question_type, role_family)
        communication_score = _score_communication_answer(answer)
        jd_fit_score = _score_jd_fit(normalized_answer, interview_context, focus_skills)
        clarity_score = _score_clarity(answer)
        specificity_score = _score_specificity(answer, normalized_answer, focus_skills)
        structure_score = _score_structure(answer)

        total_score = round(
            technical_score * 0.28
            + communication_score * 0.18
            + jd_fit_score * 0.18
            + clarity_score * 0.14
            + specificity_score * 0.12
            + structure_score * 0.10,
            2,
        )

        rubric_breakdown = {
            "technical_score": technical_score,
            "communication_score": communication_score,
            "jd_fit_score": jd_fit_score,
            "clarity_score": clarity_score,
            "specificity_score": specificity_score,
            "structure_score": structure_score,
        }

        strengths = _detect_strengths(answer, normalized_answer, focus_skills, rubric_breakdown)
        weaknesses = _detect_weaknesses(answer, normalized_answer, focus_skills, rubric_breakdown)
        weakest_dimension = min(rubric_breakdown.items(), key=lambda item: item[1])[0]

        feedback_text = _build_feedback_text(
            question_payload=question_payload,
            total_score=total_score,
            rubric_breakdown=rubric_breakdown,
            strengths=strengths,
            weaknesses=weaknesses,
        )

        completed = current_index >= resolved_max_questions
        next_question = None
        if not completed:
            question_plan = _build_question_plan(interview_context)
            evaluation_history = _extract_evaluation_history(transcript)
            next_index = current_index + 1

            if _should_follow_up(question_payload, answer, rubric_breakdown, evaluation_history):
                next_question = _build_follow_up_question(
                    question_payload=question_payload,
                    interview_context=interview_context,
                    weaknesses=weaknesses,
                    weakest_dimension=weakest_dimension,
                    question_index=next_index,
                    max_questions=resolved_max_questions,
                )
            else:
                next_question = _select_next_question(
                    question_plan=question_plan,
                    transcript=transcript,
                    rubric_breakdown=rubric_breakdown,
                    current_question_payload=question_payload,
                    question_index=next_index,
                    max_questions=resolved_max_questions,
                )
            next_question = _refine_question_payload(next_question, interview_context, transcript)

        return {
            "success": True,
            "model_version": MODEL_VERSION,
            "data": {
                "session_id": session_id,
                "question_index": current_index,
                "max_questions": resolved_max_questions,
                "total_score": total_score,
                "technical_score": technical_score,
                "communication_score": communication_score,
                "jd_fit_score": jd_fit_score,
                "clarity_score": clarity_score,
                "specificity_score": specificity_score,
                "structure_score": structure_score,
                "weakest_dimension": weakest_dimension,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "feedback_text": feedback_text,
                "completed": completed,
                "next_question": next_question,
                "generation_provider": next_question.get("generation_provider") if next_question else "rule_based",
                "role_family": role_family,
            },
            "error": None,
        }
    except Exception as exc:
        logger.exception("Evaluate mock interview answer failed for session_id=%s", session_id)
        return {
            "success": False,
            "model_version": MODEL_VERSION,
            "data": {},
            "error": str(exc),
        }


def generate_mock_interview_report(
    session_id: int,
    *,
    interview_context: dict | None = None,
    transcript: list[dict] | None = None,
) -> dict:
    interview_context = interview_context or {}
    transcript = transcript or []

    try:
        evaluation_items = [item for item in transcript if (item.get("metadata") or {}).get("type") == "interview_feedback"]
        if not evaluation_items:
            return {
                "success": False,
                "model_version": MODEL_VERSION,
                "data": {},
                "error": "Chưa có đủ dữ liệu trả lời để sinh báo cáo phỏng vấn.",
            }

        role_family = _resolve_role_family(interview_context)
        averages = _calculate_report_averages(evaluation_items)
        strengths = _top_list_items(evaluation_items, "strengths")
        weaknesses = _top_list_items(evaluation_items, "weaknesses")
        weakest_dimension = min(averages["rubric_summary"].items(), key=lambda item: item[1])[0]
        weakest_answer = _find_weakest_answer(evaluation_items)
        recommended_focus = _build_recommended_focus(interview_context, weakest_dimension, weaknesses)
        practice_plan = _build_practice_plan(interview_context, weakest_dimension, weaknesses)
        improvement_text = _build_report_improvement_text(
            interview_context=interview_context,
            weakest_dimension=weakest_dimension,
            strengths=strengths,
            weaknesses=weaknesses,
            recommended_focus=recommended_focus,
            practice_plan=practice_plan,
            weakest_answer=weakest_answer,
        )
        report_payload = {
            "diem_manh": strengths,
            "diem_yeu": weaknesses,
            "de_xuat_cai_thien": improvement_text,
            "metadata": {
                "rubric_summary": averages["rubric_summary"],
                "assessment_criteria": _build_assessment_criteria(),
                "role_family": role_family,
                "weakest_dimension": weakest_dimension,
                "weakest_answer_summary": weakest_answer,
                "recommended_focus": recommended_focus,
                "practice_plan": practice_plan,
                "structured_improvement": _build_structured_improvement(
                    weakest_dimension=weakest_dimension,
                    recommended_focus=recommended_focus,
                    practice_plan=practice_plan,
                    weakest_answer=weakest_answer,
                ),
            },
        }
        improvement_text = _refine_report_text(report_payload, interview_context)

        return {
            "success": True,
            "model_version": MODEL_VERSION,
            "data": {
                "session_id": session_id,
                "tong_diem": averages["overall"],
                "diem_ky_thuat": averages["technical_score"],
                "diem_giao_tiep": averages["communication_score"],
                "diem_phu_hop_jd": averages["jd_fit_score"],
                "diem_manh": strengths,
                "diem_yeu": weaknesses,
                "de_xuat_cai_thien": improvement_text,
                "metadata": {
                    "rubric_summary": averages["rubric_summary"],
                    "assessment_criteria": _build_assessment_criteria(),
                    "role_family": role_family,
                    "weakest_dimension": weakest_dimension,
                    "weakest_answer_summary": weakest_answer,
                    "recommended_focus": recommended_focus,
                    "practice_plan": practice_plan,
                    "structured_improvement": _build_structured_improvement(
                        weakest_dimension=weakest_dimension,
                        recommended_focus=recommended_focus,
                        practice_plan=practice_plan,
                        weakest_answer=weakest_answer,
                    ),
                    "generation_provider": _resolve_generation_provider(),
                },
            },
            "error": None,
        }
    except Exception as exc:
        logger.exception("Generate mock interview report failed for session_id=%s", session_id)
        return {
            "success": False,
            "model_version": MODEL_VERSION,
            "data": {},
            "error": str(exc),
        }


def _build_question_plan(interview_context: dict) -> list[dict]:
    candidate = interview_context.get("candidate_profile") or {}
    related_job = interview_context.get("related_job") or {}
    top_matches = interview_context.get("top_matching_jobs") or []
    role_family = _resolve_role_family(interview_context)

    matched_skills = []
    missing_skills = []
    if top_matches:
        matched_skills = (top_matches[0].get("matched_skills") or [])[:4]
        missing_skills = (top_matches[0].get("missing_skills") or [])[:4]

    candidate_skills = (candidate.get("parsed_skills") or [])[:6]
    related_job_skills = (related_job.get("skills") or [])[:6]
    job_title = related_job.get("title") or interview_context.get("career_report", {}).get("nghe_de_xuat") or "vị trí mục tiêu"

    role_defaults = {
        "backend": ("Laravel", "REST API", "Docker", "MySQL"),
        "frontend": ("JavaScript", "Vue.js", "TypeScript", "UI/UX"),
        "mobile": ("Android", "iOS", "Flutter", "Firebase"),
        "data": ("SQL", "Python", "ETL", "Data Visualization"),
        "general": ("backend", "service", "Docker", "MySQL"),
    }
    fallback_primary, fallback_secondary, fallback_gap, fallback_secondary_gap = role_defaults.get(role_family, role_defaults["general"])

    primary_skill = matched_skills[0] if matched_skills else (candidate_skills[0] if candidate_skills else fallback_primary)
    secondary_skill = matched_skills[1] if len(matched_skills) > 1 else fallback_secondary
    gap_skill = missing_skills[0] if missing_skills else fallback_gap
    secondary_gap = missing_skills[1] if len(missing_skills) > 1 else fallback_secondary_gap
    opening_focus = related_job_skills[:3] or matched_skills[:3] or candidate_skills[:2]

    return [
        {
            "question_type": "opening",
            "interview_stage_label": "Mở đầu",
            "focus_skills": opening_focus,
            "suggested_answer_points": [
                "Tóm tắt ngắn gọn kinh nghiệm hiện tại",
                f"Lý do phù hợp với hướng {job_title}",
                "Nhấn mạnh 1-2 dự án hoặc kỹ năng nổi bật",
            ],
            "question_text": f"Bạn hãy giới thiệu ngắn gọn về bản thân và lý do bạn phù hợp với vị trí {job_title}.",
        },
        {
            "question_type": "technical_core",
            "interview_stage_label": "Kỹ thuật cốt lõi",
            "focus_skills": [primary_skill],
            "suggested_answer_points": [
                f"Mô tả cách bạn đã dùng {primary_skill} trong dự án",
                "Nêu vai trò của bạn",
                "Nêu kết quả hoặc bài học rút ra",
            ],
            "question_text": f"Hãy mô tả một tình huống thực tế bạn đã sử dụng {primary_skill} trong dự án gần đây.",
        },
        {
            "question_type": "gap_skill",
            "interview_stage_label": "Khoảng trống kỹ năng",
            "focus_skills": [gap_skill, secondary_gap],
            "suggested_answer_points": [
                f"Thừa nhận mức độ hiện tại với {gap_skill}",
                "Nêu kế hoạch học hoặc thực hành",
                "Giải thích cách bạn có thể bắt kịp nhanh",
            ],
            "question_text": f"Nếu nhà tuyển dụng hỏi về kỹ năng {gap_skill}, bạn sẽ trả lời thế nào khi đây là kỹ năng bạn còn cần bổ sung?",
        },
        {
            "question_type": "problem_solving",
            "interview_stage_label": "Tình huống xử lý",
            "focus_skills": [primary_skill, secondary_skill],
            "suggested_answer_points": [
                "Nêu cách tiếp cận bài toán",
                "Giải thích cách ưu tiên bước xử lý",
                "Nêu cách kiểm tra và đánh giá kết quả",
            ],
            "question_text": f"Nếu được giao xử lý một nhiệm vụ liên quan tới {primary_skill} và cần phối hợp thêm {secondary_skill}, bạn sẽ bắt đầu như thế nào?",
        },
        {
            "question_type": "behavioral",
            "interview_stage_label": "Hành vi và phối hợp",
            "focus_skills": [],
            "suggested_answer_points": [
                "Mô tả một tình huống làm việc nhóm",
                "Nêu khó khăn cụ thể",
                "Nêu cách bạn xử lý và kết quả",
            ],
            "question_text": "Hãy chia sẻ một tình huống bạn gặp khó khăn khi làm việc nhóm hoặc làm việc với yêu cầu thay đổi, và cách bạn xử lý.",
        },
        {
            "question_type": "system_thinking",
            "interview_stage_label": "Tư duy hệ thống",
            "focus_skills": [primary_skill, secondary_gap],
            "suggested_answer_points": [
                "Nêu cách chia nhỏ yêu cầu",
                "Giải thích thiết kế luồng xử lý",
                "Nêu cách kiểm tra hiệu năng và độ ổn định",
            ],
            "question_text": f"Nếu cần mở rộng một tính năng backend đang dùng {primary_skill} và dữ liệu liên quan tới {secondary_gap}, bạn sẽ phân tích và thiết kế theo những bước nào?",
        },
        {
            "question_type": "career_motivation",
            "interview_stage_label": "Động lực và định hướng",
            "focus_skills": candidate_skills[:2],
            "suggested_answer_points": [
                "Nêu mục tiêu phát triển ngắn hạn",
                "Liên hệ với vị trí đang ứng tuyển",
                "Cho thấy tinh thần học hỏi và cam kết cải thiện",
            ],
            "question_text": f"Trong 3 đến 6 tháng tới, bạn muốn phát triển bản thân như thế nào để phù hợp hơn với vị trí {job_title}?",
        },
    ]


def _resolve_max_questions(max_questions: int) -> int:
    return max(MIN_MAX_QUESTIONS, min(int(max_questions or DEFAULT_MAX_QUESTIONS), HARD_MAX_QUESTIONS))


def _resolve_generation_provider() -> str:
    provider = (settings.mock_interview_provider or "rule_based").strip().lower()
    if provider in {"ollama", "rule_based"}:
        return provider
    return "rule_based"


def _refine_question_payload(question_payload: dict, interview_context: dict, transcript: list[dict]) -> dict:
    refined = question_payload.copy()
    provider = _resolve_generation_provider()

    if provider != "ollama":
        refined["question_text"] = _sanitize_interview_question_text(refined.get("question_text") or "")
        refined["generation_provider"] = "rule_based"
        return refined

    try:
        refined_text = ollama_provider.refine_question(refined, interview_context, transcript)
        if refined_text:
            sanitized_text = _sanitize_interview_question_text(refined_text)
            if _is_valid_refined_question(sanitized_text, refined, interview_context):
                refined["question_text"] = sanitized_text
                refined["generation_provider"] = "ollama"
                return refined
            logger.warning(
                "Fallback to rule_based question because refined question is off-topic: %s",
                sanitized_text,
            )
    except Exception as exc:
        logger.warning("Fallback to rule_based question generation: %s", exc)

    refined["question_text"] = _sanitize_interview_question_text(refined.get("question_text") or "")
    refined["generation_provider"] = "rule_based"
    return refined


def _refine_report_text(report_payload: dict, interview_context: dict) -> str:
    provider = _resolve_generation_provider()
    if provider != "ollama":
        return report_payload.get("de_xuat_cai_thien") or ""

    try:
        refined_text = ollama_provider.refine_report(report_payload, interview_context)
        if refined_text:
            return refined_text
    except Exception as exc:
        logger.warning("Fallback to rule_based report generation: %s", exc)

    return report_payload.get("de_xuat_cai_thien") or ""


def _resolve_initial_question_payload(question_plan: list[dict], question_index: int, max_questions: int) -> dict:
    bounded_index = max(1, min(question_index, min(len(question_plan), max_questions)))
    return _materialize_question_payload(
        question_plan[bounded_index - 1],
        question_index=bounded_index,
        max_questions=max_questions,
        selection_strategy="initial_plan",
    )


def _materialize_question_payload(template: dict, *, question_index: int, max_questions: int, selection_strategy: str) -> dict:
    payload = template.copy()
    payload["question_index"] = question_index
    payload["max_questions"] = max_questions
    payload["selection_strategy"] = selection_strategy
    return payload


def _score_technical_answer(normalized_answer: str, focus_skills: list[str], interview_context: dict, question_type: str, role_family: str) -> float:
    score = 28.0
    answer_length = len(normalized_answer.split())

    if answer_length >= 18:
        score += 8
    if answer_length >= 35:
        score += 8

    normalized_focus = [normalize_search_text(skill) for skill in focus_skills if skill]
    hits = sum(1 for skill in normalized_focus if skill and skill in normalized_answer)
    score += min(hits * 14, 32)

    role_terms = {
        "backend": ["api", "backend", "database", "laravel", "mysql", "docker", "git", "query", "service", "deploy"],
        "frontend": ["frontend", "component", "state", "vue", "react", "javascript", "typescript", "css", "ui"],
        "mobile": ["mobile", "android", "ios", "flutter", "firebase", "app", "ui", "deploy"],
        "data": ["sql", "python", "etl", "dashboard", "data", "pipeline", "report", "analysis"],
        "general": ["api", "backend", "database", "git", "service", "deploy"],
    }
    technical_terms = role_terms.get(role_family, role_terms["general"])
    score += min(sum(1 for token in technical_terms if token in normalized_answer) * 3, 18)

    if question_type in {"technical_core", "problem_solving", "system_thinking"} and any(
        word in normalized_answer for word in ["du an", "dự án", "xu ly", "xử lý", "thiet ke", "thiết kế"]
    ):
        score += 10

    return min(round(score, 2), 100.0)


def _score_communication_answer(answer: str) -> float:
    score = 35.0
    answer_length = len(answer.split())

    if answer_length >= 20:
        score += 10
    if answer_length >= 40:
        score += 10
    if any(token in answer for token in [".", ":", ";"]):
        score += 8
    if any(word in normalize_search_text(answer) for word in ["vi", "vì", "nen", "nên", "ket qua", "kết quả", "sau do", "sau đó"]):
        score += 12

    return min(round(score, 2), 100.0)


def _score_jd_fit(normalized_answer: str, interview_context: dict, focus_skills: list[str]) -> float:
    score = 30.0
    related_job = interview_context.get("related_job") or {}
    job_skills = [normalize_search_text(skill) for skill in (related_job.get("skills") or []) if skill]
    normalized_focus = [normalize_search_text(skill) for skill in focus_skills if skill]

    overlap = sum(1 for skill in job_skills[:6] if skill and skill in normalized_answer)
    score += min(overlap * 10, 30)

    focus_overlap = sum(1 for skill in normalized_focus if skill and skill in normalized_answer)
    score += min(focus_overlap * 12, 24)

    if any(word in normalized_answer for word in ["phu hop", "phù hợp", "bat kip", "bắt kịp", "hoc nhanh", "học nhanh"]):
        score += 8

    return min(round(score, 2), 100.0)


def _score_clarity(answer: str) -> float:
    normalized_answer = normalize_search_text(answer)
    score = 34.0

    if any(word in normalized_answer for word in ["truoc tien", "đầu tiên", "sau do", "sau đó", "cuoi cung", "cuối cùng"]):
        score += 20
    if any(word in normalized_answer for word in ["vi", "vì", "boi vi", "bởi vì", "ly do", "lý do"]):
        score += 16
    if any(token in answer for token in [".", ":", ";", "-"]):
        score += 10

    return min(round(score, 2), 100.0)


def _score_specificity(answer: str, normalized_answer: str, focus_skills: list[str]) -> float:
    score = 28.0

    if any(word in normalized_answer for word in ["du an", "dự án", "module", "api", "endpoint", "query", "service"]):
        score += 20
    if any(char.isdigit() for char in answer):
        score += 10
    if any(word in normalized_answer for word in ["ket qua", "kết quả", "toi uu", "tối ưu", "giam", "giảm", "tang", "tăng"]):
        score += 18
    if any(skill and normalize_search_text(skill) in normalized_answer for skill in focus_skills):
        score += 14

    return min(round(score, 2), 100.0)


def _score_structure(answer: str) -> float:
    normalized_answer = normalize_search_text(answer)
    score = 30.0

    if any(token in answer for token in ["1.", "2.", "3.", "- "]):
        score += 20
    if any(word in normalized_answer for word in ["boi canh", "bối cảnh", "hanh dong", "hành động", "ket qua", "kết quả"]):
        score += 18
    if len(answer.split()) >= 25:
        score += 12

    return min(round(score, 2), 100.0)


def _detect_strengths(answer: str, normalized_answer: str, focus_skills: list[str], rubric_breakdown: dict[str, float]) -> list[str]:
    strengths: list[str] = []

    if rubric_breakdown["technical_score"] >= 68:
        strengths.append("Bám khá sát phần kỹ thuật mà câu hỏi đang hướng tới")
    if rubric_breakdown["specificity_score"] >= 65:
        strengths.append("Có ví dụ hoặc chi tiết cụ thể, giúp câu trả lời thuyết phục hơn")
    if rubric_breakdown["structure_score"] >= 65:
        strengths.append("Câu trả lời có cấu trúc tương đối rõ ràng")
    if rubric_breakdown["communication_score"] >= 65:
        strengths.append("Diễn đạt dễ hiểu và có mạch")
    if any(skill and normalize_search_text(skill) in normalized_answer for skill in focus_skills):
        strengths.append("Nhắc đúng kỹ năng trọng tâm của câu hỏi")
    if any(word in normalized_answer for word in ["du an", "dự án", "kinh nghiem", "kinh nghiệm"]):
        strengths.append("Biết liên hệ với kinh nghiệm hoặc dự án thực tế")

    return strengths[:4] or ["Có cố gắng trả lời đúng phạm vi của câu hỏi"]


def _detect_weaknesses(answer: str, normalized_answer: str, focus_skills: list[str], rubric_breakdown: dict[str, float]) -> list[str]:
    weaknesses: list[str] = []

    if len(answer.split()) < 18:
        weaknesses.append("Câu trả lời còn ngắn, chưa đủ chiều sâu")
    if rubric_breakdown["clarity_score"] < 55:
        weaknesses.append("Ý chính chưa thật sự rõ, người phỏng vấn khó theo dõi")
    if rubric_breakdown["specificity_score"] < 55:
        weaknesses.append("Thiếu ví dụ thực tế hoặc chi tiết cụ thể")
    if rubric_breakdown["structure_score"] < 55:
        weaknesses.append("Cách trình bày chưa có cấu trúc rõ ràng")
    if focus_skills and not any(skill and normalize_search_text(skill) in normalized_answer for skill in focus_skills):
        weaknesses.append("Chưa nhắc rõ kỹ năng trọng tâm mà câu hỏi đang hỏi tới")

    return weaknesses[:4] or ["Nên tăng thêm ví dụ thực tế để câu trả lời thuyết phục hơn"]


def _build_feedback_text(
    *,
    question_payload: dict,
    total_score: float,
    rubric_breakdown: dict[str, float],
    strengths: list[str],
    weaknesses: list[str],
) -> str:
    lines = [
        f"Đánh giá câu {question_payload.get('question_index', '?')}:",
        f"- Tổng điểm tạm thời: {total_score:.2f}/100",
        f"- Kỹ thuật: {rubric_breakdown['technical_score']:.2f}/100",
        f"- Giao tiếp: {rubric_breakdown['communication_score']:.2f}/100",
        f"- Phù hợp JD: {rubric_breakdown['jd_fit_score']:.2f}/100",
        f"- Rõ ý: {rubric_breakdown['clarity_score']:.2f}/100",
        f"- Cụ thể: {rubric_breakdown['specificity_score']:.2f}/100",
        f"- Cấu trúc: {rubric_breakdown['structure_score']:.2f}/100",
        "",
        "Điểm mạnh:",
        *[f"- {item}" for item in strengths[:3]],
        "",
        "Điểm cần cải thiện:",
        *[f"- {item}" for item in weaknesses[:3]],
    ]
    return "\n".join(lines)


def _extract_evaluation_history(transcript: list[dict]) -> list[dict]:
    history: list[dict] = []
    for item in transcript:
        metadata = item.get("metadata") or {}
        if metadata.get("type") == "interview_feedback":
            history.append(metadata)
    return history


def _should_follow_up(
    question_payload: dict,
    answer: str,
    rubric_breakdown: dict[str, float],
    evaluation_history: list[dict],
) -> bool:
    if question_payload.get("question_type") == "follow_up":
        return False

    recent_follow_up = any((item.get("next_question") or {}).get("question_type") == "follow_up" for item in evaluation_history[-1:])
    if recent_follow_up:
        return False

    if len(answer.split()) < 14:
        return True

    weak_dimensions = sum(
        1
        for key in ("technical_score", "clarity_score", "specificity_score", "structure_score")
        if rubric_breakdown[key] < 52
    )
    return weak_dimensions >= 2


def _build_follow_up_question(
    *,
    question_payload: dict,
    interview_context: dict,
    weaknesses: list[str],
    weakest_dimension: str,
    question_index: int,
    max_questions: int,
) -> dict:
    focus_skills = question_payload.get("focus_skills") or []
    primary_focus = focus_skills[0] if focus_skills else "kỹ năng đang được hỏi"
    weakness_hint = weaknesses[0] if weaknesses else "trả lời còn chung chung"

    if weakest_dimension == "specificity_score":
        question_text = f"Bạn có thể nêu một ví dụ cụ thể hơn về việc bạn đã dùng {primary_focus} trong dự án thật, gồm bối cảnh, việc bạn làm và kết quả không?"
    elif weakest_dimension == "structure_score":
        question_text = f"Hãy trả lời lại ngắn gọn về {primary_focus} theo 3 ý: bối cảnh, hành động của bạn và kết quả đạt được."
    elif weakest_dimension == "clarity_score":
        question_text = f"Nếu giải thích lại cho người phỏng vấn, bạn sẽ trình bày rõ hơn về {primary_focus} như thế nào để họ dễ hiểu ngay?"
    else:
        question_text = f"Bạn có thể đào sâu hơn vào cách bạn dùng {primary_focus} hoặc cách bạn sẽ bù khoảng trống kỹ năng này trong công việc thực tế không?"

    return _materialize_question_payload(
        {
            "question_type": "follow_up",
            "interview_stage_label": "Đào sâu",
            "focus_skills": focus_skills,
            "suggested_answer_points": [
                "Đưa ví dụ cụ thể hơn",
                "Nêu rõ việc bạn đã làm",
                "Nêu kết quả hoặc bài học rút ra",
                weakness_hint,
            ],
            "question_text": question_text,
        },
        question_index=question_index,
        max_questions=max_questions,
        selection_strategy="follow_up",
    )


def _select_next_question(
    *,
    question_plan: list[dict],
    transcript: list[dict],
    rubric_breakdown: dict[str, float],
    current_question_payload: dict,
    question_index: int,
    max_questions: int,
) -> dict:
    asked_types = [
        (item.get("metadata") or {}).get("question_type")
        for item in transcript
        if (item.get("metadata") or {}).get("type") == "interview_question"
    ]
    current_type = current_question_payload.get("question_type")

    if rubric_breakdown["technical_score"] < 58:
        candidate = _find_unasked_question(question_plan, asked_types, ["problem_solving", "system_thinking", "technical_core"], exclude=current_type)
        if candidate:
            return _materialize_question_payload(candidate, question_index=question_index, max_questions=max_questions, selection_strategy="adaptive_technical")

    if rubric_breakdown["jd_fit_score"] < 58:
        candidate = _find_unasked_question(question_plan, asked_types, ["gap_skill", "career_motivation"], exclude=current_type)
        if candidate:
            return _materialize_question_payload(candidate, question_index=question_index, max_questions=max_questions, selection_strategy="adaptive_jd_fit")

    if rubric_breakdown["communication_score"] < 58 or rubric_breakdown["clarity_score"] < 58:
        candidate = _find_unasked_question(question_plan, asked_types, ["behavioral", "career_motivation"], exclude=current_type)
        if candidate:
            return _materialize_question_payload(candidate, question_index=question_index, max_questions=max_questions, selection_strategy="adaptive_communication")

    candidate = _find_unasked_question(question_plan, asked_types, [item["question_type"] for item in question_plan], exclude=None)
    if not candidate:
        candidate = question_plan[min(question_index - 1, len(question_plan) - 1)]

    return _materialize_question_payload(candidate, question_index=question_index, max_questions=max_questions, selection_strategy="plan_progression")


def _find_unasked_question(question_plan: list[dict], asked_types: list[str | None], preferred_types: list[str], exclude: str | None) -> dict | None:
    for question_type in preferred_types:
        if question_type == exclude:
            continue
        if question_type in asked_types:
            continue
        for item in question_plan:
            if item["question_type"] == question_type:
                return item
    return None


def _calculate_report_averages(evaluation_items: list[dict]) -> dict:
    def _avg(key: str) -> float:
        values = [float((item.get("metadata") or {}).get(key) or 0) for item in evaluation_items]
        return round(sum(values) / len(values), 2)

    technical_score = _avg("technical_score")
    communication_score = _avg("communication_score")
    jd_fit_score = _avg("jd_fit_score")
    clarity_score = _avg("clarity_score")
    specificity_score = _avg("specificity_score")
    structure_score = _avg("structure_score")
    overall = round(
        technical_score * 0.28
        + communication_score * 0.18
        + jd_fit_score * 0.18
        + clarity_score * 0.14
        + specificity_score * 0.12
        + structure_score * 0.10,
        2,
    )

    return {
        "overall": overall,
        "technical_score": technical_score,
        "communication_score": communication_score,
        "jd_fit_score": jd_fit_score,
        "rubric_summary": {
            "technical_score": technical_score,
            "communication_score": communication_score,
            "jd_fit_score": jd_fit_score,
            "clarity_score": clarity_score,
            "specificity_score": specificity_score,
            "structure_score": structure_score,
        },
    }


def _find_weakest_answer(evaluation_items: list[dict]) -> dict:
    weakest = min(
        evaluation_items,
        key=lambda item: float((item.get("metadata") or {}).get("total_score") or 0),
    )
    metadata = weakest.get("metadata") or {}
    return {
        "question_index": metadata.get("question_index"),
        "total_score": metadata.get("total_score"),
        "main_issue": (metadata.get("weaknesses") or [None])[0],
    }


def _build_recommended_focus(interview_context: dict, weakest_dimension: str, weaknesses: list[str]) -> list[str]:
    report = interview_context.get("career_report") or {}
    role_family = _resolve_role_family(interview_context)
    suggested_skills = ((report.get("goi_y_ky_nang_bo_sung") or {}).get("skills") or [])[:3]
    mapping = {
        "technical_score": "Củng cố ví dụ kỹ thuật và cách giải quyết vấn đề",
        "communication_score": "Luyện diễn đạt ngắn gọn, rõ ý và tự tin hơn",
        "jd_fit_score": "Liên hệ chặt hơn giữa kinh nghiệm của bạn và yêu cầu JD",
        "clarity_score": "Trình bày theo ý rõ ràng, tránh trả lời dàn trải",
        "specificity_score": "Bổ sung ví dụ cụ thể, dữ liệu và kết quả rõ ràng",
        "structure_score": "Luyện khung trả lời có cấu trúc như bối cảnh - hành động - kết quả",
    }

    focus = [mapping.get(weakest_dimension, "Tăng chất lượng trả lời phỏng vấn")]
    role_focus = {
        "backend": "Liên hệ rõ hơn tới tình huống backend thực tế như API, database, service.",
        "frontend": "Liên hệ rõ hơn tới component, state management và trải nghiệm người dùng.",
        "mobile": "Liên hệ rõ hơn tới ứng dụng di động, hiệu năng và trải nghiệm trên thiết bị.",
        "data": "Liên hệ rõ hơn tới dữ liệu, truy vấn, pipeline và báo cáo phân tích.",
    }
    if role_family in role_focus:
        focus.append(role_focus[role_family])
    focus.extend(f"Ưu tiên bồi dưỡng thêm kỹ năng: {skill}" for skill in suggested_skills)
    focus.extend(weaknesses[:2])
    return focus[:4]


def _build_practice_plan(interview_context: dict, weakest_dimension: str, weaknesses: list[str]) -> list[str]:
    related_job = interview_context.get("related_job") or {}
    role_family = _resolve_role_family(interview_context)
    top_skill = ((related_job.get("skills") or [])[:1] or ["stack mục tiêu"])[0]

    plan = [
        "Chuẩn bị sẵn 2 đến 3 ví dụ dự án thật liên quan trực tiếp tới vị trí đang ứng tuyển.",
        f"Luyện trả lời về {top_skill} theo khung: bối cảnh, việc bạn làm, kết quả đạt được.",
        "Tự ghi âm hoặc tự nói thử trong 2 đến 3 phút để cải thiện sự rõ ràng và mạch trả lời.",
    ]

    if weakest_dimension in {"specificity_score", "technical_score"}:
        plan.insert(1, "Bổ sung số liệu, kết quả, hoặc thay đổi cụ thể để câu trả lời bớt chung chung.")
    if weakest_dimension in {"clarity_score", "structure_score", "communication_score"}:
        plan.insert(1, "Luyện tách câu trả lời thành 3 ý rõ ràng thay vì nói thành một đoạn dài.")
    if weaknesses:
        plan.append(f"Tập trung sửa trước điểm yếu nổi bật: {weaknesses[0]}.")

    role_plan = {
        "backend": "Ôn lại cách giải thích API, database và logic nghiệp vụ bằng ví dụ thật.",
        "frontend": "Chuẩn bị ví dụ về component, state và cách tối ưu trải nghiệm người dùng.",
        "mobile": "Chuẩn bị ví dụ về luồng ứng dụng, xử lý thiết bị và tối ưu trải nghiệm mobile.",
        "data": "Chuẩn bị ví dụ về truy vấn, xử lý dữ liệu và cách rút insight từ dữ liệu.",
    }
    if role_family in role_plan:
        plan.append(role_plan[role_family])

    return plan[:5]


def _top_list_items(evaluation_items: list[dict], key: str) -> list[str]:
    counter: Counter[str] = Counter()
    for item in evaluation_items:
        values = (item.get("metadata") or {}).get(key) or []
        for value in values:
            if isinstance(value, str) and value.strip():
                counter[value.strip()] += 1
    return [value for value, _count in counter.most_common(5)]


def _build_report_improvement_text(
    *,
    interview_context: dict,
    weakest_dimension: str,
    strengths: list[str],
    weaknesses: list[str],
    recommended_focus: list[str],
    practice_plan: list[str],
    weakest_answer: dict,
) -> str:
    related_job = interview_context.get("related_job") or {}
    job_title = related_job.get("title") or "vị trí mục tiêu"
    dimension_labels = {
        "technical_score": "chiều sâu kỹ thuật",
        "communication_score": "khả năng giao tiếp",
        "jd_fit_score": "mức độ liên hệ với JD",
        "clarity_score": "độ rõ ràng",
        "specificity_score": "mức độ cụ thể",
        "structure_score": "cấu trúc trả lời",
    }

    lines = [
        f"Tóm tắt ngắn:",
        f"- Với vị trí {job_title}, điểm cần ưu tiên cải thiện nhất hiện tại là {dimension_labels.get(weakest_dimension, weakest_dimension)}.",
    ]

    if weakest_answer.get("question_index"):
        lines.append(
            f"- Câu trả lời cần cải thiện nhất nằm ở câu số {weakest_answer['question_index']} với vấn đề chính: "
            f"{weakest_answer.get('main_issue') or 'chưa đủ thuyết phục'}."
        )

    if recommended_focus:
        lines.append("")
        lines.append("Ưu tiên cải thiện:")
        lines.extend(f"- {item}" for item in recommended_focus)

    if practice_plan:
        lines.append("")
        lines.append("Kế hoạch luyện tiếp:")
        lines.extend(f"- {item}" for item in practice_plan)

    if strengths:
        lines.append("")
        lines.append("Điểm mạnh nên tiếp tục phát huy:")
        lines.extend(f"- {item}" for item in strengths[:3])

    if weaknesses:
        lines.append("")
        lines.append("Các điểm yếu còn cần theo dõi:")
        lines.extend(f"- {item}" for item in weaknesses[:3])

    return "\n".join(lines)


def _build_assessment_criteria() -> list[dict]:
    return [
        {
            "key": "technical_score",
            "label": "Kỹ thuật",
            "description": "Mức độ đúng chuyên môn, dùng đúng kỹ năng trọng tâm, có chiều sâu kỹ thuật và cách xử lý vấn đề.",
        },
        {
            "key": "communication_score",
            "label": "Giao tiếp",
            "description": "Cách diễn đạt có tự tin, mạch lạc, dễ nghe và phù hợp ngữ cảnh phỏng vấn hay không.",
        },
        {
            "key": "jd_fit_score",
            "label": "Phù hợp JD",
            "description": "Mức độ liên hệ giữa câu trả lời với yêu cầu công việc và vị trí đang ứng tuyển.",
        },
        {
            "key": "clarity_score",
            "label": "Rõ ý",
            "description": "Câu trả lời có đi thẳng vào trọng tâm, tránh mơ hồ và giúp người phỏng vấn hiểu nhanh hay không.",
        },
        {
            "key": "specificity_score",
            "label": "Cụ thể",
            "description": "Có ví dụ, bối cảnh, hành động và kết quả rõ ràng thay vì nói chung chung hay không.",
        },
        {
            "key": "structure_score",
            "label": "Cấu trúc",
            "description": "Câu trả lời có bố cục tốt, ví dụ theo khung bối cảnh - hành động - kết quả, thay vì nói liền một đoạn hay không.",
        },
    ]


def _build_structured_improvement(
    *,
    weakest_dimension: str,
    recommended_focus: list[str],
    practice_plan: list[str],
    weakest_answer: dict,
) -> dict:
    dimension_labels = {
        "technical_score": "chiều sâu kỹ thuật",
        "communication_score": "khả năng giao tiếp",
        "jd_fit_score": "mức độ liên hệ với JD",
        "clarity_score": "độ rõ ràng",
        "specificity_score": "mức độ cụ thể",
        "structure_score": "cấu trúc trả lời",
    }

    summary_lines = [
        f"Điểm cần ưu tiên cải thiện nhất là {dimension_labels.get(weakest_dimension, weakest_dimension)}.",
    ]
    if weakest_answer.get("question_index"):
        summary_lines.append(
            f"Câu trả lời cần cải thiện nhất là câu {weakest_answer['question_index']}, vì {weakest_answer.get('main_issue') or 'chưa đủ thuyết phục'}."
        )

    return {
        "summary": summary_lines,
        "priority_actions": recommended_focus[:4],
        "practice_plan": practice_plan[:5],
    }


def _sanitize_interview_question_text(text: str) -> str:
    cleaned = (text or "").replace("**", "").replace("__", "").replace("`", "").replace("#", "").strip()
    if not cleaned:
        return ""

    cleaned = re.sub(r"^(câu hỏi|question)\s*:\s*", "", cleaned, flags=re.IGNORECASE).strip()

    answer_markers = [
        r"^\s*(gợi ý trả lời|goi y tra loi|trả lời mẫu|tra loi mau|mẫu trả lời|mau tra loi)\s*[:\-]",
        r"^\s*(ví dụ trả lời|vi du tra loi|đáp án|dap an|answer)\s*[:\-]",
        r"^\s*(tiêu chí chấm|tieu chi cham|rubric|đánh giá|danh gia)\s*[:\-]",
        r"^\s*(outline trả lời|hướng dẫn trả lời|huong dan tra loi)\s*[:\-]",
    ]

    question_lines: list[str] = []
    for raw_line in cleaned.splitlines():
        line = " ".join(raw_line.split()).strip()
        if not line:
            continue
        if any(re.match(pattern, line, flags=re.IGNORECASE) for pattern in answer_markers):
            break
        if question_lines and line.startswith("-"):
            break
        question_lines.append(line)

    candidate = " ".join(question_lines).strip() or cleaned

    if "?" in candidate:
        candidate = candidate[: candidate.find("?") + 1].strip()
    else:
        lowered = candidate.lower()
        plain_markers = [
            "gợi ý trả lời",
            "goi y tra loi",
            "trả lời mẫu",
            "tra loi mau",
            "mẫu trả lời",
            "mau tra loi",
            "ví dụ trả lời",
            "vi du tra loi",
            "đáp án",
            "dap an",
            "answer:",
        ]
        positions = [lowered.find(marker) for marker in plain_markers if lowered.find(marker) != -1]
        if positions:
            candidate = candidate[: min(positions)].strip(" .:-")

    candidate = re.sub(r"\s+", " ", candidate).strip(" .")
    if not candidate:
        return ""
    if candidate.endswith("?"):
        return candidate

    question_prefixes = ("hãy", "bạn", "nếu", "trong", "khi", "vì sao", "mô tả", "chia sẻ")
    if candidate.lower().startswith(question_prefixes):
        return f"{candidate}?"
    return candidate


def _is_valid_refined_question(text: str, question_payload: dict, interview_context: dict) -> bool:
    if not text:
        return False

    question_type = (question_payload.get("question_type") or "general").strip().lower()
    related_job_skills = [
        str(skill).strip()
        for skill in (interview_context.get("related_job") or {}).get("skills", [])
        if str(skill).strip()
    ]
    focus_skills = [
        str(skill).strip()
        for skill in (question_payload.get("focus_skills") or [])
        if str(skill).strip()
    ]

    allowed_for_question = focus_skills + related_job_skills
    if question_type in {"opening", "career_motivation", "behavioral"}:
        allowed_for_question = related_job_skills or focus_skills

    if not allowed_for_question:
        return True

    extracted = extract_skills_from_text(text)
    mentioned_skills = [item["skill_name"] for item in extracted if item.get("skill_name")]
    if not mentioned_skills:
        return True

    normalized_allowed = {normalize_search_text(skill) for skill in allowed_for_question}
    unexpected = [
        skill for skill in mentioned_skills
        if normalize_search_text(skill) not in normalized_allowed
    ]

    if not unexpected:
        return True

    # Cho phép một ít dư địa ở câu kỹ thuật sâu, nhưng khóa cứng ở câu mở đầu / động lực / hành vi.
    if question_type in {"opening", "career_motivation", "behavioral"}:
        return False

    return len(unexpected) == 0


def _resolve_role_family(interview_context: dict) -> str:
    related_job = interview_context.get("related_job") or {}
    job_title = normalize_search_text(str(related_job.get("title") or ""))
    skills = [normalize_search_text(str(skill)) for skill in (related_job.get("skills") or []) if skill]
    corpus = " ".join([job_title, *skills])

    families = {
        "backend": ["backend", "api", "laravel", "php", "spring", "node", "mysql", "postgres", "rest"],
        "frontend": ["frontend", "react", "vue", "javascript", "typescript", "css", "html", "ui"],
        "mobile": ["mobile", "android", "ios", "flutter", "react native", "swift", "kotlin", "firebase"],
        "data": ["data", "analyst", "analytics", "bi", "etl", "sql", "python", "warehouse", "pipeline"],
    }

    best_family = "general"
    best_score = 0
    for family, keywords in families.items():
        score = sum(1 for keyword in keywords if keyword in corpus)
        if score > best_score:
            best_family = family
            best_score = score

    return best_family
