from __future__ import annotations

from collections import Counter
import re
from difflib import SequenceMatcher

from app.core.logger import get_logger
from app.services.skill_catalog import SKILL_CATALOG, normalize_search_text


logger = get_logger(__name__)

MODEL_VERSION = "matching_v3_dynamic_weights"

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
        "skill": 0.4,
        "experience": 0.1,
        "education": 0.2,
        "text_similarity": 0.3,
    },
    "fresher": {
        "skill": 0.42,
        "experience": 0.13,
        "education": 0.15,
        "text_similarity": 0.3,
    },
    "junior": {
        "skill": 0.43,
        "experience": 0.2,
        "education": 0.1,
        "text_similarity": 0.27,
    },
    "mid": {
        "skill": 0.38,
        "experience": 0.32,
        "education": 0.08,
        "text_similarity": 0.22,
    },
    "senior": {
        "skill": 0.3,
        "experience": 0.42,
        "education": 0.06,
        "text_similarity": 0.22,
    },
    "lead_manager": {
        "skill": 0.25,
        "experience": 0.48,
        "education": 0.07,
        "text_similarity": 0.2,
    },
    "default": {
        "skill": 0.4,
        "experience": 0.3,
        "education": 0.1,
        "text_similarity": 0.2,
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
            (text_similarity_score * weights["text_similarity"]),
            2,
        )

        chi_tiet_diem = {
            "skill_score": round(skill_score, 2),
            "exact_skill_score": round(exact_skill_score, 2),
            "semantic_skill_score": round(semantic_skill_score, 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "text_similarity_score": round(text_similarity_score, 2),
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
        }

        return {
            "success": True,
            "model_version": MODEL_VERSION,
            "data": {
                "diem_phu_hop": diem_phu_hop,
                "diem_ky_nang": round(skill_score, 2),
                "diem_kinh_nghiem": round(experience_score, 2),
                "diem_hoc_van": round(education_score, 2),
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
                    level_info=level_info,
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
                "chi_tiet_diem": {},
                "matched_skills_json": [],
                "missing_skills_json": [],
                "danh_sach_ky_nang_thieu": None,
                "explanation": None,
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


def _build_explanation(
    *,
    diem_phu_hop: float,
    matched_skills: list[dict],
    missing_skills: list[dict],
    near_matched_skills: list[dict],
    experience_score: float,
    education_score: float,
    text_similarity_score: float,
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
        f"và điểm tương đồng nội dung CV-JD đạt {round(text_similarity_score, 2)}/100. "
        f"Bộ trọng số được áp dụng theo nhóm cấp bậc {level_info['level']}."
    )

    if near_names:
        explanation += f" Hệ thống cũng nhận diện các kỹ năng gần nghĩa/gần vai trò: {near_names}."

    return explanation


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
