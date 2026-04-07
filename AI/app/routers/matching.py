from fastapi import APIRouter

from app.schemas.common import BaseAiResponse
from app.schemas.matching import MatchingRequest
from app.services.matcher import match_cv_jd


router = APIRouter()


@router.post("/match/cv-jd", response_model=BaseAiResponse)
def matching_endpoint(payload: MatchingRequest) -> BaseAiResponse:
    return BaseAiResponse(
        **match_cv_jd(
            payload.ho_so_id,
            payload.tin_tuyen_dung_id,
            cv_profile=payload.cv_profile,
            jd_profile=payload.jd_profile,
        )
    )
