from __future__ import annotations

from collections import Counter
import json
import math
import re
from difflib import SequenceMatcher
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.core.logger import get_logger
from app.providers.gemini_client import generate_text
from app.providers.ollama_client import generate_text as generate_ollama_text
from app.services.llm_timeout import TimeoutError, run_with_timeout
from app.services.skill_catalog import SKILL_CATALOG, canonical_skill_display_name, canonicalize_skill_name, normalize_search_text


logger = get_logger(__name__)

MODEL_VERSION = "matching_v4_salary_location_workmode"

EXACT_SKILL_COMPONENT_WEIGHT = 0.75
SEMANTIC_SKILL_COMPONENT_WEIGHT = 0.25
TEXT_BM25_WEIGHT = 0.55
TEXT_TFIDF_WEIGHT = 0.2
TEXT_LEXICAL_WEIGHT = 0.15
TEXT_SKILL_CONTEXT_WEIGHT = 0.1
BM25_K1 = 1.4
BM25_B = 0.75

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
    include_llm_explanation: bool = True,
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
            "text_similarity_method": {
                "name": "bm25_tfidf_skill_alias_context",
                "description": "BM25/TF-IDF trên raw_text đã chuẩn hóa, có mở rộng ngữ cảnh bằng skill alias.",
                "bm25_weight": TEXT_BM25_WEIGHT,
                "tfidf_weight": TEXT_TFIDF_WEIGHT,
                "lexical_weight": TEXT_LEXICAL_WEIGHT,
                "skill_context_weight": TEXT_SKILL_CONTEXT_WEIGHT,
            },
        }

        score_explanation_items = _build_score_explanation_items(
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
        )
        explanation_payload = _build_match_explanation_payload(
            cv_profile=cv_profile,
            jd_profile=jd_profile,
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
            candidate_level_info=candidate_level_info,
            chi_tiet_diem=chi_tiet_diem,
            score_explanation_items=score_explanation_items,
            include_llm_explanation=include_llm_explanation,
        )

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
                **explanation_payload,
                "provider": explanation_payload.get("explanation_provider", "rule_based"),
                "score_explanation_items": score_explanation_items,
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

        normalized = _normalize_skill_name(str(skill_name))
        items.append(
            {
                "skill_name": canonical_skill_display_name(str(skill_name)),
                "normalized": normalized,
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

    if any(keyword in normalized for keyword in {"khong yeu cau kinh nghiem", "khong yeu cau", "no experience required"}):
        return 0.0

    month_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(thang|month|months|mo)\b", normalized)
    if month_match:
        return round(float(month_match.group(1).replace(",", ".")) / 12, 2)

    year_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(nam|year|years)\b", normalized)
    if year_match:
        return float(year_match.group(1).replace(",", "."))

    plain_number = re.fullmatch(r"\s*(\d+(?:[.,]\d+)?)\s*", normalized)
    if plain_number:
        return float(plain_number.group(1).replace(",", "."))

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

    cv_tokens = _build_context_similarity_terms(cv_text, cv_profile, "cv")
    jd_tokens = _build_context_similarity_terms(jd_text, jd_profile, "jd")

    if not cv_tokens or not jd_tokens:
        return 0.0

    bm25 = _normalized_bm25_similarity(cv_tokens, jd_tokens)
    tfidf = _tfidf_cosine_similarity(cv_tokens, jd_tokens)
    cosine = _cosine_similarity(cv_tokens, jd_tokens)
    jaccard = _jaccard_similarity(cv_tokens, jd_tokens)
    lexical = cosine * 0.7 + jaccard * 0.3
    skill_context = _skill_context_overlap_score(cv_profile, jd_profile, cv_text, jd_text)

    score = (
        bm25 * TEXT_BM25_WEIGHT
        + tfidf * TEXT_TFIDF_WEIGHT
        + lexical * TEXT_LEXICAL_WEIGHT
        + skill_context * TEXT_SKILL_CONTEXT_WEIGHT
    ) * 100
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


def _build_match_explanation_payload(
    *,
    cv_profile: dict,
    jd_profile: dict,
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
    candidate_level_info: dict,
    chi_tiet_diem: dict,
    score_explanation_items: list[dict],
    include_llm_explanation: bool = True,
) -> dict:
    fallback_explanation = _build_explanation(
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
    )

    if not include_llm_explanation:
        return {
            "explanation": fallback_explanation,
            "explanation_provider": "rule_based_batch",
        }

    provider = (settings.match_explanation_provider or "ollama").strip().lower()
    if provider not in {"ollama", "gemini", "template", "rule", "rules", "rule_based", "local"}:
        logger.warning("Unknown MATCH_EXPLANATION_PROVIDER=%s, fallback to ollama", settings.match_explanation_provider)
        provider = "ollama"

    if provider not in {"ollama", "gemini"}:
        return {
            "explanation": fallback_explanation,
            "explanation_provider": "rule_based",
        }

    context = {
        "candidate": {
            "profile_title": cv_profile.get("tieu_de_ho_so"),
            "years_experience": chi_tiet_diem.get("cv_years"),
            "years_experience_label": _format_year_duration(chi_tiet_diem.get("cv_years")),
            "education": cv_profile.get("trinh_do"),
            "skills": chi_tiet_diem.get("cv_skills"),
            "source": cv_profile.get("nguon_ho_so"),
        },
        "job": {
            "title": jd_profile.get("tieu_de") or jd_profile.get("title"),
            "level": level_info.get("level"),
            "required_years": chi_tiet_diem.get("jd_required_years"),
            "required_years_label": _format_year_duration(chi_tiet_diem.get("jd_required_years")),
            "education": jd_profile.get("trinh_do_yeu_cau"),
            "skills": chi_tiet_diem.get("jd_skills"),
        },
        "scores": {
            "overall": diem_phu_hop,
            "skill": score_explanation_items[0]["score"] if score_explanation_items else None,
            "experience": experience_score,
            "education": education_score,
            "text_similarity": text_similarity_score,
            "salary": salary_score,
            "location": location_score,
            "work_mode": work_mode_score,
            "weights": chi_tiet_diem.get("weights"),
        },
        "skill_match": {
            "matched": matched_skills,
            "missing": missing_skills,
            "near_matched": near_matched_skills,
        },
        "level_resolution": {
            "job": level_info,
            "candidate": candidate_level_info,
        },
        "score_explanation_items": score_explanation_items,
        "deterministic_explanation": fallback_explanation,
    }

    try:
        timeout_seconds = max(1.0, float(settings.ai_llm_fallback_seconds))
        logger.info(
            "Generating match explanation provider=%s timeout_seconds=%s",
            provider,
            timeout_seconds,
        )
        llm_payload = run_with_timeout(
            lambda: _generate_llm_match_explanation(context, provider),
            timeout_seconds,
        )
        return {
            "explanation": llm_payload["explanation"],
            "strengths": llm_payload["strengths"],
            "weaknesses": llm_payload["weaknesses"],
            "risks": llm_payload["risks"],
            "questions": llm_payload["questions"],
            "recommendation": llm_payload["recommendation"],
            "explanation_provider": provider,
            "explanation_model": settings.gemini_model if provider == "gemini" else settings.ollama_model,
        }
    except TimeoutError:
        logger.warning(
            "%s match explanation timed out after %.1fs, fallback to deterministic explanation.",
            provider,
            float(settings.ai_llm_fallback_seconds),
        )
        return {
            "explanation": fallback_explanation,
            "explanation_provider": "template_timeout_fallback",
            "explanation_error": f"{provider} quá {settings.ai_llm_fallback_seconds}s chưa phản hồi.",
        }
    except Exception as exc:
        logger.warning(
            "%s match explanation failed, fallback to deterministic explanation: %s",
            provider,
            exc,
        )
        return {
            "explanation": fallback_explanation,
            "explanation_provider": "rule_based_fallback",
            "explanation_error": str(exc),
        }


def _generate_llm_match_explanation(context: dict, provider: str) -> dict:
    if provider == "gemini":
        raw = generate_text(
            system_prompt=(
                "Bạn là trợ lý tuyển dụng viết giải thích so sánh CV-JD. "
                "Chỉ dùng dữ liệu JSON đầu vào, không bịa thêm kỹ năng, số năm, công ty, chứng chỉ hoặc thành tích. "
                "Điểm số đã được hệ thống tính sẵn, không tự tính lại và không thay đổi điểm. "
                "Viết tiếng Việt rõ ràng, trung lập, hữu ích cho HR. "
                "Chỉ trả về JSON hợp lệ, không markdown."
            ),
            user_prompt=_build_match_explanation_prompt(context),
            max_tokens=max(settings.match_explanation_max_tokens, 700),
            temperature=0,
            format_json=True,
        )
        return _normalize_llm_match_explanation(raw)

    raw = generate_ollama_text(
        _build_match_explanation_prompt(context),
        max_tokens=settings.match_explanation_max_tokens,
        temperature=0,
        top_p=0.8,
        num_ctx=max(settings.ollama_num_ctx, 3072),
        format_json=True,
        error_context="Ollama local cho match explanation",
    )

    return _normalize_llm_match_explanation(raw)


def _normalize_llm_match_explanation(raw: str) -> dict:
    payload = _parse_json_payload(raw)

    explanation = _replace_decimal_year_phrases(str(payload.get("explanation") or "").strip())
    strengths = [_replace_decimal_year_phrases(item) for item in _normalize_llm_list(payload.get("strengths"))]
    weaknesses = [_replace_decimal_year_phrases(item) for item in _normalize_llm_list(payload.get("weaknesses"))]
    risks = [_replace_decimal_year_phrases(item) for item in _normalize_llm_list(payload.get("risks"))]
    questions = [
        _replace_decimal_year_phrases(item)
        for item in _normalize_llm_list(payload.get("questions") or payload.get("interview_questions"))
    ]
    recommendation = _replace_decimal_year_phrases(str(payload.get("recommendation") or "").strip())

    if not explanation or not strengths or not weaknesses or not recommendation:
        raise RuntimeError("Ollama không trả về explanation/strengths/weaknesses/recommendation hợp lệ.")

    return {
        "explanation": explanation,
        "strengths": strengths[:4],
        "weaknesses": weaknesses[:4],
        "risks": (risks or ["Cần HR đọc CV chi tiết để xác nhận ngữ cảnh và mức độ đóng góp thực tế."])[:3],
        "questions": (questions or ["Ứng viên đã từng xử lý nhiệm vụ nào gần nhất với JD này và kết quả đo lường ra sao?"])[:4],
        "recommendation": recommendation,
    }


def _build_match_explanation_prompt(context: dict) -> str:
    schema = {
        "explanation": "Chuỗi 2-4 câu.",
        "strengths": ["Chuỗi điểm mạnh 1", "Chuỗi điểm mạnh 2"],
        "weaknesses": ["Chuỗi điểm thiếu/cần xác minh 1", "Chuỗi điểm thiếu/cần xác minh 2"],
        "risks": ["Chuỗi rủi ro hoặc dữ liệu chưa đủ"],
        "questions": ["Chuỗi câu hỏi phỏng vấn"],
        "recommendation": "Chuỗi khuyến nghị ngắn cho HR.",
    }
    return (
        "Bạn là trợ lý tuyển dụng viết giải thích so sánh CV-JD. "
        "Chỉ dùng dữ liệu JSON đầu vào, không bịa thêm kỹ năng, số năm, công ty, chứng chỉ hoặc thành tích. "
        "Điểm số đã được hệ thống tính sẵn, không tự tính lại và không thay đổi điểm. "
        "Viết tiếng Việt rõ ràng, trung lập, hữu ích cho HR. "
        "Chỉ trả về một JSON object hợp lệ, không markdown, không giải thích ngoài JSON.\n"
        "Hãy viết giải thích cho HR dựa trên dữ liệu sau.\n"
        "Quy tắc:\n"
        "- Không thay đổi điểm số và không thêm thông tin ngoài JSON.\n"
        "- Nếu dữ liệu thiếu, hãy nói cần xác minh thay vì suy đoán.\n"
        "- Nhắc rõ kỹ năng khớp/thiếu quan trọng, kinh nghiệm và yếu tố làm điểm tăng/giảm.\n"
        "- Khi nói về kinh nghiệm dưới 1 năm, dùng label tháng trong JSON, ví dụ 0.25 năm phải viết là 3 tháng; 0.5 năm phải viết là 6 tháng.\n"
        "- Tất cả key và string phải dùng dấu nháy kép.\n"
        "- Không dùng dấu phẩy cuối mảng/object.\n"
        "- Trả về đủ 6 key đúng tên: explanation, strengths, weaknesses, risks, questions, recommendation.\n"
        f"Schema: {json.dumps(schema, ensure_ascii=False)}\n"
        f"Dữ liệu: {json.dumps(context, ensure_ascii=False)}"
    )


def _parse_json_payload(raw: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise
        payload = json.loads(match.group(0))

    if not isinstance(payload, dict):
        raise RuntimeError("LLM trả về JSON không phải object.")

    return payload


def _normalize_llm_list(value: object) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if not isinstance(value, list):
        return []

    results = []
    for item in value:
        if isinstance(item, dict):
            text = item.get("text") or item.get("value") or item.get("label")
        else:
            text = item
        text = str(text or "").strip()
        if text:
            results.append(text)

    return results


def _format_year_duration(value) -> str | None:
    if not isinstance(value, (int, float)):
        return None

    years = float(value)
    if years < 0:
        return None
    if years == 0:
        return "0 năm"
    if years < 1:
        months = max(1, round(years * 12))
        return f"{months} tháng"

    formatted = f"{years:.2f}".rstrip("0").rstrip(".")
    return f"{formatted} năm"


def _replace_decimal_year_phrases(text: str) -> str:
    if not text:
        return text

    def repl(match: re.Match) -> str:
        value = float(match.group(1).replace(",", "."))
        label = _format_year_duration(value)
        return label or match.group(0)

    return re.sub(r"\b(0[.,]\d+)\s*năm\b", repl, text, flags=re.I)


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
            "message": "Đo mức độ liên quan nội dung bằng BM25/TF-IDF sau khi chuẩn hóa raw_text và mở rộng skill alias.",
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
    return canonicalize_skill_name(value)


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


def _build_context_similarity_terms(normalized_text: str, profile: dict, profile_type: str) -> list[str]:
    terms = _tokenize_for_similarity(normalized_text)
    detected_skills = _detect_skill_contexts(normalized_text)

    if profile_type == "cv":
        explicit_skills = {
            skill
            for skill in _extract_cv_skill_names(profile)
            if skill
        }
    else:
        explicit_skills = {
            item["normalized"]
            for item in _extract_jd_skill_items(profile)
            if item.get("normalized")
        }

    for skill_key in sorted(detected_skills | explicit_skills):
        terms.extend(_skill_similarity_terms(skill_key, repetitions=3))

    for skill_key in sorted(detected_skills):
        category = SKILL_LOOKUP.get(skill_key, {}).get("category")
        if category:
            terms.append(_term_key("domain", str(category)))

    return terms


def _detect_skill_contexts(normalized_text: str) -> set[str]:
    detected: set[str] = set()
    if not normalized_text:
        return detected

    for item in SKILL_CATALOG:
        canonical = canonicalize_skill_name(str(item.get("skill_name") or ""))
        aliases = [item.get("skill_name"), *item.get("aliases", [])]
        for alias in aliases:
            alias_text = normalize_search_text(str(alias or "")).strip()
            if not alias_text:
                continue

            pattern = r"(?<!\w)" + re.escape(alias_text) + r"(?!\w)"
            if re.search(pattern, normalized_text):
                detected.add(canonical)
                break

    return detected


def _skill_similarity_terms(skill_key: str, *, repetitions: int = 1) -> list[str]:
    if not skill_key:
        return []

    meta = SKILL_LOOKUP.get(skill_key, {})
    display_name = str(meta.get("skill_name") or skill_key)
    terms = [_term_key("skill", skill_key)] * repetitions
    terms.extend(_tokenize_for_similarity(normalize_search_text(display_name)))

    category = meta.get("category")
    if category:
        terms.append(_term_key("domain", str(category)))

    return terms


def _term_key(prefix: str, value: str) -> str:
    normalized = normalize_search_text(value).strip()
    key = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return f"{prefix}_{key}" if key else prefix


def _normalized_bm25_similarity(document_tokens: list[str], query_tokens: list[str]) -> float:
    corpus = [document_tokens, query_tokens]
    score = _bm25_score(document_tokens, query_tokens, corpus)
    ideal_score = _bm25_score(query_tokens, query_tokens, corpus)

    if ideal_score <= 0:
        return 0.0

    return min(score / ideal_score, 1.0)


def _bm25_score(document_tokens: list[str], query_tokens: list[str], corpus: list[list[str]]) -> float:
    doc_counter = Counter(document_tokens)
    query_counter = Counter(query_tokens)
    doc_len = len(document_tokens)
    avg_doc_len = sum(len(doc) for doc in corpus) / max(len(corpus), 1)
    corpus_sets = [set(doc) for doc in corpus]

    if not doc_len or not avg_doc_len:
        return 0.0

    score = 0.0
    for token, query_weight in query_counter.items():
        tf = doc_counter.get(token, 0)
        if not tf:
            continue

        doc_frequency = sum(1 for doc in corpus_sets if token in doc)
        idf = math.log(1 + (len(corpus) - doc_frequency + 0.5) / (doc_frequency + 0.5))
        denominator = tf + BM25_K1 * (1 - BM25_B + BM25_B * doc_len / avg_doc_len)
        score += idf * ((tf * (BM25_K1 + 1)) / denominator) * min(query_weight, 3)

    return score


def _tfidf_cosine_similarity(left_tokens: list[str], right_tokens: list[str]) -> float:
    documents = [left_tokens, right_tokens]
    left_vector = _tfidf_vector(left_tokens, documents)
    right_vector = _tfidf_vector(right_tokens, documents)
    common = set(left_vector) & set(right_vector)
    dot = sum(left_vector[token] * right_vector[token] for token in common)
    left_norm = sum(value * value for value in left_vector.values()) ** 0.5
    right_norm = sum(value * value for value in right_vector.values()) ** 0.5

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot / (left_norm * right_norm)


def _tfidf_vector(tokens: list[str], documents: list[list[str]]) -> dict[str, float]:
    counter = Counter(tokens)
    total = max(len(tokens), 1)
    document_sets = [set(document) for document in documents]
    vector = {}

    for token, count in counter.items():
        doc_frequency = sum(1 for document in document_sets if token in document)
        idf = math.log((len(documents) + 1) / (doc_frequency + 1)) + 1
        vector[token] = (count / total) * idf

    return vector


def _skill_context_overlap_score(cv_profile: dict, jd_profile: dict, cv_text: str, jd_text: str) -> float:
    cv_skills = set(_extract_cv_skill_names(cv_profile)) | _detect_skill_contexts(cv_text)
    jd_skills = {item["normalized"] for item in _extract_jd_skill_items(jd_profile)} | _detect_skill_contexts(jd_text)

    if not jd_skills:
        return 0.0

    exact_overlap = len(cv_skills & jd_skills) / len(jd_skills)
    category_overlap = _skill_category_overlap_score(cv_skills, jd_skills)
    return min(exact_overlap * 0.8 + category_overlap * 0.2, 1.0)


def _skill_category_overlap_score(cv_skills: set[str], jd_skills: set[str]) -> float:
    cv_categories = {
        SKILL_LOOKUP.get(skill, {}).get("category")
        for skill in cv_skills
        if SKILL_LOOKUP.get(skill, {}).get("category")
    }
    jd_categories = {
        SKILL_LOOKUP.get(skill, {}).get("category")
        for skill in jd_skills
        if SKILL_LOOKUP.get(skill, {}).get("category")
    }

    if not jd_categories:
        return 0.0

    return len(cv_categories & jd_categories) / len(jd_categories)


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
