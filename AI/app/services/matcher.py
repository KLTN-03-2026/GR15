from __future__ import annotations

from collections import Counter
import re
from difflib import SequenceMatcher

from app.core.logger import get_logger
from app.services.skill_catalog import SKILL_CATALOG, normalize_search_text


logger = get_logger(__name__)

MODEL_VERSION = "matching_v4_salary_location_workmode"

EXACT_SKILL_COMPONENT_WEIGHT = 0.75
SEMANTIC_SKILL_COMPONENT_WEIGHT = 0.25

TOKEN_STOPWORDS = {
    "va",
    "voi",
    "hoac",
    "la",
    "cac",
    "trong",
    "cho",
    "mot",
    "nhung",
    "yeu",
    "cau",
    "ung",
    "vien",
    "kinh",
    "nghiem",
    "duoc",
    "lam",
    "viec",
    "co",
    "the",
    "can",
    "su",
    "noi",
    "dung",
    "and",
    "with",
    "the",
    "for",
    "from",
    "you",
    "your",
    "our",
    "will",
    "must",
    "job",
    "candidate",
    "work",
    "working",
    "experience",
    "skills",
    "skill",
    "year",
    "years",
}

SEMANTIC_DOMAIN_TOKENS = {
    "marketing",
    "sales",
    "accounting",
    "finance",
    "recruitment",
    "hr",
    "design",
    "developer",
    "development",
    "testing",
    "analysis",
    "analytics",
    "data",
    "logistics",
    "support",
    "customer",
    "mobile",
    "ios",
    "android",
    "backend",
    "frontend",
    "seo",
    "content",
}

EDUCATION_LEVELS = {
    "trung hoc": 1,
    "cap 3": 1,
    "cao dang": 2,
    "college": 2,
    "dai hoc": 3,
    "university": 3,
    "cu nhan": 3,
    "ky su": 3,
    "thac si": 4,
    "master": 4,
    "tien si": 5,
    "phd": 5,
}

LEVEL_WEIGHT_PROFILES = {
    "intern": {
        "skill": 0.36,
        "experience": 0.09,
        "education": 0.17,
        "text_similarity": 0.22,
        "salary": 0.05,
        "location": 0.06,
        "work_mode": 0.05,
    },
    "fresher": {
        "skill": 0.38,
        "experience": 0.11,
        "education": 0.13,
        "text_similarity": 0.22,
        "salary": 0.05,
        "location": 0.06,
        "work_mode": 0.05,
    },
    "junior": {
        "skill": 0.39,
        "experience": 0.18,
        "education": 0.08,
        "text_similarity": 0.2,
        "salary": 0.05,
        "location": 0.06,
        "work_mode": 0.04,
    },
    "mid": {
        "skill": 0.34,
        "experience": 0.29,
        "education": 0.07,
        "text_similarity": 0.17,
        "salary": 0.05,
        "location": 0.05,
        "work_mode": 0.03,
    },
    "senior": {
        "skill": 0.28,
        "experience": 0.38,
        "education": 0.05,
        "text_similarity": 0.16,
        "salary": 0.06,
        "location": 0.04,
        "work_mode": 0.03,
    },
    "lead_manager": {
        "skill": 0.23,
        "experience": 0.43,
        "education": 0.06,
        "text_similarity": 0.15,
        "salary": 0.06,
        "location": 0.04,
        "work_mode": 0.03,
    },
    "default": {
        "skill": 0.36,
        "experience": 0.27,
        "education": 0.08,
        "text_similarity": 0.17,
        "salary": 0.05,
        "location": 0.04,
        "work_mode": 0.03,
    },
}

SKILL_LOOKUP = {
    normalize_search_text(item["skill_name"]).strip(): {
        "skill_name": item["skill_name"],
        "category": item.get("category"),
        "aliases": [normalize_search_text(alias).strip() for alias in item.get("aliases", []) if alias],
    }
    for item in SKILL_CATALOG
}


