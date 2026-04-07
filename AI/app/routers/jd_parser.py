from fastapi import APIRouter

from app.schemas.common import BaseAiResponse
from app.schemas.jd import JdParseRequest
from app.services.jd_parser import parse_jd


router = APIRouter()


@router.post("/parse/jd", response_model=BaseAiResponse)
def parse_jd_endpoint(payload: JdParseRequest) -> BaseAiResponse:
    return BaseAiResponse(**parse_jd(payload.tin_tuyen_dung_id, payload.job_text))
