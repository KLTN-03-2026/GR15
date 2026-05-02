from __future__ import annotations

import unittest
from unittest.mock import patch

from app.services.chatbot import generate_career_chat_reply
from app.providers.chat_template_provider import TemplateChatProvider
from app.services.chatbot_intent_engine import (
    INTENT_LEARNING_PLAN,
    build_template_answer,
    resolve_intent,
)


def simulator_context() -> dict:
    return {
        "candidate_profile": {
            "ho_ten": "Mai",
            "tieu_de_ho_so": "Backend Developer",
            "vi_tri_ung_tuyen_muc_tieu": "Backend Developer Laravel",
            "ten_nganh_nghe_muc_tieu": "Công nghệ thông tin",
            "kinh_nghiem_nam": 1,
            "trinh_do": "Đại học",
            "parsed_skills": ["Laravel", "PHP", "REST API"],
            "builder_skills": ["Git", "MySQL"],
        },
        "career_report": {
            "nghe_de_xuat": "Backend Developer Laravel",
            "muc_do_phu_hop": 52.5,
            "goi_y_ky_nang_bo_sung": {
                "skills": ["Docker", "Redis", "Thiết kế hệ thống"],
                "recommended_roles": ["PHP Developer", "API Developer"],
            },
        },
        "top_matching_jobs": [
            {
                "job_title": "Backend Developer Laravel",
                "score": 52.5,
                "matched_skills": ["Laravel", "REST API"],
                "missing_skills": ["Docker", "Redis"],
            }
        ],
        "semantic_jobs": [
            {"title": "Backend Developer Laravel", "company_name": "TechViet"},
        ],
    }


class CareerPathSimulatorTests(unittest.TestCase):
    def test_roadmap_keywords_resolve_to_career_path_simulator(self) -> None:
        intent = resolve_intent(
            "Hãy tạo roadmap 30 60 90 ngày cho hướng nghề của tôi",
            context=simulator_context(),
        )

        self.assertEqual(intent, INTENT_LEARNING_PLAN)

    def test_template_answer_uses_profile_skill_gap_and_jobs(self) -> None:
        answer = build_template_answer(
            "Cho tôi lộ trình 90 ngày",
            simulator_context(),
            [],
            INTENT_LEARNING_PLAN,
        )

        self.assertIn("Career Path Simulator 30/60/90 ngày:", answer)
        self.assertIn("Mục tiêu chính: Backend Developer Laravel", answer)
        self.assertIn("Docker", answer)
        self.assertIn("30 ngày đầu:", answer)
        self.assertIn("60 ngày:", answer)
        self.assertIn("90 ngày:", answer)
        self.assertIn("Backend Developer Laravel - TechViet", answer)

    def test_chatbot_non_model_provider_returns_simulator_answer(self) -> None:
        with patch("app.services.chatbot._resolve_provider", return_value=("template", TemplateChatProvider())):
            response = generate_career_chat_reply(
                1,
                "Tôi cần lộ trình 30/60/90 ngày để tăng cơ hội ứng tuyển",
                context=simulator_context(),
                history=[],
                force_model=False,
            )

        self.assertTrue(response["success"])
        self.assertEqual(response["data"]["intent"], INTENT_LEARNING_PLAN)
        self.assertIn("Career Path Simulator 30/60/90 ngày:", response["data"]["answer"])


if __name__ == "__main__":
    unittest.main()
