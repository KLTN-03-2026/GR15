from __future__ import annotations

import unittest

from app.services.chatbot_intent_engine import (
    INTENT_CAREER_DIRECTION,
    INTENT_COVER_LETTER,
    INTENT_INTERVIEW_PREP,
    INTENT_JOB_RECOMMENDATION,
    INTENT_LEARNING_PLAN,
    INTENT_MATCHING_EXPLANATION,
    INTENT_NEXT_STEP_ACTION,
    INTENT_OUT_OF_SCOPE,
    INTENT_SKILL_GAP,
    build_template_answer,
    resolve_intent,
)


def sample_context() -> dict:
    return {
        "candidate_profile": {
            "ho_ten": "Nguyen Van A",
            "tieu_de_ho_so": "CV Backend Laravel",
            "kinh_nghiem_nam": 1,
            "trinh_do": "Dai hoc",
            "parsed_skills": ["Laravel", "Git", "REST API", "PHP"],
        },
        "career_report": {
            "nghe_de_xuat": "Backend Developer Laravel",
            "muc_do_phu_hop": 39.26,
            "goi_y_ky_nang_bo_sung": {
                "skills": ["Docker", "MySQL", "Thiết kế hệ thống"],
                "strength_categories": ["backend_development", "database"],
                "recommended_roles": ["Backend Developer Laravel", "PHP Developer", "API Developer"],
            },
        },
        "top_matching_jobs": [
            {
                "job_title": "Backend Developer Laravel",
                "score": 39.26,
                "matched_skills": ["Git", "Laravel", "REST API"],
                "missing_skills": ["Docker", "MySQL"],
                "explanation": "Hồ sơ có nền tảng backend nhưng vẫn thiếu một số kỹ năng quan trọng để tăng độ phù hợp.",
            }
        ],
        "related_job": {
            "title": "Backend Developer Laravel",
            "level": "Junior",
            "skills": ["Laravel", "MySQL", "REST API"],
        },
        "semantic_jobs": [
            {"title": "Backend Developer Laravel", "company_name": "Cong ty AI Test"},
            {"title": "PHP Developer", "company_name": "Cong ty Demo"},
        ],
        "conversation_summary": (
            "Chủ đề gần nhất: định hướng nghề nghiệp. "
            "Hướng nghề đang ưu tiên: Backend Developer Laravel. "
            "Kỹ năng nền hiện có: Laravel, Git, REST API, PHP. "
            "Kỹ năng còn thiếu nổi bật: Docker, MySQL."
        ),
    }


class ChatbotRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = sample_context()

    def test_job_question_maps_to_job_recommendation(self) -> None:
        intent = resolve_intent(
            "Trong hệ thống hiện có job nào gần nhất với hồ sơ của tôi?",
            history=[],
            context=self.context,
        )
        self.assertEqual(intent, INTENT_JOB_RECOMMENDATION)

    def test_apply_now_question_maps_to_job_recommendation(self) -> None:
        intent = resolve_intent(
            "Có job nào trong hệ thống phù hợp để tôi apply ngay không?",
            history=[],
            context=self.context,
        )
        self.assertEqual(intent, INTENT_JOB_RECOMMENDATION)

    def test_next_step_question_does_not_map_to_job(self) -> None:
        intent = resolve_intent(
            "Nếu muốn tăng cơ hội ứng tuyển nhanh nhất, tôi nên làm gì trước trong tuần này?",
            history=[],
            context=self.context,
        )
        self.assertEqual(intent, INTENT_NEXT_STEP_ACTION)

    def test_skill_gap_question_maps_correctly(self) -> None:
        intent = resolve_intent(
            "Tôi đang thiếu những kỹ năng nào để phù hợp hơn với vị trí backend này?",
            history=[],
            context=self.context,
        )
        self.assertEqual(intent, INTENT_SKILL_GAP)

    def test_matching_question_maps_correctly(self) -> None:
        intent = resolve_intent(
            "Vì sao hồ sơ của tôi chưa phù hợp hoàn toàn với job này?",
            history=[],
            context=self.context,
        )
        self.assertEqual(intent, INTENT_MATCHING_EXPLANATION)

    def test_interview_question_maps_correctly(self) -> None:
        intent = resolve_intent(
            "Nhấn mạnh điểm mạnh nào trong phỏng vấn?",
            history=[],
            context=self.context,
        )
        self.assertEqual(intent, INTENT_INTERVIEW_PREP)

    def test_cover_letter_question_maps_correctly(self) -> None:
        intent = resolve_intent(
            "Tôi nên nhấn mạnh điểm gì trong thư xin việc cho job này?",
            history=[],
            context=self.context,
        )
        self.assertEqual(intent, INTENT_COVER_LETTER)

    def test_career_direction_question_maps_correctly(self) -> None:
        intent = resolve_intent(
            "Từ hồ sơ hiện tại, tôi nên theo Backend Developer hay hướng khác?",
            history=[],
            context=self.context,
        )
        self.assertEqual(intent, INTENT_CAREER_DIRECTION)

    def test_learning_plan_question_maps_correctly(self) -> None:
        intent = resolve_intent(
            "Hãy đề xuất cho tôi hướng chính, hướng thay thế và kế hoạch học theo từng giai đoạn.",
            history=[],
            context=self.context,
        )
        self.assertEqual(intent, INTENT_LEARNING_PLAN)

    def test_follow_up_question_uses_previous_intent(self) -> None:
        history = [
            {"role": "user", "content": "Từ hồ sơ hiện tại, tôi nên theo Backend Developer hay hướng khác?", "intent": INTENT_CAREER_DIRECTION},
            {"role": "assistant", "content": "Bạn nên ưu tiên theo hướng Backend Developer Laravel.", "intent": INTENT_CAREER_DIRECTION},
        ]
        intent = resolve_intent(
            "Vậy còn hướng thay thế thì sao?",
            history=history,
            context=self.context,
        )
        self.assertEqual(intent, INTENT_CAREER_DIRECTION)

    def test_out_of_scope_question_maps_correctly(self) -> None:
        intent = resolve_intent(
            "Thời tiết hôm nay thế nào?",
            history=[],
            context={},
        )
        self.assertEqual(intent, INTENT_OUT_OF_SCOPE)

    def test_job_template_answer_has_job_list_not_plan(self) -> None:
        answer = build_template_answer(
            "Trong hệ thống hiện có job nào gần nhất với hồ sơ của tôi?",
            self.context,
            [],
            INTENT_JOB_RECOMMENDATION,
        )
        self.assertIn("Gợi ý công việc nên xem:", answer)
        self.assertIn("- Backend Developer Laravel", answer)
        self.assertNotIn("Giai đoạn 1", answer)

    def test_next_step_answer_is_actionable(self) -> None:
        answer = build_template_answer(
            "Nếu muốn tăng cơ hội ứng tuyển nhanh nhất, tôi nên làm gì trước trong tuần này?",
            self.context,
            [],
            INTENT_NEXT_STEP_ACTION,
        )
        self.assertIn("Việc nên làm trước trong tuần này:", answer)
        self.assertIn("Bước tiếp theo:", answer)
        self.assertNotIn("Gợi ý công việc nên xem:", answer)

    def test_interview_answer_mentions_strengths(self) -> None:
        answer = build_template_answer(
            "Nhấn mạnh điểm mạnh nào trong phỏng vấn?",
            self.context,
            [],
            INTENT_INTERVIEW_PREP,
        )
        self.assertIn("Những điểm mạnh nên nhấn mạnh khi phỏng vấn:", answer)
        self.assertIn("- Laravel", answer)

    def test_learning_plan_answer_has_stages(self) -> None:
        answer = build_template_answer(
            "Hãy lập cho tôi lộ trình 3 tháng để tăng cơ hội ứng tuyển.",
            self.context,
            [],
            INTENT_LEARNING_PLAN,
        )
        self.assertIn("Giai đoạn 1:", answer)
        self.assertIn("Giai đoạn 2:", answer)
        self.assertIn("Giai đoạn 3:", answer)


if __name__ == "__main__":
    unittest.main()
