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
        content = provider.generate(context).strip()

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
                    "provider": settings.cover_letter_provider,
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
        featured_skills=featured_skills,
        job_focus_skills=job_focus_skills,
        missing_skills=missing_skills,
        experience_summary=kinh_nghiem,
        matching_score=diem_phu_hop,
        matching_explanation=explanation,
    )


def _resolve_provider():
    provider_name = settings.cover_letter_provider.lower().strip()
    if provider_name == "ollama":
        return OllamaCoverLetterProvider()
    if provider_name == "openai":
        return OpenAICoverLetterProvider()
    return TemplateCoverLetterProvider()


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


def _determine_tone(diem_phu_hop: float | None) -> str:
    if diem_phu_hop is None:
        return "neutral"
    if diem_phu_hop >= 80:
        return "strong"
    if diem_phu_hop >= 60:
        return "balanced"
    return "growth"
