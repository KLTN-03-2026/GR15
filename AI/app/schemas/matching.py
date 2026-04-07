from pydantic import BaseModel


class MatchingRequest(BaseModel):
    ho_so_id: int
    tin_tuyen_dung_id: int
    cv_profile: dict | None = None
    jd_profile: dict | None = None
