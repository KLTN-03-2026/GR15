from __future__ import annotations

import unittest
from unittest.mock import patch

from app.providers.chat_ollama_provider import _compact_context as compact_ollama_context
from app.providers.chat_openai_provider import _compact_context as compact_openai_context
from app.services.chatbot import generate_career_chat_reply
from app.providers.chat_template_provider import TemplateChatProvider
from app.services.chatbot_intent_engine import (
    INTENT_LEARNING_PLAN,
    INTENT_JOB_RECOMMENDATION,
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

        self.assertIn("Mô phỏng lộ trình nghề nghiệp 30/60/90 ngày:", answer)
        self.assertIn("Mục tiêu chính: Backend Developer Laravel", answer)
        self.assertIn("Docker", answer)
        self.assertIn("30 ngày:", answer)
        self.assertIn("60 ngày:", answer)
        self.assertIn("90 ngày:", answer)
        self.assertIn("Backend Developer Laravel", answer)

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
        self.assertIn("Mô phỏng lộ trình nghề nghiệp 30/60/90 ngày:", response["data"]["answer"])

    def test_job_recommendation_tolerates_legacy_string_skill_hint_payload(self) -> None:
        context = simulator_context()
        context["career_report"]["goi_y_ky_nang_bo_sung"] = "Docker, Redis, Thiết kế hệ thống"

        answer = build_template_answer(
            "Trong hệ thống hiện có job nào gần nhất với hồ sơ của tôi?",
            context,
            [],
            INTENT_JOB_RECOMMENDATION,
        )

        self.assertIn("Vị trí gần nhất hiện tại là Backend Developer Laravel.", answer)

    def test_compact_context_accepts_legacy_string_skill_hint_payload(self) -> None:
        context = simulator_context()
        context["career_report"]["goi_y_ky_nang_bo_sung"] = "Docker, Redis, Thiết kế hệ thống"

        ollama_context = compact_ollama_context(context)
        openai_context = compact_openai_context(context)

        self.assertEqual(
            ollama_context["career_report"]["goi_y_ky_nang_bo_sung"]["skills"][:2],
            ["Docker", "Redis"],
        )
        self.assertEqual(
            openai_context["career_report"]["goi_y_ky_nang_bo_sung"]["skills"][:2],
            ["Docker", "Redis"],
        )

    def test_learning_plan_prefers_explicit_vue_topic_over_profile_target(self) -> None:
        context = simulator_context()
        context["candidate_profile"]["vi_tri_ung_tuyen_muc_tieu"] = "System Administrator"
        context["career_report"]["nghe_de_xuat"] = "System Administrator"
        context["top_matching_jobs"] = [
            {
                "job_title": "System Administrator",
                "score": 85.4,
                "matched_skills": ["Linux", "Networking"],
                "missing_skills": ["Monitoring"],
            }
        ]

        answer = build_template_answer(
            "Hãy gợi ý lộ trình 30/60/90 ngày để tôi học frontend VueJS.",
            context,
            [],
            INTENT_LEARNING_PLAN,
        )

        self.assertIn("Mục tiêu chính: Frontend Vue.js.", answer)
        self.assertIn("Vue.js nền tảng", answer)
        self.assertNotIn("Mục tiêu chính: System Administrator.", answer)


if __name__ == "__main__":
    unittest.main()
