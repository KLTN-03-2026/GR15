from __future__ import annotations

import re
from pathlib import Path

import pdfplumber

from app.core.logger import get_logger
from app.services.skill_catalog import extract_skills_from_text, normalize_search_text


logger = get_logger(__name__)

PARSER_VERSION = "cv_parser_v1"
SECTION_SCAN_LIMIT = 24

NAME_BLOCKLIST = {
    "cv",
    "resume",
    "curriculum vitae",
    "ho so",
    "so dien thoai",
    "dien thoai",
    "email",
    "linkedin",
    "github",
    "kinh nghiem",
    "experience",
    "hoc van",
    "education",
    "ky nang",
    "skills",
    "technical skills",
}

EXPERIENCE_SECTION_PATTERNS = (
    r"kinh\s*nghiem",
    r"experience",
    r"work\s*history",
    r"employment",
)

EDUCATION_SECTION_PATTERNS = (
    r"hoc\s*van",
    r"education",
    r"bang\s*cap",
    r"truong",
)

SKILL_SECTION_PATTERNS = (
    r"ky\s*nang",
    r"skills",
    r"technical\s*skills",
    r"cong\s*nghe",
    r"tool",
)

PROJECT_SECTION_PATTERNS = (
    r"du\s*an",
    r"projects",
    r"project\s*experience",
    r"san\s*pham",
)

CERTIFICATION_SECTION_PATTERNS = (
    r"chung\s*chi",
    r"certifications?",
    r"licenses?",
)


def parse_cv(ho_so_id: int, file_path: str) -> dict:
    logger.info("Parse CV for ho_so_id=%s file_path=%s", ho_so_id, file_path)

    try:
        resolved_path = _resolve_cv_path(file_path)
        raw_text = _extract_text(resolved_path)
        normalized_text = _normalize_text(raw_text)

        if not normalized_text:
            raise ValueError("Không thể trích xuất nội dung từ CV.")

        parsed_email = _extract_email(normalized_text)
        parsed_phone = _extract_phone(normalized_text)
        parsed_name = _extract_name(normalized_text, parsed_email, parsed_phone)
        skill_contexts = _collect_skill_contexts(normalized_text)
        parsed_skills = _extract_skills(normalized_text, skill_contexts)
        parsed_experience = _extract_section_blocks(normalized_text, EXPERIENCE_SECTION_PATTERNS)
        parsed_education = _extract_section_blocks(normalized_text, EDUCATION_SECTION_PATTERNS)
        confidence_score = _estimate_confidence(
            normalized_text=normalized_text,
            parsed_email=parsed_email,
            parsed_phone=parsed_phone,
            parsed_name=parsed_name,
            parsed_skills=parsed_skills,
            parsed_experience=parsed_experience,
            parsed_education=parsed_education,
        )

        return {
            "success": True,
            "parser_version": PARSER_VERSION,
            "confidence_score": confidence_score,
            "data": {
                "raw_text": normalized_text,
                "parsed_name": parsed_name,
                "parsed_email": parsed_email,
                "parsed_phone": parsed_phone,
                "parsed_skills_json": parsed_skills,
                "parsed_experience_json": parsed_experience,
                "parsed_education_json": parsed_education,
            },
            "error": None,
        }
    except Exception as exc:
        logger.exception("CV parser failed for ho_so_id=%s", ho_so_id)
        return {
            "success": False,
            "parser_version": PARSER_VERSION,
            "confidence_score": 0.0,
            "data": {
                "raw_text": None,
                "parsed_name": None,
                "parsed_email": None,
                "parsed_phone": None,
                "parsed_skills_json": [],
                "parsed_experience_json": [],
                "parsed_education_json": [],
            },
            "error": str(exc),
        }


def _resolve_cv_path(file_path: str) -> Path:
    raw_path = Path(file_path)
    project_root = Path(__file__).resolve().parents[3]
    candidates = []

    if raw_path.is_absolute():
        candidates.append(raw_path)
    else:
        candidates.extend(
            [
                Path.cwd() / raw_path,
                project_root / raw_path,
                project_root / "AI" / raw_path,
                project_root / "BE" / raw_path,
                project_root / "BE" / "storage" / "app" / "public" / raw_path,
                project_root / "BE" / "storage" / "app" / raw_path,
            ]
        )

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()

    raise FileNotFoundError(f"Không tìm thấy file CV: {file_path}")


