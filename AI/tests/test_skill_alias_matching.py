from __future__ import annotations

import unittest

from app.services.matcher import match_cv_jd
from app.services.matcher import _calculate_text_similarity_score
from app.services.matcher import _extract_year_number
from app.services.skill_catalog import canonical_skill_display_name, canonicalize_skill_name


class SkillAliasMatchingTests(unittest.TestCase):
    def test_catalog_canonicalizes_common_aliases(self) -> None:
        self.assertEqual(canonicalize_skill_name("JS"), canonicalize_skill_name("JavaScript"))
        self.assertEqual(canonical_skill_display_name("reactjs"), "React")
        self.assertEqual(canonical_skill_display_name("postgres"), "PostgreSQL")

    def test_cv_jd_matching_uses_skill_alias_catalog(self) -> None:
        result = match_cv_jd(
            1,
            2,
            cv_profile={
                "parsed_skills": ["JS", "reactjs", "postgres"],
                "raw_text": "Frontend developer using JS, ReactJS and Postgres.",
            },
            jd_profile={
                "required_skills": [
                    {"skill_name": "JavaScript", "bat_buoc": True, "trong_so": 1},
                    {"skill_name": "React", "bat_buoc": True, "trong_so": 1},
                    {"skill_name": "PostgreSQL", "bat_buoc": False, "trong_so": 1},
                ],
                "raw_text": "Need JavaScript, React and PostgreSQL.",
            },
        )

        self.assertTrue(result["success"], result.get("error"))
        data = result["data"]
        self.assertEqual(data["diem_ky_nang"], 75.0)
        self.assertEqual(
            [item["skill_name"] for item in data["matched_skills_json"]],
            ["JavaScript", "React", "PostgreSQL"],
        )
        self.assertEqual(data["missing_skills_json"], [])

    def test_experience_parser_supports_month_inputs_like_cv_builder(self) -> None:
        self.assertEqual(_extract_year_number("6 tháng"), 0.5)
        self.assertEqual(_extract_year_number("0.5"), 0.5)
        self.assertEqual(_extract_year_number("1 năm"), 1.0)
        self.assertEqual(_extract_year_number("Không yêu cầu kinh nghiệm"), 0.0)

    def test_text_similarity_uses_skill_alias_context(self) -> None:
        score = _calculate_text_similarity_score(
            {
                "raw_text": "Built iPhone app integrating Firestore and API services.",
            },
            {
                "raw_text": "Need iOS developer with Firebase and REST API experience.",
            },
        )

        self.assertGreaterEqual(score, 40.0)


if __name__ == "__main__":
    unittest.main()
