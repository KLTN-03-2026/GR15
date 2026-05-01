from __future__ import annotations

from app.core.config import settings
from app.core.logger import get_logger
from app.providers import (
    CoverLetterContext,
    OllamaCoverLetterProvider,
    OpenAICoverLetterProvider,
    TemplateCoverLetterProvider,
)


logger = get_logger(__name__)

MODEL_VERSION = f"cover_letter::{settings.cover_letter_provider}"


def generate_cover_letter(
    ho_so_id: int,
    tin_tuyen_dung_id: int,
    *,
    cv_profile: dict | None = None,
    jd_profile: dict | None = None,
    matching_profile: dict | None = None,
) -> dict:
    logger.info(
        "Generate cover letter ho_so_id=%s tin_tuyen_dung_id=%s model=%s",
        ho_so_id,
        tin_tuyen_dung_id,
        settings.local_llm_model,
    )

    try:
        context = _build_context(
            cv_profile=cv_profile or {},
            jd_profile=jd_profile or {},
            matching_profile=matching_profile or {},
        )
        provider = _resolve_provider()
        content = _finalize_cover_letter(provider.generate(context))

        if not content:
            raise RuntimeError("Provider không trả về nội dung thư xin việc.")

        return {
            "success": True,
            "model_version": MODEL_VERSION,
            "data": {
                "thu_xin_viec_ai": content,
                "model_version": MODEL_VERSION,
                "meta": {
                    "candidate_name": context.candidate_name,
                    "job_title": context.job_title,
                    "company_name": context.company_name,
                    "featured_skills": context.featured_skills,
                    "missing_skills": context.missing_skills[:4],
                    "diem_phu_hop": context.matching_score,
                    "provider": _resolve_provider_name(),
                },
            },
            "error": None,
        }
    except Exception as exc:
        logger.exception(
            "Cover letter generation failed for ho_so_id=%s tin_tuyen_dung_id=%s",
            ho_so_id,
            tin_tuyen_dung_id,
        )
        return {
            "success": False,
            "model_version": MODEL_VERSION,
            "data": {
                "thu_xin_viec_ai": None,
                "model_version": MODEL_VERSION,
                "meta": {},
            },
            "error": str(exc),
        }


def _build_context(*, cv_profile: dict, jd_profile: dict, matching_profile: dict) -> CoverLetterContext:
    ung_vien_ten = _extract_candidate_name(cv_profile)
    vi_tri = jd_profile.get("tieu_de") or "vị trí đang tuyển"
    cong_ty = jd_profile.get("ten_cong_ty") or "Quý công ty"

    matched_skills = _extract_skill_names(matching_profile.get("matched_skills_json"))
    missing_skills = _extract_skill_names(matching_profile.get("missing_skills_json"))
    cv_skills = _extract_skill_names(cv_profile.get("parsed_skills"))
    jd_skills = _extract_skill_names(jd_profile.get("required_skills") or jd_profile.get("parsed_skills"))

    featured_skills = matched_skills[:3] or cv_skills[:3]
    job_focus_skills = jd_skills[:4]
    kinh_nghiem = _extract_experience_summary(cv_profile)
    diem_phu_hop = matching_profile.get("diem_phu_hop")
    explanation = matching_profile.get("explanation")
    tone = _determine_tone(diem_phu_hop)

    return CoverLetterContext(
        candidate_name=ung_vien_ten,
        job_title=vi_tri,
        company_name=cong_ty,
        tone=tone,
        candidate_title=cv_profile.get("tieu_de_ho_so"),
        career_goal=cv_profile.get("muc_tieu_nghe_nghiep"),
        education_level=cv_profile.get("trinh_do"),
        years_experience=cv_profile.get("kinh_nghiem_nam"),
        job_level=jd_profile.get("cap_bac"),
        required_experience=jd_profile.get("kinh_nghiem_yeu_cau"),
        required_education=jd_profile.get("trinh_do_yeu_cau"),
        featured_skills=featured_skills,
        job_focus_skills=job_focus_skills,
        missing_skills=missing_skills,
        candidate_evidence=_extract_candidate_evidence(cv_profile),
        job_evidence=_extract_job_evidence(jd_profile),
        experience_summary=kinh_nghiem,
        matching_score=diem_phu_hop,
        matching_explanation=explanation,
        score_breakdown={
            "diem_ky_nang": matching_profile.get("diem_ky_nang"),
            "diem_kinh_nghiem": matching_profile.get("diem_kinh_nghiem"),
            "diem_hoc_van": matching_profile.get("diem_hoc_van"),
            "chi_tiet_diem": matching_profile.get("chi_tiet_diem") or {},
        },
    )