def _extract_text(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        pages: list[str] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    pages.append(page_text)
        return "\n".join(pages)

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError(f"Định dạng file chưa được hỗ trợ: {suffix}")


def _normalize_text(text: str) -> str:
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def _extract_email(text: str) -> str | None:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> str | None:
    match = re.search(r"(?:(?:\+?84)|0)(?:[\s.\-]?\d){8,10}", text)
    if not match:
        return None
    digits = re.sub(r"\D", "", match.group(0))
    if digits.startswith("84") and not digits.startswith("084"):
        digits = "0" + digits[2:]
    return digits


def _extract_name(text: str, parsed_email: str | None, parsed_phone: str | None) -> str | None:
    for line in text.splitlines()[:10]:
        cleaned = line.strip(" -|:,")
        if not cleaned:
            continue

        lowered = normalize_search_text(cleaned)
        if any(token in lowered for token in NAME_BLOCKLIST):
            continue
        if parsed_email and parsed_email.lower() in lowered:
            continue
        if parsed_phone and parsed_phone in re.sub(r"\D", "", cleaned):
            continue
        if len(cleaned) < 4 or len(cleaned) > 60:
            continue
        if re.search(r"\d", cleaned):
            continue

        words = [word for word in cleaned.split() if word]
        if 2 <= len(words) <= 6:
            return cleaned.title()

    return None


def _extract_skills(text: str, section_contexts: dict[str, str]) -> list[dict]:
    return extract_skills_from_text(text, section_contexts=section_contexts)


def _collect_skill_contexts(text: str) -> dict[str, str]:
    lines = text.splitlines()
    return {
        "header": "\n".join(lines[:10]),
        "skills": _join_section_contents(_extract_section_blocks(text, SKILL_SECTION_PATTERNS)),
        "experience": _join_section_contents(_extract_section_blocks(text, EXPERIENCE_SECTION_PATTERNS)),
        "projects": _join_section_contents(_extract_section_blocks(text, PROJECT_SECTION_PATTERNS)),
        "education": _join_section_contents(_extract_section_blocks(text, EDUCATION_SECTION_PATTERNS)),
        "certifications": _join_section_contents(_extract_section_blocks(text, CERTIFICATION_SECTION_PATTERNS)),
        "general": text,
    }


def _extract_section_blocks(text: str, patterns: tuple[str, ...]) -> list[dict]:
    lines = text.splitlines()
    results = []

    for index, line in enumerate(lines):
        lowered = normalize_search_text(line)
        if not any(re.search(pattern, lowered) for pattern in patterns):
            continue

        section_lines = []
        for next_line in lines[index + 1:index + 1 + SECTION_SCAN_LIMIT]:
            next_lowered = normalize_search_text(next_line)
            if _looks_like_new_section(next_lowered):
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
    section_markers = (
        "kinh nghiem",
        "experience",
        "hoc van",
        "education",
        "ky nang",
        "skills",
        "technical skills",
        "cong nghe",
        "tools",
        "du an",
        "projects",
        "chung chi",
        "certificates",
        "hoat dong",
        "activities",
        "muc tieu",
        "objective",
        "thong tin lien he",
        "contact",
    )
    return any(marker in line for marker in section_markers)


def _estimate_confidence(
    *,
    normalized_text: str,
    parsed_email: str | None,
    parsed_phone: str | None,
    parsed_name: str | None,
    parsed_skills: list[dict],
    parsed_experience: list[dict],
    parsed_education: list[dict],
) -> float:
    score = 0.45

    if len(normalized_text) > 300:
        score += 0.15
    if parsed_email:
        score += 0.1
    if parsed_phone:
        score += 0.1
    if parsed_name:
        score += 0.08
    if parsed_skills:
        score += min(0.08 + len(parsed_skills) * 0.01, 0.12)
    if parsed_experience:
        score += 0.08
    if parsed_education:
        score += 0.07

    return round(min(score, 0.99), 2)


def _join_section_contents(blocks: list[dict]) -> str:
    return "\n".join(block.get("content", "") for block in blocks if block.get("content"))
