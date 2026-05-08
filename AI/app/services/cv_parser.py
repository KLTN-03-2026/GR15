from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pdfplumber

from app.core.logger import get_logger
from app.services.skill_catalog import extract_skills_from_text, normalize_search_text


logger = get_logger(__name__)

PARSER_VERSION = "cv_parser_v2_layout_guarded"
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


def parse_cv(ho_so_id: int, file_path: str | None = None, raw_text: str | None = None) -> dict:
    logger.info("Parse CV for ho_so_id=%s file_path=%s has_raw_text=%s", ho_so_id, file_path, bool(raw_text))

    try:
        source_text = raw_text
        extraction_meta: dict = {
            "source": "raw_text" if raw_text else "file",
            "layout": "plain_text",
            "warnings": [],
            "page_count": None,
        }

        if source_text:
            normalized_text = _normalize_text(source_text)
        else:
            if not file_path:
                raise ValueError("Thiếu dữ liệu CV để phân tích.")
            resolved_path = _resolve_cv_path(file_path)
            source_text, extraction_meta = _extract_text_with_metadata(resolved_path)
            normalized_text = _normalize_text(source_text)

        if not normalized_text:
            raise ValueError("Không thể trích xuất nội dung từ CV.")

        parsed_email = _extract_email(normalized_text)
        parsed_phone = _extract_phone(normalized_text)
        parsed_name = _extract_name(normalized_text, parsed_email, parsed_phone)
        skill_contexts = _collect_skill_contexts(normalized_text)
        parsed_skills = _extract_skills(normalized_text, skill_contexts)
        parsed_experience = _extract_section_blocks(normalized_text, EXPERIENCE_SECTION_PATTERNS)
        parsed_education = _extract_section_blocks(normalized_text, EDUCATION_SECTION_PATTERNS)
        layout_analysis = _analyze_layout(normalized_text, extraction_meta)
        quality_warnings = _build_quality_warnings(
            normalized_text=normalized_text,
            parsed_email=parsed_email,
            parsed_phone=parsed_phone,
            parsed_name=parsed_name,
            parsed_skills=parsed_skills,
            parsed_experience=parsed_experience,
            parsed_education=parsed_education,
            layout_analysis=layout_analysis,
        )
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
                "layout_analysis_json": layout_analysis,
                "quality_warnings_json": quality_warnings,
                "review_required": bool(quality_warnings) or confidence_score < 0.78,
                "suggested_actions": _suggest_review_actions(quality_warnings, layout_analysis),
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
                "layout_analysis_json": {},
                "quality_warnings_json": [
                    {
                        "severity": "error",
                        "code": "cv_parse_failed",
                        "message": str(exc),
                    }
                ],
                "review_required": True,
                "suggested_actions": ["Tải lại CV dạng PDF/DOCX có text hoặc nhập hồ sơ bằng CV Builder."],
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


def _extract_text_with_metadata(path: Path) -> tuple[str, dict]:
    suffix = path.suffix.lower()
    metadata = {
        "source": "file",
        "file_type": suffix.lstrip("."),
        "layout": "plain_text",
        "warnings": [],
        "page_count": None,
        "two_column_pages": [],
    }

    if suffix == ".pdf":
        pages: list[str] = []
        with pdfplumber.open(path) as pdf:
            metadata["page_count"] = len(pdf.pages)
            for page_index, page in enumerate(pdf.pages, start=1):
                page_text, page_meta = _extract_pdf_page_text(page)
                if page_meta.get("two_column"):
                    metadata["layout"] = "two_column_or_complex"
                    metadata["two_column_pages"].append(page_index)
                if page_text.strip():
                    pages.append(page_text)
        if not pages:
            metadata["warnings"].append("Không trích xuất được text từ PDF; CV có thể là file scan/ảnh và cần OCR.")
        return "\n".join(pages), metadata

    if suffix == ".docx":
        return _extract_docx_text(path), metadata

    if suffix == ".doc":
        metadata["warnings"].append("File DOC cũ có thể làm mất định dạng bảng/cột; nên kiểm tra lại kết quả parse.")
        return _extract_legacy_doc_text(path), metadata

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore"), metadata

    raise ValueError(f"Định dạng file chưa được hỗ trợ: {suffix}")


def _extract_pdf_page_text(page) -> tuple[str, dict]:
    page_text = page.extract_text() or ""
    meta = {"two_column": False}

    try:
        words = page.extract_words(x_tolerance=2, y_tolerance=3, keep_blank_chars=False)
    except Exception:
        return page_text, meta

    if not words:
        return page_text, meta

    width = float(getattr(page, "width", 0) or 0)
    if width <= 0:
        return page_text, meta

    left_words = [word for word in words if float(word.get("x0", 0)) < width * 0.47]
    right_words = [word for word in words if float(word.get("x0", 0)) > width * 0.53]
    has_two_columns = len(left_words) >= 12 and len(right_words) >= 12 and min(len(left_words), len(right_words)) / max(len(words), 1) >= 0.22

    if not has_two_columns:
        return page_text, meta

    meta["two_column"] = True

    def materialize(column_words: list[dict]) -> str:
        rows: list[list[dict]] = []
        for word in sorted(column_words, key=lambda item: (round(float(item.get("top", 0)) / 4), float(item.get("x0", 0)))):
            top = float(word.get("top", 0))
            if not rows or abs(float(rows[-1][0].get("top", 0)) - top) > 5:
                rows.append([word])
            else:
                rows[-1].append(word)

        lines = []
        for row in rows:
            lines.append(" ".join(str(item.get("text", "")).strip() for item in sorted(row, key=lambda item: float(item.get("x0", 0))) if str(item.get("text", "")).strip()))
        return "\n".join(line for line in lines if line.strip())

    column_text = "\n".join(part for part in [materialize(left_words), materialize(right_words)] if part.strip())
    return column_text or page_text, meta


