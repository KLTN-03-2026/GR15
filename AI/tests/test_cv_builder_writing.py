from app.services.cv_builder_writing import generate_cv_builder_writing


def test_generate_summary_suggestions() -> None:
    result = generate_cv_builder_writing(
        {
            "tieu_de_ho_so": "Backend Developer",
            "kinh_nghiem_nam": 2,
            "ten_nganh_nghe_muc_tieu": "Công nghệ thông tin",
            "ky_nang_json": [{"ten": "Laravel"}, {"ten": "PostgreSQL"}],
        },
        section="summary",
        options={"tone": "impact"},
    )

    suggestions = result["data"]["suggestions"]

    assert result["success"] is True
    assert len(suggestions) == 3
    assert "Backend Developer" in suggestions[0]


def test_generate_skill_suggestions_omits_existing_skills() -> None:
    result = generate_cv_builder_writing(
        {
            "vi_tri_ung_tuyen_muc_tieu": "Backend Developer",
            "ten_nganh_nghe_muc_tieu": "Công nghệ thông tin",
            "ky_nang_json": [{"ten": "Laravel"}],
        },
        section="skills",
        options={},
    )

    skills = result["data"]["skill_suggestions"]
    names = [item["ten"] for item in skills]

    assert "Laravel" not in names
    assert "REST API" in names
