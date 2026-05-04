from pydantic import BaseModel


class CoverLetterRequest(BaseModel):
    ho_so_id: int
    tin_tuyen_dung_id: int
    cv_profile: dict | None = None
    jd_profile: dict | None = None
    matching_profile: dict | None = None


class CareerReportRequest(BaseModel):
    ho_so_id: int
    cv_profile: dict | None = None
    matching_profiles: list[dict] | None = None


class CvBuilderWritingRequest(BaseModel):
    cv_profile: dict | None = None
    section: str = "summary"
    options: dict | None = None
