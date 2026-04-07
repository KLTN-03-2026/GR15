from __future__ import annotations

import re

from app.core.logger import get_logger
from app.services.skill_catalog import extract_skills_from_text, normalize_search_text


logger = get_logger(__name__)

PARSER_VERSION = "jd_parser_v1"
SECTION_SCAN_LIMIT = 28

REQUIREMENT_MARKERS = (
    "yeu cau",
    "requirements",
    "qualifications",
    "what we expect",
    "ki nang yeu cau",
)

BENEFIT_MARKERS = (
    "quyen loi",
    "benefits",
    "che do",
    "phuc loi",
    "what we offer",
)

LOCATION_KEYWORDS = (
    "ha noi",
    "hanoi",
    "ho chi minh",
    "tp hcm",
    "hcm",
    "da nang",
    "can tho",
    "hai phong",
    "remote",
    "hybrid",
    "onsite",
)


def parse_jd(tin_tuyen_dung_id: int, job_text: str) -> dict:
    logger.info("Parse JD for tin_tuyen_dung_id=%s", tin_tuyen_dung_id)

    try:
        normalized_text = _normalize_text(job_text)
        if not normalized_text:
            raise ValueError("Nội dung JD trống.")

        section_contexts = {
            "header": "\n".join(normalized_text.splitlines()[:8]),
            "requirements": _join_section_contents(_extract_section_blocks(normalized_text, REQUIREMENT_MARKERS)),
            "benefits": _join_section_contents(_extract_section_blocks(normalized_text, BENEFIT_MARKERS)),
            "general": normalized_text,
        }
        parsed_skills = _extract_skills(normalized_text, section_contexts)
        parsed_requirements = _extract_section_blocks(normalized_text, REQUIREMENT_MARKERS)
        parsed_benefits = _extract_section_blocks(normalized_text, BENEFIT_MARKERS)
        parsed_salary = _extract_salary(normalized_text)
        parsed_location = _extract_location(normalized_text)
        confidence_score = _estimate_confidence(
            normalized_text=normalized_text,
            parsed_skills=parsed_skills,
            parsed_requirements=parsed_requirements,
            parsed_benefits=parsed_benefits,
            parsed_salary=parsed_salary,
            parsed_location=parsed_location,
        )

        return {
            "success": True,
            "parser_version": PARSER_VERSION,
            "confidence_score": confidence_score,
            "data": {
                "raw_text": normalized_text,
                "parsed_skills_json": parsed_skills,
                "parsed_requirements_json": parsed_requirements,
                "parsed_benefits_json": parsed_benefits,
                "parsed_salary_json": parsed_salary,
                "parsed_location_json": parsed_location,
            },
            "error": None,
        }
    except Exception as exc:
        logger.exception("JD parser failed for tin_tuyen_dung_id=%s", tin_tuyen_dung_id)
        return {
            "success": False,
            "parser_version": PARSER_VERSION,
            "confidence_score": 0.0,
            "data": {
                "raw_text": job_text,
                "parsed_skills_json": [],
                "parsed_requirements_json": [],
                "parsed_benefits_json": [],
                "parsed_salary_json": {},
                "parsed_location_json": {},
            },
            "error": str(exc),
        }


def _normalize_text(text: str) -> str:
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def _extract_skills(text: str, section_contexts: dict[str, str]) -> list[dict]:
    results = extract_skills_from_text(text, section_contexts=section_contexts)
    for item in results:
        required = _is_required_skill(text, item["matched_text"])
        item["bat_buoc"] = required
        item["muc_do_yeu_cau"] = 3 if required else 2
        item["trong_so"] = 1.5 if required else 1.0
        item["do_tin_cay"] = item.pop("confidence")
    return results


def _is_required_skill(text: str, alias: str) -> bool:
    patterns = (
        rf"(yeu cau|bat buoc|must have|required)[^.:\n]{{0,80}}{re.escape(alias)}",
        rf"{re.escape(alias)}[^.:\n]{{0,80}}(yeu cau|bat buoc|required)",
    )
    searchable = normalize_search_text(text)
    return any(re.search(pattern, searchable) for pattern in patterns)


def _extract_section_blocks(text: str, markers: tuple[str, ...]) -> list[dict]:
    lines = text.splitlines()
    results = []

    for index, line in enumerate(lines):
        normalized_line = normalize_search_text(line)
        if not any(marker in normalized_line for marker in markers):
            continue

        section_lines = []
        for next_line in lines[index + 1:index + 1 + SECTION_SCAN_LIMIT]:
            if _looks_like_new_section(normalize_search_text(next_line)):
                break
            section_lines.append(next_line)

        content = "\n".join(section_lines).strip()
        if content:
            results.append(
                {
                    "section_title": line,
                    "content": content,
                }
            )

    return results


def _looks_like_new_section(line: str) -> bool:
    markers = REQUIREMENT_MARKERS + BENEFIT_MARKERS + (
        "mo ta cong viec",
        "job description",
        "dia diem",
        "muc luong",
        "salary",
        "thoi gian lam viec",
    )
    return any(marker in line for marker in markers)


def _extract_salary(text: str) -> dict:
    matches = re.findall(r"(\d+(?:[.,]\d+)?)\s*(trieu|triệu|million|m)\+?", text.lower())
    if not matches:
        return {}

    values = []
    for number, unit in matches:
        numeric = float(number.replace(",", "."))
        if unit in {"m", "million", "trieu", "triệu"}:
            values.append(int(numeric * 1_000_000))

    if not values:
        return {}

    return {
        "muc_luong_tu": min(values),
        "muc_luong_den": max(values),
        "don_vi_luong": "VND",
        "raw_matches": [f"{number} {unit}" for number, unit in matches],
    }


def _extract_location(text: str) -> dict:
    normalized = normalize_search_text(text)
    found_locations = []

    for keyword in LOCATION_KEYWORDS:
        keyword_search = normalize_search_text(keyword)
        if keyword_search in normalized:
            found_locations.append(keyword)

    unique_locations = []
    for location in found_locations:
        if location not in unique_locations:
            unique_locations.append(location)

    if not unique_locations:
        return {}

    return {
        "locations": unique_locations,
        "work_mode": _detect_work_mode(normalized),
    }


def _detect_work_mode(normalized_text: str) -> str | None:
    if "remote" in normalized_text:
        return "remote"
    if "hybrid" in normalized_text:
        return "hybrid"
    if "onsite" in normalized_text:
        return "onsite"
    return None


def _estimate_confidence(
    *,
    normalized_text: str,
    parsed_skills: list[dict],
    parsed_requirements: list[dict],
    parsed_benefits: list[dict],
    parsed_salary: dict,
    parsed_location: dict,
) -> float:
    score = 0.45

    if len(normalized_text) > 200:
        score += 0.12
    if parsed_skills:
        score += min(0.1 + len(parsed_skills) * 0.01, 0.16)
    if parsed_requirements:
        score += 0.1
    if parsed_benefits:
        score += 0.08
    if parsed_salary:
        score += 0.06
    if parsed_location:
        score += 0.05

    return round(min(score, 0.99), 2)

def _join_section_contents(blocks: list[dict]) -> str:
    return "\n".join(block.get("content", "") for block in blocks if block.get("content"))
