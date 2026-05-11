from pydantic import BaseModel


class MatchingRequest(BaseModel):
    request_key: str | None = None
    ho_so_id: int
    tin_tuyen_dung_id: int
    cv_profile: dict | None = None
    jd_profile: dict | None = None
    include_llm_explanation: bool = False


class MatchingBatchRequest(BaseModel):
    items: list[MatchingRequest]