def _resolve_provider():
    provider_name = _resolve_provider_name()
    if provider_name == "ollama":
        return OllamaCoverLetterProvider()
    if provider_name == "openai":
        return OpenAICoverLetterProvider()
    if provider_name in {"template", "rule", "rules"}:
        return TemplateCoverLetterProvider()

    logger.warning("Unknown COVER_LETTER_PROVIDER=%s, fallback to ollama LLM provider", settings.cover_letter_provider)
    return OllamaCoverLetterProvider()


def _resolve_provider_name() -> str:
    provider_name = (settings.cover_letter_provider or "ollama").lower().strip()
    if provider_name in {"", "llm"}:
        return "ollama"
    return provider_name


def _extract_candidate_name(cv_profile: dict) -> str:
    return (
        cv_profile.get("parsed_name")
        or cv_profile.get("ho_ten")
        or cv_profile.get("tieu_de_ho_so")
        or "Ứng viên"
    )


def _extract_skill_names(items: list | None) -> list[str]:
    if not items:
        return []

    names = []
    for item in items:
        if isinstance(item, dict):
            name = item.get("skill_name") or item.get("ten_ky_nang") or item.get("name")
        else:
            name = item

        if not name:
            continue

        normalized = str(name).strip()
        if normalized and normalized not in names:
            names.append(normalized)

    return names


def _extract_experience_summary(cv_profile: dict) -> str:
    kinh_nghiem_nam = cv_profile.get("kinh_nghiem_nam")
    if isinstance(kinh_nghiem_nam, (int, float)):
        if kinh_nghiem_nam <= 0:
            return "Tôi đang trong giai đoạn tích lũy kinh nghiệm thực tế và luôn sẵn sàng học hỏi nhanh để đáp ứng yêu cầu công việc."
        return f"Tôi đã có khoảng {kinh_nghiem_nam:g} năm kinh nghiệm liên quan."

    parsed_experience = cv_profile.get("parsed_experience") or []
    if parsed_experience:
        return "Tôi đã tham gia các dự án và công việc có liên quan trực tiếp đến vị trí ứng tuyển."

    return "Tôi đã có sự chuẩn bị nền tảng phù hợp cho vị trí này."


def _extract_candidate_evidence(cv_profile: dict) -> list[str]:
    evidence: list[str] = []

    for source_key in ["builder_experience", "parsed_experience", "builder_projects", "builder_certificates"]:
        items = cv_profile.get(source_key) or []
        for item in items[:3]:
            if isinstance(item, dict):
                value = (
                    item.get("title")
                    or item.get("ten_du_an")
                    or item.get("vi_tri")
                    or item.get("company")
                    or item.get("mo_ta")
                    or item.get("description")
                    or item.get("name")
                )
            else:
                value = item

            value = str(value or "").strip()
            if value and value not in evidence:
                evidence.append(value)

    career_goal = str(cv_profile.get("muc_tieu_nghe_nghiep") or "").strip()
    if career_goal and career_goal not in evidence:
        evidence.append(career_goal[:240])

    return evidence[:8]


def _extract_job_evidence(jd_profile: dict) -> list[str]:
    evidence: list[str] = []

    for key in ["cap_bac", "kinh_nghiem_yeu_cau", "trinh_do_yeu_cau"]:
        value = str(jd_profile.get(key) or "").strip()
        if value and value not in evidence:
            evidence.append(value)

    raw_text = str(jd_profile.get("raw_text") or "").strip()
    if raw_text:
        evidence.append(raw_text[:360])

    return evidence[:5]


def _determine_tone(diem_phu_hop: float | None) -> str:
    if diem_phu_hop is None:
        return "neutral"
    if diem_phu_hop >= 80:
        return "strong"
    if diem_phu_hop >= 60:
        return "balanced"
    return "growth"


def _finalize_cover_letter(text: str) -> str:
    cleaned = (
        str(text or "")
        .replace("**", "")
        .replace("__", "")
        .replace("`", "")
        .replace("#", "")
        .strip()
    )

    replacements = {
        "cover letter": "thư xin việc",
        "Cover letter": "Thư xin việc",
        "matching": "đối sánh",
        "Matching": "Đối sánh",
        "job ": "vị trí ",
        "Job ": "Vị trí ",
        "apply": "ứng tuyển",
        "Apply": "Ứng tuyển",
        "portfolio": "hồ sơ dự án",
        "Portfolio": "Hồ sơ dự án",
        "case study": "bài phân tích tình huống",
        "Case study": "Bài phân tích tình huống",
    }
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)

    normalized_lines: list[str] = []
    previous_blank = False
    for raw_line in cleaned.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            if normalized_lines and not previous_blank:
                normalized_lines.append("")
            previous_blank = True
            continue

        normalized_lines.append(line)
        previous_blank = False

    return "\n".join(normalized_lines).strip()