def _extract_docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as docx:
            document_xml = docx.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise ValueError("File DOCX không hợp lệ hoặc không đọc được nội dung.") from exc

    root = ET.fromstring(document_xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []

    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)

    return "\n".join(paragraphs)


def _extract_legacy_doc_text(path: Path) -> str:
    raw = path.read_bytes()
    decoded_candidates = [
        raw.decode("utf-8", errors="ignore"),
        raw.decode("utf-16le", errors="ignore"),
        raw.decode("latin-1", errors="ignore"),
    ]

    best_text = ""
    best_score = 0

    for decoded in decoded_candidates:
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]+", "\n", decoded)
        chunks = re.findall(r"[A-Za-zÀ-ỹ0-9@._%+\-/(),:; ]{3,}", cleaned)
        text = "\n".join(chunk.strip() for chunk in chunks if chunk.strip())
        score = len(text)

        if "@" in text:
            score += 500
        if re.search(r"(?i)\b(cv|resume|experience|education|skills|kinh nghiem|hoc van|ky nang)\b", text):
            score += 500

        if score > best_score:
            best_score = score
            best_text = text

    return best_text


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


def _analyze_layout(text: str, extraction_meta: dict) -> dict:
    lines = text.splitlines()
    line_lengths = [len(line) for line in lines if line.strip()]
    short_line_ratio = (
        len([length for length in line_lengths if length <= 24]) / len(line_lengths)
        if line_lengths
        else 0
    )
    section_hits = sum(
        1
        for line in lines
        if _looks_like_new_section(normalize_search_text(line))
    )
    two_column_pages = extraction_meta.get("two_column_pages") or []
    complexity_score = 0

    if two_column_pages:
        complexity_score += 45
    if short_line_ratio >= 0.5 and len(lines) >= 20:
        complexity_score += 25
    if section_hits >= 7:
        complexity_score += 15
    if extraction_meta.get("warnings"):
        complexity_score += 15

    complexity_score = min(100, complexity_score)

    return {
        "layout": extraction_meta.get("layout") or "plain_text",
        "is_complex_layout": complexity_score >= 45,
        "complexity_score": complexity_score,
        "two_column_pages": two_column_pages,
        "page_count": extraction_meta.get("page_count"),
        "short_line_ratio": round(short_line_ratio, 2),
        "section_signal_count": section_hits,
        "extraction_warnings": extraction_meta.get("warnings") or [],
    }


def _build_quality_warnings(
    *,
    normalized_text: str,
    parsed_email: str | None,
    parsed_phone: str | None,
    parsed_name: str | None,
    parsed_skills: list[dict],
    parsed_experience: list[dict],
    parsed_education: list[dict],
    layout_analysis: dict,
) -> list[dict]:
    warnings: list[dict] = []

    if len(normalized_text) < 220:
        warnings.append({
            "severity": "warning",
            "code": "cv_text_too_short",
            "message": "Nội dung trích xuất từ CV còn ngắn; nếu đây là CV scan/ảnh, nên dùng file có text hoặc OCR.",
        })
    if layout_analysis.get("is_complex_layout"):
        warnings.append({
            "severity": "info",
            "code": "cv_complex_layout_detected",
            "message": "CV có dấu hiệu layout nhiều cột hoặc thiết kế phức tạp; hãy kiểm tra lại thứ tự kinh nghiệm, học vấn và kỹ năng.",
        })
    if not parsed_name:
        warnings.append({"severity": "warning", "code": "missing_name", "message": "Chưa nhận diện chắc chắn họ tên ứng viên."})
    if not parsed_email:
        warnings.append({"severity": "warning", "code": "missing_email", "message": "Chưa nhận diện được email trong CV."})
    if not parsed_phone:
        warnings.append({"severity": "info", "code": "missing_phone", "message": "Chưa nhận diện được số điện thoại hợp lệ."})
    if len(parsed_skills) < 3:
        warnings.append({"severity": "warning", "code": "few_skills", "message": "Số kỹ năng nhận diện còn ít; nên rà soát và bổ sung kỹ năng thủ công nếu cần."})
    if not parsed_experience:
        warnings.append({"severity": "info", "code": "missing_experience", "message": "Chưa tách được khối kinh nghiệm làm việc rõ ràng."})
    if not parsed_education:
        warnings.append({"severity": "info", "code": "missing_education", "message": "Chưa tách được khối học vấn rõ ràng."})

    return warnings


def _suggest_review_actions(warnings: list[dict], layout_analysis: dict) -> list[str]:
    actions = []
    codes = {item.get("code") for item in warnings}

    if "cv_complex_layout_detected" in codes:
        actions.append("Kiểm tra lại thứ tự nội dung vì CV có thể là layout 2 cột hoặc thiết kế phức tạp.")
    if {"missing_name", "missing_email", "missing_phone"} & codes:
        actions.append("Xác nhận lại thông tin cá nhân trước khi áp dụng vào tài khoản.")
    if "few_skills" in codes:
        actions.append("Mở mục Kỹ năng của tôi để bổ sung kỹ năng quan trọng chưa được AI nhận diện.")
    if "cv_text_too_short" in codes:
        actions.append("Nếu CV là ảnh/scan, hãy dùng bản PDF/DOCX có thể copy text để parse chính xác hơn.")

    if not actions:
        actions.append("Kết quả parse đủ tốt; chỉ cần rà soát nhanh trước khi dùng cho matching.")

    return actions[:4]
