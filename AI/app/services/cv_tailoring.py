from __future__ import annotations

import json

from app.core.config import settings


MODEL_VERSION = f"cv_tailoring_v1.0::rule_based::{settings.local_llm_model}"


def generate_cv_tailoring(
    ho_so_id: int,
    tin_tuyen_dung_id: int,
    cv_profile: dict | None = None,
    jd_profile: dict | None = None,
) -> dict:
    cv = cv_profile or {}
    jd = jd_profile or {}
    job_title = jd.get("title") or "vị trí ứng tuyển"
    company = jd.get("company") or "công ty"
    job_skills = _string_list(jd.get("skills"))
    cv_skills = _string_list(cv.get("skills"))
    matched = [skill for skill in cv_skills if _contains_similar(skill, job_skills)]
    missing = [skill for skill in job_skills if not _contains_similar(skill, cv_skills)]
    prioritized_skills = _prioritized_skills(cv.get("skill_items") or cv_skills, matched, job_skills)

    tailored_profile = {
        "title": _truncate(f"CV {job_title} - {company}", 190),
        "career_goal": (
            f"Ứng tuyển vị trí {job_title}, tập trung thể hiện kinh nghiệm, kỹ năng và dự án phù hợp "
            f"với yêu cầu tuyển dụng của {company}."
        ),
        "summary": _tailored_summary(cv, job_title, company, matched),
        "skills": prioritized_skills,
        "experiences": _prioritize_items(cv.get("experiences") or [], job_skills),
        "projects": _prioritize_items(cv.get("projects") or [], job_skills),
        "education": cv.get("education") or [],
        "certificates": cv.get("certificates") or [],
    }

    return {
        "success": True,
        "message": "Đã tạo nội dung CV tối ưu theo JD.",
        "data": {
            "tailored_profile": tailored_profile,
            "matched_keywords": matched[:10],
            "skill_gaps": missing[:10],
            "recommendations": _recommendations(matched, missing, job_title),
            "cover_letter_suggestion": _cover_letter_suggestion(job_title, company, matched),
            "source_profile_id": ho_so_id,
            "job_id": tin_tuyen_dung_id,
            "model_version": MODEL_VERSION,
        },
    }


def _string_list(value) -> list[str]:
    if not value:
        return []

    if isinstance(value, str):
        return [value.strip()] if value.strip() else []

    if not isinstance(value, list):
        return []

    items: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = item
        elif isinstance(item, dict):
            text = item.get("ten") or item.get("name") or item.get("skill_name") or item.get("ten_ky_nang") or ""
        else:
            text = ""

        text = str(text).strip()
        if text and text.lower() not in {existing.lower() for existing in items}:
            items.append(text)
    return items


def _contains_similar(needle: str, haystack: list[str]) -> bool:
    needle_lower = needle.lower()
    for item in haystack:
        candidate = item.lower()
        if candidate == needle_lower or needle_lower in candidate or candidate in needle_lower:
            return True
    return False


def _prioritized_skills(skill_items, matched: list[str], job_skills: list[str]) -> list[dict]:
    normalized: list[dict] = []
    for item in skill_items if isinstance(skill_items, list) else []:
        if isinstance(item, str):
            name = item.strip()
            level = "kha"
        elif isinstance(item, dict):
            name = str(item.get("ten") or item.get("name") or item.get("skill_name") or "").strip()
            level = item.get("muc_do") or item.get("level") or "kha"
        else:
            continue

        if not name:
            continue

        normalized.append({
            "ten": name,
            "muc_do": "tot" if _contains_similar(name, matched) else level,
        })

    normalized.sort(key=lambda item: (
        0 if _contains_similar(item["ten"], matched) else 1,
        0 if _contains_similar(item["ten"], job_skills) else 1,
        item["ten"].lower(),
    ))

    seen: set[str] = set()
    result: list[dict] = []
    for item in normalized:
        key = item["ten"].lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)

    return result[:14]


def _prioritize_items(items, keywords: list[str]) -> list[dict]:
    if not isinstance(items, list):
        return []

    def score(item) -> int:
        raw = json.dumps(item, ensure_ascii=False).lower()
        return sum(1 for keyword in keywords if keyword.lower() in raw)

    return sorted([item for item in items if isinstance(item, dict)], key=score, reverse=True)


def _tailored_summary(cv: dict, job_title: str, company: str, matched: list[str]) -> str:
    base = (cv.get("summary") or cv.get("career_goal") or "").strip()
    years = cv.get("years_experience")
    years_text = f"{years} năm kinh nghiệm" if years not in (None, "", 0) else "kinh nghiệm phù hợp"
    skill_text = ", ".join(matched[:4])

    opening = f"Ứng viên có {years_text}, định hướng ứng tuyển vị trí {job_title} tại {company}."
    if skill_text:
        opening += f" Các điểm mạnh nên nhấn mạnh trong CV gồm {skill_text}."

    return f"{opening} {base}".strip()


def _recommendations(matched: list[str], missing: list[str], job_title: str) -> list[str]:
    items = [
        f"Đưa các kinh nghiệm/dự án liên quan trực tiếp tới {job_title} lên trước.",
        "Viết lại mô tả công việc theo kết quả và phạm vi đóng góp cụ thể.",
    ]

    if matched:
        items.insert(0, "Ưu tiên các keyword đang khớp với JD: " + ", ".join(matched[:5]) + ".")

    if missing:
        items.append("Nếu có kinh nghiệm với các kỹ năng còn thiếu, hãy bổ sung minh chứng: " + ", ".join(missing[:5]) + ".")

    return items


def _cover_letter_suggestion(job_title: str, company: str, matched: list[str]) -> str:
    skills = ", ".join(matched[:3]) if matched else "các kinh nghiệm liên quan"
    return (
        f"Tôi mong muốn ứng tuyển vị trí {job_title} tại {company}. "
        f"Với nền tảng về {skills}, tôi tin mình có thể nhanh chóng đóng góp vào công việc và phối hợp hiệu quả với đội ngũ."
    )


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
