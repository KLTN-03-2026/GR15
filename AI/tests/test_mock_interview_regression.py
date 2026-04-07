from __future__ import annotations

import unittest

from app.services.mock_interview import (
    _resolve_role_family,
    evaluate_mock_interview_answer,
    generate_mock_interview_question,
    generate_mock_interview_report,
)


def backend_context() -> dict:
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
            },
        },
        "top_matching_jobs": [
            {
                "job_title": "Backend Developer Laravel",
                "score": 39.26,
                "matched_skills": ["Git", "Laravel", "REST API"],
                "missing_skills": ["Docker", "MySQL"],
                "explanation": "Hồ sơ có nền tảng backend nhưng vẫn thiếu một số kỹ năng quan trọng.",
            }
        ],
        "related_job": {
            "title": "Backend Developer Laravel",
            "level": "Junior",
            "skills": ["Laravel", "MySQL", "REST API", "Docker"],
        },
    }


def mobile_context() -> dict:
    return {
        "candidate_profile": {
            "ho_ten": "Tran Thi B",
            "tieu_de_ho_so": "CV Mobile Flutter",
            "parsed_skills": ["Flutter", "Dart", "Firebase"],
        },
        "career_report": {
            "nghe_de_xuat": "Mobile Developer",
            "muc_do_phu_hop": 58.0,
            "goi_y_ky_nang_bo_sung": {
                "skills": ["Android", "iOS"],
            },
        },
        "top_matching_jobs": [
            {
                "job_title": "Mobile Developer Flutter",
                "score": 58.0,
                "matched_skills": ["Flutter", "Firebase"],
                "missing_skills": ["Android"],
            }
        ],
        "related_job": {
            "title": "Mobile Developer Flutter",
            "level": "Junior",
            "skills": ["Flutter", "Firebase", "Android", "iOS"],
        },
    }


class MockInterviewRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.backend = backend_context()
        self.mobile = mobile_context()

    def test_role_family_backend_detects_correctly(self) -> None:
        self.assertEqual(_resolve_role_family(self.backend), "backend")

    def test_role_family_mobile_detects_correctly(self) -> None:
        self.assertEqual(_resolve_role_family(self.mobile), "mobile")

    def test_generate_question_returns_role_family(self) -> None:
        result = generate_mock_interview_question(1, interview_context=self.backend, transcript=[])
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["role_family"], "backend")

    def test_first_question_does_not_include_answer_outline(self) -> None:
        result = generate_mock_interview_question(1, interview_context=self.backend, transcript=[])
        text = result["data"]["question_text"].lower()
        self.assertNotIn("gợi ý trả lời", text)
        self.assertNotIn("trả lời mẫu", text)
        self.assertNotIn("đáp án", text)

    def test_first_question_does_not_add_irrelevant_skill(self) -> None:
        result = generate_mock_interview_question(1, interview_context=self.backend, transcript=[])
        text = result["data"]["question_text"].lower()
        self.assertNotIn("firebase", text)

    def test_short_answer_triggers_follow_up_or_next_question(self) -> None:
        question = generate_mock_interview_question(1, interview_context=self.backend, transcript=[])["data"]
        result = evaluate_mock_interview_answer(
            1,
            question_payload=question,
            answer="Tôi có làm Laravel và API.",
            interview_context=self.backend,
            transcript=[],
        )
        self.assertTrue(result["success"])
        self.assertIn("next_question", result["data"])
        self.assertTrue(result["data"]["next_question"])

    def test_report_contains_assessment_criteria_and_role_family(self) -> None:
        transcript = [
            {
                "role": "assistant",
                "content": "Câu hỏi",
                "metadata": {"type": "interview_feedback", "question_index": 1, "technical_score": 62, "communication_score": 58, "jd_fit_score": 60, "clarity_score": 56, "specificity_score": 50, "structure_score": 54, "total_score": 58, "strengths": ["Có ví dụ"], "weaknesses": ["Thiếu cấu trúc"]},
            },
            {
                "role": "assistant",
                "content": "Câu hỏi",
                "metadata": {"type": "interview_feedback", "question_index": 2, "technical_score": 68, "communication_score": 64, "jd_fit_score": 66, "clarity_score": 62, "specificity_score": 60, "structure_score": 58, "total_score": 64, "strengths": ["Bám kỹ thuật"], "weaknesses": ["Thiếu ví dụ sâu"]},
            },
        ]
        result = generate_mock_interview_report(1, interview_context=self.backend, transcript=transcript)
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["metadata"]["role_family"], "backend")
        self.assertTrue(result["data"]["metadata"]["assessment_criteria"])

    def test_mobile_report_role_family_matches(self) -> None:
        transcript = [
            {
                "role": "assistant",
                "content": "Câu hỏi",
                "metadata": {"type": "interview_feedback", "question_index": 1, "technical_score": 72, "communication_score": 62, "jd_fit_score": 70, "clarity_score": 64, "specificity_score": 61, "structure_score": 59, "total_score": 66, "strengths": ["Bám kỹ năng mobile"], "weaknesses": ["Thiếu chiều sâu"]},
            },
        ]
        result = generate_mock_interview_report(1, interview_context=self.mobile, transcript=transcript)
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["metadata"]["role_family"], "mobile")


if __name__ == "__main__":
    unittest.main()
