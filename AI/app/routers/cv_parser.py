from fastapi import APIRouter

from app.schemas.common import BaseAiResponse
from app.schemas.cv import CvParseRequest
from app.services.cv_parser import parse_cv


router = APIRouter()


@router.post("/parse/cv", response_model=BaseAiResponse)
def parse_cv_endpoint(payload: CvParseRequest) -> BaseAiResponse:
    return BaseAiResponse(**parse_cv(payload.ho_so_id, payload.file_path))