def match_cv_jd(
    ho_so_id: int,
    tin_tuyen_dung_id: int,
    *,
    cv_profile: dict | None = None,
    jd_profile: dict | None = None,
) -> dict:
    logger.info("Matching ho_so_id=%s tin_tuyen_dung_id=%s", ho_so_id, tin_tuyen_dung_id)

    try:
        if not cv_profile or not jd_profile:
            raise ValueError("Thiếu dữ liệu CV/JD để thực hiện matching.")

        level_info = _resolve_job_level(jd_profile)
        weights = level_info["weights"]
        cv_skill_names = _extract_cv_skill_names(cv_profile)
        jd_skill_items = _extract_jd_skill_items(jd_profile)

        (
            matched_skills,
            missing_skills,
            near_matched_skills,
            skill_score,
            exact_skill_score,
            semantic_skill_score,
        ) = _calculate_skill_score(cv_skill_names, jd_skill_items)
        experience_score = _calculate_experience_score(cv_profile, jd_profile)
        education_score = _calculate_education_score(cv_profile, jd_profile)
        text_similarity_score = _calculate_text_similarity_score(cv_profile, jd_profile)
        salary_score, salary_fit_detail = _calculate_salary_score(cv_profile, jd_profile)
        location_score, location_fit_detail = _calculate_location_score(cv_profile, jd_profile)
        work_mode_score, work_mode_fit_detail = _calculate_work_mode_score(cv_profile, jd_profile)
        cv_years = _extract_cv_years(cv_profile)
        jd_years = _extract_jd_years(jd_profile)
        cv_education_level = _extract_education_level(
            cv_profile.get("trinh_do"),
            cv_profile.get("parsed_education"),
        )
        jd_education_level = _extract_education_level(
            jd_profile.get("trinh_do_yeu_cau"),
            None,
        )
        candidate_level_info = _resolve_candidate_level(cv_profile, cv_years)

        diem_phu_hop = round(
            (skill_score * weights["skill"]) +
            (experience_score * weights["experience"]) +
            (education_score * weights["education"]) +
            (text_similarity_score * weights["text_similarity"]) +
            (salary_score * weights["salary"]) +
            (location_score * weights["location"]) +
            (work_mode_score * weights["work_mode"]),
            2,
        )

        chi_tiet_diem = {
            "skill_score": round(skill_score, 2),
            "exact_skill_score": round(exact_skill_score, 2),
            "semantic_skill_score": round(semantic_skill_score, 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "text_similarity_score": round(text_similarity_score, 2),
            "salary_score": round(salary_score, 2),
            "location_score": round(location_score, 2),
            "work_mode_score": round(work_mode_score, 2),
            "weights": weights,
            "job_level": level_info["level"],
            "job_level_source": level_info["source"],
            "job_level_signals": level_info["signals"],
            "candidate_level": candidate_level_info["level"],
            "candidate_level_source": candidate_level_info["source"],
            "candidate_level_signals": candidate_level_info["signals"],
            "cv_years": cv_years,
            "jd_required_years": jd_years,
            "cv_education_level": cv_education_level,
            "jd_education_level": jd_education_level,
            "cv_trinh_do": cv_profile.get("trinh_do"),
            "jd_trinh_do_yeu_cau": jd_profile.get("trinh_do_yeu_cau"),
            "cv_skills": sorted(cv_skill_names),
            "jd_skills": [item["skill_name"] for item in jd_skill_items],
            "matched_count": len(matched_skills),
            "missing_count": len(missing_skills),
            "near_match_count": len(near_matched_skills),
            "near_matched_skills": near_matched_skills,
            "salary_fit_detail": salary_fit_detail,
            "location_fit_detail": location_fit_detail,
            "work_mode_fit_detail": work_mode_fit_detail,
        }

        return {
            "success": True,
            "model_version": MODEL_VERSION,
            "data": {
                "diem_phu_hop": diem_phu_hop,
                "diem_ky_nang": round(skill_score, 2),
                "diem_kinh_nghiem": round(experience_score, 2),
                "diem_hoc_van": round(education_score, 2),
                "diem_luong": round(salary_score, 2),
                "diem_dia_diem": round(location_score, 2),
                "diem_hinh_thuc_lam_viec": round(work_mode_score, 2),
                "chi_tiet_diem": chi_tiet_diem,
                "matched_skills_json": matched_skills,
                "missing_skills_json": missing_skills,
                "danh_sach_ky_nang_thieu": ", ".join(item["skill_name"] for item in missing_skills) or None,
                "explanation": _build_explanation(
                    diem_phu_hop=diem_phu_hop,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    near_matched_skills=near_matched_skills,
                    experience_score=experience_score,
                    education_score=education_score,
                    text_similarity_score=text_similarity_score,
                    salary_score=salary_score,
                    location_score=location_score,
                    work_mode_score=work_mode_score,
                    level_info=level_info,
                ),
                "score_explanation_items": _build_score_explanation_items(
                    skill_score=skill_score,
                    experience_score=experience_score,
                    education_score=education_score,
                    text_similarity_score=text_similarity_score,
                    salary_score=salary_score,
                    location_score=location_score,
                    work_mode_score=work_mode_score,
                    weights=weights,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    salary_fit_detail=salary_fit_detail,
                    location_fit_detail=location_fit_detail,
                    work_mode_fit_detail=work_mode_fit_detail,
                ),
                "model_version": MODEL_VERSION,
            },
            "error": None,
        }
    except Exception as exc:
        logger.exception("Matching failed for ho_so_id=%s tin_tuyen_dung_id=%s", ho_so_id, tin_tuyen_dung_id)
        return {
            "success": False,
            "model_version": MODEL_VERSION,
            "data": {
                "diem_phu_hop": 0,
                "diem_ky_nang": 0,
                "diem_kinh_nghiem": 0,
                "diem_hoc_van": 0,
                "diem_luong": 0,
                "diem_dia_diem": 0,
                "diem_hinh_thuc_lam_viec": 0,
                "chi_tiet_diem": {},
                "matched_skills_json": [],
                "missing_skills_json": [],
                "danh_sach_ky_nang_thieu": None,
                "explanation": None,
                "score_explanation_items": [],
                "model_version": MODEL_VERSION,
            },
            "error": str(exc),
        }


def _extract_cv_skill_names(cv_profile: dict) -> set[str]:
    parsed_skills = cv_profile.get("parsed_skills") or []
    skill_names = set()

    for item in parsed_skills:
        if isinstance(item, dict) and item.get("skill_name"):
            skill_names.add(_normalize_skill_name(item["skill_name"]))
        elif isinstance(item, str):
            skill_names.add(_normalize_skill_name(item))

    return {item for item in skill_names if item}


def _extract_jd_skill_items(jd_profile: dict) -> list[dict]:
    required_skills = jd_profile.get("required_skills") or []
    parsed_skills = jd_profile.get("parsed_skills") or []
    source_items = required_skills if required_skills else parsed_skills

    items = []
    for item in source_items:
        if isinstance(item, str):
            skill_name = item
            bat_buoc = False
            trong_so = 1.0
        elif isinstance(item, dict):
            skill_name = item.get("skill_name") or item.get("ten_ky_nang") or item.get("name")
            bat_buoc = bool(item.get("bat_buoc", False))
            trong_so = float(item.get("trong_so", 1.0) or 1.0)
        else:
            continue

        if not skill_name:
            continue

        items.append(
            {
                "skill_name": str(skill_name),
                "normalized": _normalize_skill_name(str(skill_name)),
                "bat_buoc": bat_buoc,
                "trong_so": trong_so,
            }
        )

    deduped = {}
    for item in items:
        deduped[item["normalized"]] = item

    return [item for item in deduped.values() if item["normalized"]]


def _calculate_skill_score(
    cv_skill_names: set[str],
    jd_skill_items: list[dict],
) -> tuple[list[dict], list[dict], list[dict], float, float, float]:
    if not jd_skill_items:
        base_score = 60.0 if cv_skill_names else 0.0
        return [], [], [], base_score, base_score, 0.0

    total_weight = sum(item["trong_so"] for item in jd_skill_items) or 1.0
    matched_weight = 0.0
    semantic_weight = 0.0
    matched_skills = []
    missing_skills = []
    near_matched_skills = []

    for item in jd_skill_items:
        payload = {
            "skill_name": item["skill_name"],
            "bat_buoc": item["bat_buoc"],
            "trong_so": item["trong_so"],
        }

        if item["normalized"] in cv_skill_names:
            matched_weight += item["trong_so"]
            matched_skills.append(payload)
            continue

        similarity = _find_best_skill_similarity(item["normalized"], cv_skill_names)
        if similarity and similarity["score"] >= 0.55:
            semantic_credit = item["trong_so"] * _semantic_credit_ratio(similarity)
            semantic_weight += semantic_credit
            near_matched_skills.append(
                {
                    **payload,
                    "matched_with": similarity["matched_skill_name"],
                    "matched_score": round(similarity["score"], 2),
                    "match_type": similarity["match_type"],
                    "semantic_credit_ratio": round(_semantic_credit_ratio(similarity), 2),
                }
            )
            continue

        missing_skills.append(payload)

    exact_skill_score = (matched_weight / total_weight) * 100
    semantic_skill_score = (semantic_weight / total_weight) * 100
    score = (
        exact_skill_score * EXACT_SKILL_COMPONENT_WEIGHT
        + semantic_skill_score * SEMANTIC_SKILL_COMPONENT_WEIGHT
    )
    return (
        matched_skills,
        missing_skills,
        near_matched_skills,
        round(score, 2),
        round(exact_skill_score, 2),
        round(semantic_skill_score, 2),
    )


def _calculate_experience_score(cv_profile: dict, jd_profile: dict) -> float:
    cv_years = _extract_cv_years(cv_profile)
    jd_years = _extract_jd_years(jd_profile)

    if jd_years is None:
        return 75.0 if cv_years is not None else 60.0
    if cv_years is None:
        return 35.0
    if cv_years >= jd_years:
        return 100.0

    return round(max((cv_years / max(jd_years, 1)) * 100, 25.0), 2)


def _calculate_education_score(cv_profile: dict, jd_profile: dict) -> float:
    cv_level = _extract_education_level(
        cv_profile.get("trinh_do"),
        cv_profile.get("parsed_education"),
    )
    jd_level = _extract_education_level(
        jd_profile.get("trinh_do_yeu_cau"),
        None,
    )

    if jd_level is None:
        return 75.0 if cv_level is not None else 60.0
    if cv_level is None:
        return 40.0
    if cv_level >= jd_level:
        return 100.0

    return round(max((cv_level / jd_level) * 100, 30.0), 2)


def _extract_cv_years(cv_profile: dict) -> float | None:
    cv_years = cv_profile.get("kinh_nghiem_nam")
    if isinstance(cv_years, (int, float)):
        return float(cv_years)

    parsed_experience = cv_profile.get("parsed_experience") or []
    joined_text = " ".join(
        item.get("content", "") if isinstance(item, dict) else str(item)
        for item in parsed_experience
    )
    return _extract_year_number(joined_text)


def _extract_jd_years(jd_profile: dict) -> float | None:
    return _extract_year_number(str(jd_profile.get("kinh_nghiem_yeu_cau") or ""))


def _extract_year_number(text: str) -> float | None:
    normalized = normalize_search_text(text)
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(nam|year)", normalized)
    if match:
        return float(match.group(1).replace(",", "."))

    if "duoi 1 nam" in normalized or "less than 1 year" in normalized:
        return 1.0

    return None


def _extract_education_level(primary_text: str | None, parsed_education: list | None) -> int | None:
    candidates = [primary_text or ""]
    if parsed_education:
        candidates.extend(
            item.get("content", "") if isinstance(item, dict) else str(item)
            for item in parsed_education
        )

    joined = normalize_search_text(" ".join(candidates))
    for keyword, level in EDUCATION_LEVELS.items():
        if keyword in joined:
            return level

    return None


def _resolve_job_level(jd_profile: dict) -> dict:
    cap_bac = normalize_search_text(str(jd_profile.get("cap_bac") or ""))
    tieu_de = normalize_search_text(str(jd_profile.get("tieu_de") or ""))
    kinh_nghiem_yeu_cau = normalize_search_text(str(jd_profile.get("kinh_nghiem_yeu_cau") or ""))

    text_blob = " ".join(filter(None, [cap_bac, tieu_de, kinh_nghiem_yeu_cau]))
    years = _extract_jd_years(jd_profile)
    signals = []

    if any(keyword in text_blob for keyword in {"intern", "thuc tap", "thuc tap sinh"}):
        signals.append("intern_keyword")
        return _build_level_payload("intern", "cap_bac_or_title", signals)

    if any(keyword in text_blob for keyword in {"fresher", "new grad", "moi tot nghiep"}):
        signals.append("fresher_keyword")
        return _build_level_payload("fresher", "cap_bac_or_title", signals)

    if any(keyword in text_blob for keyword in {"junior", "jun", "staff"}):
        signals.append("junior_keyword")
        return _build_level_payload("junior", "cap_bac_or_title", signals)

    if any(keyword in text_blob for keyword in {"senior", "sr", "expert", "chuyen vien cao cap"}):
        signals.append("senior_keyword")
        return _build_level_payload("senior", "cap_bac_or_title", signals)

    if any(keyword in text_blob for keyword in {"lead", "leader", "manager", "truong nhom", "truong phong", "giam sat"}):
        signals.append("lead_manager_keyword")
        return _build_level_payload("lead_manager", "cap_bac_or_title", signals)

    if years is not None:
        signals.append(f"experience_years:{years}")
        if years < 1:
            return _build_level_payload("intern", "kinh_nghiem_yeu_cau", signals)
        if years <= 1:
            return _build_level_payload("fresher", "kinh_nghiem_yeu_cau", signals)
        if years <= 2:
            return _build_level_payload("junior", "kinh_nghiem_yeu_cau", signals)
        if years <= 4:
            return _build_level_payload("mid", "kinh_nghiem_yeu_cau", signals)
        if years <= 7:
            return _build_level_payload("senior", "kinh_nghiem_yeu_cau", signals)
        return _build_level_payload("lead_manager", "kinh_nghiem_yeu_cau", signals)

    return _build_level_payload("default", "fallback", ["no_clear_level_signal"])


def _build_level_payload(level: str, source: str, signals: list[str]) -> dict:
    return {
        "level": level,
        "source": source,
        "signals": signals,
        "weights": LEVEL_WEIGHT_PROFILES[level],
    }


def _resolve_candidate_level(cv_profile: dict, cv_years: float | None) -> dict:
    tieu_de_ho_so = normalize_search_text(str(cv_profile.get("tieu_de_ho_so") or ""))
    text_blob = tieu_de_ho_so
    signals = []

    if any(keyword in text_blob for keyword in {"intern", "thuc tap", "thuc tap sinh"}):
        signals.append("intern_keyword")
        return {
            "level": "intern",
            "source": "cv_title",
            "signals": signals,
        }

    if any(keyword in text_blob for keyword in {"fresher", "new grad", "moi tot nghiep"}):
        signals.append("fresher_keyword")
        return {
            "level": "fresher",
            "source": "cv_title",
            "signals": signals,
        }

    if any(keyword in text_blob for keyword in {"junior", "jun"}):
        signals.append("junior_keyword")
        return {
            "level": "junior",
            "source": "cv_title",
            "signals": signals,
        }

    if any(keyword in text_blob for keyword in {"senior", "sr", "lead", "manager"}):
        signals.append("senior_or_manager_keyword")
        return {
            "level": "senior_or_manager",
            "source": "cv_title",
            "signals": signals,
        }

    if cv_years is not None:
        signals.append(f"experience_years:{cv_years}")
        if cv_years < 1:
            level = "intern"
        elif cv_years <= 1:
            level = "fresher"
        elif cv_years <= 2:
            level = "junior"
        elif cv_years <= 4:
            level = "mid"
        else:
            level = "senior_or_manager"

        return {
            "level": level,
            "source": "cv_experience",
            "signals": signals,
        }

    return {
        "level": "unknown",
        "source": "fallback",
        "signals": ["no_clear_candidate_signal"],
    }


def _calculate_text_similarity_score(cv_profile: dict, jd_profile: dict) -> float:
    cv_text = normalize_search_text(str(cv_profile.get("raw_text") or ""))
    jd_text = normalize_search_text(str(jd_profile.get("raw_text") or ""))

    if not cv_text or not jd_text:
        return 0.0

    cv_tokens = _tokenize_for_similarity(cv_text)
    jd_tokens = _tokenize_for_similarity(jd_text)

    if not cv_tokens or not jd_tokens:
        return 0.0

    cosine = _cosine_similarity(cv_tokens, jd_tokens)
    jaccard = _jaccard_similarity(cv_tokens, jd_tokens)
    score = (cosine * 0.7 + jaccard * 0.3) * 100
    return round(score, 2)


def _calculate_salary_score(cv_profile: dict, jd_profile: dict) -> tuple[float, dict]:
    cv_range = _extract_salary_range(cv_profile, prefix="cv")
    jd_range = _extract_salary_range(jd_profile, prefix="jd")

    detail = {
        "cv_salary_range": cv_range,
        "jd_salary_range": jd_range,
        "signal": "neutral",
        "message": "Chưa đủ dữ liệu lương hai phía; dùng điểm trung lập để tránh phạt sai.",
    }

    if not cv_range or not jd_range:
        return 70.0, detail

    cv_min, cv_max = cv_range
    jd_min, jd_max = jd_range
    overlap = max(0, min(cv_max, jd_max) - max(cv_min, jd_min))
    cv_width = max(cv_max - cv_min, 1)
    jd_width = max(jd_max - jd_min, 1)

    if overlap > 0:
        ratio = overlap / max(min(cv_width, jd_width), 1)
        score = min(100.0, 78.0 + ratio * 22.0)
        detail.update({"signal": "overlap", "message": "Khoảng lương kỳ vọng và khoảng lương JD có giao nhau."})
        return round(score, 2), detail

    if cv_min > jd_max:
        gap_ratio = (cv_min - jd_max) / max(jd_max, 1)
        score = max(30.0, 72.0 - gap_ratio * 120.0)
        detail.update({"signal": "candidate_expectation_above_job", "message": "Kỳ vọng lương của ứng viên cao hơn khung lương JD."})
        return round(score, 2), detail

    gap_ratio = (jd_min - cv_max) / max(jd_min, 1)
    score = max(65.0, 88.0 - gap_ratio * 60.0)
    detail.update({"signal": "candidate_expectation_below_job", "message": "Kỳ vọng lương của ứng viên thấp hơn hoặc dưới khung JD."})
    return round(score, 2), detail


def _calculate_location_score(cv_profile: dict, jd_profile: dict) -> tuple[float, dict]:
    cv_locations = _extract_locations(cv_profile, ["dia_diem_mong_muon", "dia_chi", "location", "preferred_locations"])
    jd_locations = _extract_locations(jd_profile, ["dia_diem_lam_viec", "location", "locations", "parsed_location_json"])

    detail = {
        "cv_locations": cv_locations,
        "jd_locations": jd_locations,
        "signal": "neutral",
        "message": "Chưa đủ dữ liệu địa điểm hai phía; dùng điểm trung lập.",
    }

    if not cv_locations or not jd_locations:
        return 72.0, detail

    if "remote" in jd_locations or "remote" in cv_locations:
        detail.update({"signal": "remote_flexible", "message": "Có tín hiệu remote nên địa điểm ít ràng buộc hơn."})
        return 92.0, detail

    if set(cv_locations) & set(jd_locations):
        detail.update({"signal": "matched_location", "message": "Địa điểm ứng viên và JD trùng khớp."})
        return 100.0, detail

    if any(_locations_are_close(left, right) for left in cv_locations for right in jd_locations):
        detail.update({"signal": "near_location", "message": "Địa điểm gần hoặc cùng khu vực lớn."})
        return 82.0, detail

    detail.update({"signal": "location_mismatch", "message": "Địa điểm mong muốn và địa điểm JD chưa khớp rõ."})
    return 48.0, detail


def _calculate_work_mode_score(cv_profile: dict, jd_profile: dict) -> tuple[float, dict]:
    cv_modes = _extract_work_modes(cv_profile)
    jd_modes = _extract_work_modes(jd_profile)

    detail = {
        "cv_work_modes": cv_modes,
        "jd_work_modes": jd_modes,
        "signal": "neutral",
        "message": "Chưa đủ dữ liệu hình thức làm việc hai phía; dùng điểm trung lập.",
    }

    if not cv_modes or not jd_modes:
        return 75.0, detail

    if set(cv_modes) & set(jd_modes):
        detail.update({"signal": "matched_work_mode", "message": "Hình thức làm việc mong muốn khớp với JD."})
        return 100.0, detail

    if "hybrid" in cv_modes and ("remote" in jd_modes or "onsite" in jd_modes):
        detail.update({"signal": "partially_flexible", "message": "Ứng viên hybrid có thể phù hợp một phần với remote/onsite."})
        return 78.0, detail
    if "hybrid" in jd_modes and ("remote" in cv_modes or "onsite" in cv_modes):
        detail.update({"signal": "job_partially_flexible", "message": "JD hybrid có thể phù hợp một phần với mong muốn remote/onsite."})
        return 78.0, detail

    detail.update({"signal": "work_mode_mismatch", "message": "Hình thức làm việc chưa khớp rõ."})
    return 52.0, detail


def _build_explanation(
    *,
    diem_phu_hop: float,
    matched_skills: list[dict],
    missing_skills: list[dict],
    near_matched_skills: list[dict],
    experience_score: float,
    education_score: float,
    text_similarity_score: float,
    salary_score: float,
    location_score: float,
    work_mode_score: float,
    level_info: dict,
) -> str:
    if diem_phu_hop >= 80:
        level = "Mức độ phù hợp cao"
    elif diem_phu_hop >= 60:
        level = "Mức độ phù hợp khá"
    else:
        level = "Mức độ phù hợp trung bình hoặc thấp"

    matched_names = ", ".join(item["skill_name"] for item in matched_skills[:6]) or "chưa có kỹ năng trùng khớp rõ ràng"
    missing_names = ", ".join(item["skill_name"] for item in missing_skills[:6]) or "không có kỹ năng thiếu đáng kể"
    near_names = ", ".join(
        f"{item['skill_name']}~{item['matched_with']}"
        for item in near_matched_skills[:4]
    )

    explanation = (
        f"{level}. Hồ sơ đang khớp tốt với các kỹ năng: {matched_names}. "
        f"Kỹ năng còn thiếu hoặc cần bổ sung: {missing_names}. "
        f"Điểm kinh nghiệm đạt {round(experience_score, 2)}/100, điểm học vấn đạt {round(education_score, 2)}/100 "
        f"điểm tương đồng nội dung CV-JD đạt {round(text_similarity_score, 2)}/100, "
        f"điểm lương {round(salary_score, 2)}/100, điểm địa điểm {round(location_score, 2)}/100 "
        f"và điểm hình thức làm việc {round(work_mode_score, 2)}/100. "
        f"Bộ trọng số được áp dụng theo nhóm cấp bậc {level_info['level']}."
    )

    if near_names:
        explanation += f" Hệ thống cũng nhận diện các kỹ năng gần nghĩa/gần vai trò: {near_names}."

    return explanation


def _build_score_explanation_items(
    *,
    skill_score: float,
    experience_score: float,
    education_score: float,
    text_similarity_score: float,
    salary_score: float,
    location_score: float,
    work_mode_score: float,
    weights: dict,
    matched_skills: list[dict],
    missing_skills: list[dict],
    salary_fit_detail: dict,
    location_fit_detail: dict,
    work_mode_fit_detail: dict,
) -> list[dict]:
    return [
        {
            "key": "skills",
            "label": "Kỹ năng",
            "score": round(skill_score, 2),
            "weight": weights.get("skill", 0),
            "message": f"Khớp {len(matched_skills)} kỹ năng, thiếu {len(missing_skills)} kỹ năng so với JD.",
        },
        {
            "key": "experience",
            "label": "Kinh nghiệm",
            "score": round(experience_score, 2),
            "weight": weights.get("experience", 0),
            "message": "So sánh số năm kinh nghiệm ứng viên với yêu cầu trong JD.",
        },
        {
            "key": "education",
            "label": "Học vấn",
            "score": round(education_score, 2),
            "weight": weights.get("education", 0),
            "message": "So sánh trình độ học vấn với yêu cầu tối thiểu.",
        },
        {
            "key": "text_similarity",
            "label": "Ngữ cảnh CV-JD",
            "score": round(text_similarity_score, 2),
            "weight": weights.get("text_similarity", 0),
            "message": "Đo mức độ trùng ngữ cảnh giữa CV và JD sau chuẩn hóa từ khóa.",
        },
        {
            "key": "salary",
            "label": "Lương",
            "score": round(salary_score, 2),
            "weight": weights.get("salary", 0),
            "message": salary_fit_detail.get("message"),
        },
        {
            "key": "location",
            "label": "Địa điểm",
            "score": round(location_score, 2),
            "weight": weights.get("location", 0),
            "message": location_fit_detail.get("message"),
        },
        {
            "key": "work_mode",
            "label": "Hình thức làm việc",
            "score": round(work_mode_score, 2),
            "weight": weights.get("work_mode", 0),
            "message": work_mode_fit_detail.get("message"),
        },
    ]


def _normalize_skill_name(value: str) -> str:
    return normalize_search_text(value).strip()


def _find_best_skill_similarity(jd_skill: str, cv_skill_names: set[str]) -> dict | None:
    jd_meta = SKILL_LOOKUP.get(jd_skill, {"skill_name": jd_skill, "category": None, "aliases": [jd_skill]})
    best_match = None

    for cv_skill in cv_skill_names:
        cv_meta = SKILL_LOOKUP.get(cv_skill, {"skill_name": cv_skill, "category": None, "aliases": [cv_skill]})
        score, match_type = _calculate_skill_similarity(jd_skill, jd_meta, cv_skill, cv_meta)
        if score <= 0:
            continue

        candidate = {
            "score": score,
            "match_type": match_type,
            "matched_skill_name": cv_meta["skill_name"],
        }
        if not best_match or candidate["score"] > best_match["score"]:
            best_match = candidate

    return best_match


def _calculate_skill_similarity(
    jd_skill: str,
    jd_meta: dict,
    cv_skill: str,
    cv_meta: dict,
) -> tuple[float, str]:
    if jd_skill == cv_skill:
        return 1.0, "exact"

    lexical_score = max(
        SequenceMatcher(None, jd_skill, cv_skill).ratio(),
        _best_alias_similarity(jd_meta.get("aliases", []), cv_meta.get("aliases", [])),
    )

    same_category = bool(jd_meta.get("category") and jd_meta.get("category") == cv_meta.get("category"))
    token_similarity = _token_set_similarity(jd_skill, cv_skill)
    shared_domain_score = _shared_domain_similarity(jd_skill, cv_skill)

    if same_category and (lexical_score >= 0.45 or token_similarity >= 0.45):
        return min(max(lexical_score, token_similarity) + 0.2, 0.88), "same_category"

    if lexical_score >= 0.72:
        return lexical_score, "lexical"

    if token_similarity >= 0.68:
        return token_similarity, "token_overlap"

    if shared_domain_score >= 0.55:
        return shared_domain_score, "shared_domain"

    return 0.0, "none"


def _best_alias_similarity(jd_aliases: list[str], cv_aliases: list[str]) -> float:
    best = 0.0
    for left in jd_aliases:
        for right in cv_aliases:
            best = max(best, SequenceMatcher(None, left, right).ratio())
    return best


def _token_set_similarity(left: str, right: str) -> float:
    left_tokens = set(_tokenize_for_similarity(left))
    right_tokens = set(_tokenize_for_similarity(right))
    if not left_tokens or not right_tokens:
        return 0.0

    intersection = len(left_tokens & right_tokens)
    denominator = max(len(left_tokens), len(right_tokens))
    return intersection / denominator if denominator else 0.0


def _semantic_credit_ratio(similarity: dict) -> float:
    score = similarity["score"]
    match_type = similarity["match_type"]

    if match_type == "same_category":
        return min(max(score * 0.7, 0.4), 0.85)
    if match_type in {"lexical", "token_overlap", "shared_domain"}:
        return min(max(score * 0.65, 0.35), 0.8)
    return 0.0


def _tokenize_for_similarity(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9+#./-]+", text)
    return [token for token in tokens if len(token) >= 2 and token not in TOKEN_STOPWORDS]


def _cosine_similarity(left_tokens: list[str], right_tokens: list[str]) -> float:
    left_counter = Counter(left_tokens)
    right_counter = Counter(right_tokens)

    common = set(left_counter) & set(right_counter)
    dot = sum(left_counter[token] * right_counter[token] for token in common)

    left_norm = sum(value * value for value in left_counter.values()) ** 0.5
    right_norm = sum(value * value for value in right_counter.values()) ** 0.5

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot / (left_norm * right_norm)


def _jaccard_similarity(left_tokens: list[str], right_tokens: list[str]) -> float:
    left_set = set(left_tokens)
    right_set = set(right_tokens)
    union = left_set | right_set
    if not union:
        return 0.0
    return len(left_set & right_set) / len(union)


def _shared_domain_similarity(left: str, right: str) -> float:
    left_tokens = set(_tokenize_for_similarity(left))
    right_tokens = set(_tokenize_for_similarity(right))
    shared = (left_tokens & right_tokens) & SEMANTIC_DOMAIN_TOKENS

    if not shared:
        return 0.0

    return min(0.55 + 0.08 * len(shared), 0.72)


def _extract_salary_range(profile: dict, *, prefix: str) -> tuple[int, int] | None:
    direct_min_keys = {
        "cv": ["muc_luong_mong_muon_tu", "expected_salary_from", "salary_min"],
        "jd": ["muc_luong_tu", "salary_from", "salary_min"],
    }[prefix]
    direct_max_keys = {
        "cv": ["muc_luong_mong_muon_den", "expected_salary_to", "salary_max"],
        "jd": ["muc_luong_den", "salary_to", "salary_max"],
    }[prefix]

    values = []
    for key in direct_min_keys + direct_max_keys:
        number = _coerce_salary_number(profile.get(key))
        if number:
            values.append(number)

    parsed_salary = profile.get("parsed_salary_json") or profile.get("parsed_salary") or {}
    if isinstance(parsed_salary, dict):
        for key in ["muc_luong_tu", "muc_luong_den", "salary_from", "salary_to"]:
            number = _coerce_salary_number(parsed_salary.get(key))
            if number:
                values.append(number)

    for key in ["raw_text", "mo_ta_cong_viec", "salary_expectation", "muc_luong_mong_muon"]:
        text_values = _extract_salary_numbers_from_text(str(profile.get(key) or ""))
        values.extend(text_values)

    values = [value for value in values if value > 0]
    if not values:
        return None

    return min(values), max(values)


def _coerce_salary_number(value) -> int | None:
    if isinstance(value, (int, float)) and value > 0:
        number = int(value)
        return number * 1_000_000 if number < 1000 else number
    if isinstance(value, str) and value.strip():
        numbers = _extract_salary_numbers_from_text(value)
        if numbers:
            return numbers[0]
    return None


def _extract_salary_numbers_from_text(text: str) -> list[int]:
    if not text:
        return []

    results = []
    normalized = normalize_search_text(text)
    for number, unit in re.findall(r"(\d+(?:[.,]\d+)?)\s*(trieu|triệu|million|m|vnd|dong|đồng)?", normalized):
        numeric = float(number.replace(",", "."))
        if unit in {"trieu", "triệu", "million", "m"} or numeric < 1000:
            results.append(int(numeric * 1_000_000))
        elif unit in {"vnd", "dong", "đồng"} or numeric >= 1000:
            results.append(int(numeric))
    return results[:4]


def _extract_locations(profile: dict, keys: list[str]) -> list[str]:
    values: list[str] = []
    for key in keys:
        raw = profile.get(key)
        if isinstance(raw, dict):
            raw = raw.get("locations") or raw.get("location") or raw.get("dia_diem")
        if isinstance(raw, list):
            values.extend(str(item) for item in raw)
        elif raw:
            values.extend(re.split(r"[,;/|]+", str(raw)))

    text_blob = " ".join(str(profile.get(key) or "") for key in ["raw_text", "mo_ta_cong_viec", "muc_tieu_nghe_nghiep"])
    values.extend(_detect_known_locations(text_blob))

    normalized_values = []
    for value in values:
        normalized = normalize_search_text(value)
        normalized = normalized.replace("tp hcm", "ho chi minh").replace("hcm", "ho chi minh").replace("hanoi", "ha noi")
        if normalized and normalized not in normalized_values:
            normalized_values.append(normalized)

    return normalized_values[:6]


def _detect_known_locations(text: str) -> list[str]:
    normalized = normalize_search_text(text)
    known = ["ha noi", "hanoi", "ho chi minh", "tp hcm", "hcm", "da nang", "can tho", "hai phong", "remote"]
    return [item for item in known if normalize_search_text(item) in normalized]


def _locations_are_close(left: str, right: str) -> bool:
    if left == right:
        return True
    hcm_aliases = {"ho chi minh", "tp hcm", "hcm", "sai gon"}
    hanoi_aliases = {"ha noi", "hanoi"}
    danang_aliases = {"da nang", "danang"}
    return (
        left in hcm_aliases and right in hcm_aliases
        or left in hanoi_aliases and right in hanoi_aliases
        or left in danang_aliases and right in danang_aliases
    )


def _extract_work_modes(profile: dict) -> list[str]:
    values = []
    for key in ["hinh_thuc_lam_viec", "work_mode", "preferred_work_mode", "parsed_work_mode"]:
        raw = profile.get(key)
        if isinstance(raw, list):
            values.extend(str(item) for item in raw)
        elif raw:
            values.append(str(raw))

    parsed_location = profile.get("parsed_location_json") or profile.get("parsed_location") or {}
    if isinstance(parsed_location, dict) and parsed_location.get("work_mode"):
        values.append(str(parsed_location["work_mode"]))

    values.extend([str(profile.get("raw_text") or ""), str(profile.get("mo_ta_cong_viec") or "")])

    modes = []
    normalized = normalize_search_text(" ".join(values))
    if "remote" in normalized or "tu xa" in normalized or "từ xa" in normalized:
        modes.append("remote")
    if "hybrid" in normalized or "linh hoat" in normalized or "linh hoạt" in normalized:
        modes.append("hybrid")
    if "onsite" in normalized or "tai van phong" in normalized or "tại văn phòng" in normalized or "toan thoi gian" in normalized:
        modes.append("onsite")

    return list(dict.fromkeys(modes))
