from fastapi import APIRouter

from app.schemas.common import BaseAiResponse
from app.schemas.generation import CareerReportRequest, CoverLetterRequest, CvBuilderWritingRequest
from app.services.career_report import generate_career_report
from app.services.cover_letter import generate_cover_letter
from app.services.cv_builder_writing import generate_cv_builder_writing


router = APIRouter()


@router.post("/generate/cover-letter", response_model=BaseAiResponse)
def generate_cover_letter_endpoint(payload: CoverLetterRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **generate_cover_letter(
            payload.ho_so_id,
            payload.tin_tuyen_dung_id,
            cv_profile=payload.cv_profile,
            jd_profile=payload.jd_profile,
            matching_profile=payload.matching_profile,
        )
    )


@router.post("/generate/career-report", response_model=BaseAiResponse)
def generate_career_report_endpoint(payload: CareerReportRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **generate_career_report(
            payload.ho_so_id,
            cv_profile=payload.cv_profile,
            matching_profiles=payload.matching_profiles,
        )
    )


@router.post("/generate/cv-builder-writing", response_model=BaseAiResponse)
def generate_cv_builder_writing_endpoint(payload: CvBuilderWritingRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **generate_cv_builder_writing(
            cv_profile=payload.cv_profile,
            section=payload.section,
            options=payload.options,
        )
    )
